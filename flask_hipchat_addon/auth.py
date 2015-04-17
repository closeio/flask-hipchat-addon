from flask import _request_ctx_stack as stack, request, abort

from werkzeug.local import LocalProxy
from functools import wraps
import jwt

from tenant import Tenant


def require_tenant(func):

    @wraps(func)
    def inner(*args, **kwargs):
        assert tenant
        return func(*args, **kwargs)

    return inner


def _validate_jwt(req):
    print req.args
    jwt_data = req.args.get('signed_request', None)
    if not jwt_data:
        abort(401)

    oauth_id = jwt.decode(jwt_data, verify=False)['iss']
    print oauth_id
    client = Tenant.query.filter_by(oauth_id=oauth_id).first()
    data = jwt.decode(jwt_data, client.secret)
    return client, data['prn']


def _get_tenant():
    ctx = stack.top
    if ctx is not None:
        if not hasattr(ctx, 'tenant'):
            if request.args.get('signed_request', None):
                cur_tenant, prn = _validate_jwt(request)
                ctx.sender = User(prn)
            elif request.json and 'oauth_client_id' in request.json:
                body = request.json
                oauth_id = body['oauth_client_id']
                cur_tenant = Tenant.query.filter_by(oauth_id=oauth_id).first()
                if 'item' in body and 'sender' in body['item']:
                    user = User(user_id=body['item']['sender']['id'],
                                name=body['item']['sender']['name'],
                                mention_name=body['item']['sender']['mention_name'])
                    ctx.sender = user

            else:
                cur_tenant = None
            ctx.tenant = cur_tenant
        return ctx.tenant


def _get_sender():
    _get_tenant()
    if hasattr(stack.top, 'sender'):
        return stack.top.sender
    else:
        return None


tenant = LocalProxy(_get_tenant)
sender = LocalProxy(_get_sender)


class User(object):
    def __init__(self, user_id, name=None, mention_name=None):
        self.id = user_id
        self.name = name
        self.mention_name = mention_name