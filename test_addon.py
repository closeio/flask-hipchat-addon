import logging
import json

from flask import Flask, request
from flask_hipchat_addon.addon import Addon


app = Flask(__name__)
app.config.from_object('settings')
addon = Addon(app=app, allow_room=True, allow_global=True, scopes=['send_notification'])


@addon.webhook(event='room_message', pattern='.*')
def room_message():
    data = json.loads(request.data)
    logging.debug('%s: %s', data['item']['message']['from']['name'], data['item']['message']['message'])
    return '', 204


@addon.configure_page()
def configure_page():
    return 'plugin configuration', 200

if __name__ == '__main__':
    addon.run(debug=True)