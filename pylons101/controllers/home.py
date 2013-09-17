import socket
import simplejson
import time
import redis
from pylons import request
from pylons.templating import render_mako
from pylons101.lib.base import BaseController


class HomeController(BaseController):

    def home(self):
        return render_mako('websocket.mako')

    def ws(self):
        # open websocket
        websock = request.environ['wsgi.websocket']
        websock_version = request.environ['wsgi.websocket_version']
        sec_websocket_extensions = request.environ.get('HTTP_SEC_WEBSOCKET_EXTENSIONS')
        sec_websocket_key = request.environ.get('HTTP_SEC_WEBSOCKET_KEY')
        sec_websocket_version = request.environ.get('HTTP_SEC_WEBSOCKET_VERSION')
        endpoint = websock.socket.getpeername()
        print 'connection established with endpoint %s:%s, version %s / %s, key %s, extensions %s' \
              % (endpoint[0], endpoint[1], websock_version, sec_websocket_version, sec_websocket_key, sec_websocket_extensions)

        websock.send('Hello dear Browser! I\'ll send you redis stuff when I get some')

        # send_redis_stuff(websock)
        send_stuff_in_intervals(websock)

        print 'connection closed to %s:%s' % endpoint


def send_stuff_in_intervals(websock):
    while True:
        time.sleep(5)
        msg = 'time: %s' % time.time()
        try:
            websock.send(msg)
            print 'Sent %s' % msg
        except socket.error, e:
            if e.errno != 32:  # broken pipe - client closed connection
                print e  # put that in the error log
            break


def send_redis_stuff(websock):
    # listen for new messages on redis queue
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_ps = redis_client.pubsub()
    redis_ps.subscribe(['test_channel'])

    for item in redis_ps.listen():
        try:
            websock.send(simplejson.dumps(item))
            print 'Sent %s' % item
        except socket.error, e:
            if e.errno != 32:  # broken pipe - client closed connection
                print e  # put that in the error log
            break