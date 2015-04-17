# flask-hipchat-addon
A Python Flask-based library for building HipChat Connect add-ons.

## What is this?
A Python [Flask](http://flask.pocoo.org/)-based library for building [HipChat Connect add-ons](https://www.hipchat.com/docs/apiv2/addons). 
Forked from `ac-flask-hipchat` with added Flask-SQLAlchemy as storage backend.

## Getting started
...


## A first add-on

Writing basic HipChat add-ons with `flask-hipchat-addon` requires very little code to get up and running.  Here's an 
example of a simple yet complete add-on, in two files:

### web.py

```
from flask_hipchat_addon import Addon, room_client, sender
from flask import Flask 

addon = Addon(app=Flask(__name__),
              key="ac-flask-hipchat-greeter",
              name="HipChat Greeter Example Add-o",
              allow_room=True,
              scopes=['send_notification'])

@addon.webhook(event="room_enter")
def room_entered():
    room_client.send_notification('hi: %s' % sender.name)
    return '', 204


if __name__ == '__main__':
    addon.run()
```

### requirements.txt

```
Flask-HipChat-Addon
```

## Preparing the add-on for installation

Now that you have a server running, you'll want to try it somehow.  The next step is different depending on whether  
you're going to be developing with hipchat.com or a private HipChat instance being hosted behind your corporate firewall.

### Developing with HipChat.com

The easiest way to test with hipchat.com while developing on your local machine is to use [ngrok](https://ngrok.com).
Download and install it now if you need to -- it's an amazing tool that will change the way you develop and share web applications.

Start the ngrok tunnel in another terminal window or if using the [Vagrant starter project](https://bitbucket.org/atlassianlabs/ac-flask-hipchat-vagrant),
you should already have ngrok running, and the URL should be printed to the screen when starting the VM.  For the 
purposes of this tutorial, we'll assume your domain is `https://asdf123.ngrok.com`.

While ngrok will forward both HTTP and HTTPS, for the protection of you and your HipChat group members, you should 
always use HTTPS when running your add-on on the public internet.

### Developing with a private server

To install your add-on on a private HipChat server, both the add-on server and HipChat server need to be able to connect 
to each other via HTTP or HTTPS on your local network.  Simply determine an HTTP url that your HipChat server can use to 
connect to your locally running add-on, and use that as the value of your "local base url" needed by the Installation step.

If all goes well, you won't have to change anything from the defaults, as `flask-hipchat-addon` will simply attempt to 
use the OS's hostname to build the local base url, which may already be good enough for your private network.

