from __future__ import print_function

import os
import logging
import httplib


from flask import jsonify
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

import installable
from .auth import require_tenant
from .tenant import Tenant


def _not_none(app, name, default):
    val = app.config.get(name, default)
    if val is not None:
        return val
    else:
        raise ValueError("Missing '{key}' configuration property".format(key=name))


class Addon(object):

    def __init__(self, app, key=None, name=None, description=None, config=None,
                 allow_room=True, allow_global=False, scopes=None, vendor_name=None, vendor_url=None):
        if scopes is None:
            scopes = ['send_notification']

        self.app = app
        self._init_app(app, config)
        db.init_app(app)
        db.create_all(app=app)

        self.descriptor = {
            "key": _not_none(app, 'HIPCHAT_ADDON_KEY', key),
            "name": _not_none(app, 'HIPCHAT_ADDON_NAME', name),
            "description": app.config.get('HIPCHAT_ADDON_DESCRIPTION', description) or "",
            "links": {
                "self": "{base}/addon/descriptor".format(base=app.config['HIPCHAT_ADDON_BASE_URL'])
            },
            "capabilities": {
                "installable": {
                    "allowRoom": allow_room,
                    "allowGlobal": allow_global
                },
                "hipchatApiConsumer": {
                    "scopes": scopes
                }
            },
            "vendor": {
                "url": app.config.get('HIPCHAT_ADDON_VENDOR_URL', vendor_url) or "",
                "name": app.config.get('HIPCHAT_ADDON_VENDOR_NAME', vendor_name) or ""
            }
        }

        installable.init(addon=self, allow_global=allow_global, allow_room=allow_room)

        @self.app.route("/addon/descriptor")
        def descriptor():
            return jsonify(self.descriptor)

        self.app.route("/")(descriptor)

    @staticmethod
    def _init_app(app, config):

        app.config.from_object('flask_hipchat_addon.default_settings')
        if config is not None:
            app.config.from_object(config)

        if app.config['DEBUG']:
            # These two lines enable debugging at httplib level (requests->urllib3->httplib)
            # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
            # The only thing missing will be the response.body which is not logged.
            httplib.HTTPConnection.debuglevel = 1

            # You must initialize logging, otherwise you'll not see debug output.
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        else:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.WARN)

        app.events = {}

    def configure_page(self, path="/configure", **kwargs):
        self.descriptor['capabilities'].setdefault('configurable', {})['url'] = \
            self.app.config['HIPCHAT_ADDON_BASE_URL'] + path

        def inner(func):
            return self.app.route(rule=path, **kwargs)(require_tenant(func))

        return inner

    def webhook(self, event, name=None, pattern=None, path=None, **kwargs):
        if path is None:
            path = "/event/" + event

        wh = {
            "event": event,
            "url": self.app.config['HIPCHAT_ADDON_BASE_URL'] + path
        }
        if name is not None:
            wh['name'] = name

        if pattern is not None:
            wh['pattern'] = pattern
        self.descriptor['capabilities'].setdefault('webhook', []).append(wh)

        def inner(func):
            return self.app.route(rule=path, methods=['POST'], **kwargs)(require_tenant(func))

        return inner

    def route(self, anonymous=False, *args, **kwargs):
        """
        Decorator for routes with defaulted required authenticated tenants
        """
        def inner(func):
            f = self.app.route(*args, **kwargs)(func)
            if not anonymous:
                f = require_tenant(f)
            return f

        return inner

    def run(self, *args, **kwargs):
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            print("")
            print("--------------------------------------")
            print("Public descriptor base URL: %s" % self.app.config['HIPCHAT_ADDON_BASE_URL'])
            print("--------------------------------------")
            print("")
            #for k, v in self.app.config.items():
            #    print(k, '=', v)

        self.app.run(*args, **kwargs)
