import json
from .auth import tenant
import requests


class RoomClient(object):

    def __init__(self, room_id=None):

        self.room_id = room_id
        self.token = tenant.get_token()
        self.base_url = tenant.capabilities_url[0:tenant.capabilities_url.rfind('/')]

    def send_notification(self, message):

        resp = requests.post("%s/room/%s/notification?auth_token=%s" % (self.base_url, self.room_id, self.token),
                             headers={'content-type': 'application/json'},
                             data=json.dumps({"message": message}), timeout=10)
        # todo: do better
        assert resp.status_code == 204
