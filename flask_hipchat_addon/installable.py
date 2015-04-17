import json
import logging
import requests
from flask import request

from .addon import db, cache
from .tenant import Tenant
from .events import events

_log = logging.getLogger(__name__)


def _invalid_install(msg):
    _log.error("Installation failed: %s" % msg)
    return msg, 400

@cache.cached(timeout=3600, key_prefix='get_capabilities')
def get_capabilities(url):
    return requests.get(url, timeout=10).json()


def init(addon, allow_global, allow_room, send_events=True, require_group_id=False):
    @addon.app.route('/addon/installable', methods=['POST'])
    def on_install():
        data = json.loads(request.data)
        if not data.get('roomId', None) and not allow_global:
            return _invalid_install("This add-on can only be installed in individual rooms.  Please visit the " +
                                    "'Add-ons' link in a room's administration area and install from there.")

        if data.get('roomId', None) and not allow_room:
            return _invalid_install("This add-on cannot be installed in an individual room.  Please visit the " +
                                    "'Add-ons' tab in the 'Group Admin' area and install from there.")

        _log.info("Retrieving capabilities doc at %s" % data['capabilitiesUrl'])

        capdoc = get_capabilities(data['capabilitiesUrl'])
        if capdoc['links'].get('self', None) != data['capabilitiesUrl']:
            return _invalid_install("The capabilities URL %s doesn't match the resource's self link %s" %
                                    (data['capabilitiesUrl'], capdoc['links'].get('self', None)))

        client = Tenant(oauth_id=data['oauthId'],
                        secret=data['oauthSecret'],
                        room_id=data.get('roomId', None),
                        capdoc=capdoc)

        try:
            session = client.get_token(token_only=False,
                                       scopes=addon.descriptor['capabilities']['hipchatApiConsumer']['scopes'])
        except Exception as e:
            _log.warn("Error validating installation by receiving token: %s" % e)
            return _invalid_install("Unable to retrieve token using the new OAuth information")

        _log.info("session: %s" % json.dumps(session))
        if require_group_id and int(require_group_id) != int(session['group_id']):
            _log.error("Attempted to install for group %s when group %s is only allowed" %
                       (session['group_id'], require_group_id))
            return _invalid_install("Only group %s is allowed to install this add-on" % require_group_id)

        client.group_id = session['group_id']
        client.group_name = session['group_name']

        db.session.add(client)
        db.session.commit()
        if send_events:
            events.fire_event('install', {"client": client})

        return '', 204

    @addon.app.route('/addon/installable/<string:oauth_id>', methods=['DELETE'])
    def on_uninstall(oauth_id):
        client = Tenant.query.filter_by(oauth_id=oauth_id).first()
        db.session.delete(client)
        db.session.commit()
        if send_events:
            events.fire_event('uninstall', {"client": client})

        return '', 204

    addon.descriptor['capabilities']['installable']['callbackUrl'] = "{base}/addon/installable".format(
        base=addon.app.config['HIPCHAT_ADDON_BASE_URL']
    )

