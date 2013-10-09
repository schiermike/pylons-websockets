from hashlib import sha1
from ws4py import WS_VERSION, WS_KEY
from ws4py.compat import py3k
import base64
from geventwebsocket.gunicorn.workers import GeventWebSocketWorker
from gunicorn.workers.ggevent import GeventPyWSGIWorker
import gevent.pywsgi
from ws4py.server.geventserver import WSGIServer, WebSocketWSGIHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from ws4py.websocket import WebSocket
from ws4py.exc import HandshakeError


########################################################################################################################
def log_request(self):
    log = self.server.log
    if log:
        if hasattr(log, 'write'):
            log.write(self.format_request())
        else:
            log.info(self.format_request())


gevent.pywsgi.WSGIHandler.log_request = log_request
########################################################################################################################


class MyWebSocket(WebSocket):

    def opened(self):
        print 'openend'

    def closed(self, code, reason=None):
        print 'closed: %s %s' % (code, reason)

    def received_message(self, message):
        print 'received: %s' % message

    def ponged(self, pong):
        print 'ponged: %s' % pong



class MyWebSocketWSGIHandler(gevent.pywsgi.WSGIHandler):
    """
    A WSGI handler that will perform the :rfc:`6455`
    upgrade and handshake before calling the WSGI application.

    If the incoming request doesn't have a `'Upgrade'` header,
    the handler will simply fallback to the gevent builtin's handler
    and process it as per usual.
    """

    def run_application(self):
        upgrade_header = self.environ.get('HTTP_UPGRADE', '').lower()
        if upgrade_header:
            try:
                # Build and start the HTTP response
                self.environ['ws4py.socket'] = self.socket or self.environ['wsgi.input'].rfile._sock
                self.environ['ws4py.websocket'] = self.handshake_reply(self.environ, self.start_response, MyWebSocket)
                self.result = self.application(self.environ, self.start_response) or []
                #self.process_result()
            except:
                raise
            else:
                del self.environ['ws4py.socket']
                self.socket = None
                self.rfile.close()

                ws = self.environ.pop('ws4py.websocket')
                if ws:
                    self.server.pool.track(ws)
        else:
            gevent.pywsgi.WSGIHandler.run_application(self)

    def handshake_reply(self, environ, start_response, websock_class):
        if environ.get('REQUEST_METHOD') != 'GET':
            raise HandshakeError('HTTP method must be a GET')

        for key, expected_value in [('HTTP_UPGRADE', 'websocket'),
                                    ('HTTP_CONNECTION', 'upgrade')]:
            actual_value = environ.get(key, '').lower()
            if not actual_value:
                raise HandshakeError('Header %s is not defined' % key)
            if expected_value not in actual_value:
                raise HandshakeError('Illegal value for header %s: %s' %
                                     (key, actual_value))

        key = environ.get('HTTP_SEC_WEBSOCKET_KEY')
        if key:
            ws_key = base64.b64decode(key.encode('utf-8'))
            if len(ws_key) != 16:
                raise HandshakeError("WebSocket key's length is invalid")

        version = environ.get('HTTP_SEC_WEBSOCKET_VERSION')
        supported_versions = b', '.join([unicode(v).encode('utf-8') for v in WS_VERSION])
        version_is_valid = False
        if version:
            try:
                version = int(version)
            except:
                pass
            else:
                version_is_valid = version in WS_VERSION

        if not version_is_valid:
            environ['websocket.version'] = unicode(version).encode('utf-8')
            raise HandshakeError('Unhandled or missing WebSocket version')

        ws_protocols = []
        protocols = []
        subprotocols = environ.get('HTTP_SEC_WEBSOCKET_PROTOCOL')
        if subprotocols:
            for s in subprotocols.split(','):
                s = s.strip()
                if s in protocols:
                    ws_protocols.append(s)

        ws_extensions = []
        exts = []
        extensions = environ.get('HTTP_SEC_WEBSOCKET_EXTENSIONS')
        if extensions:
            for ext in extensions.split(','):
                ext = ext.strip()
                if ext in exts:
                    ws_extensions.append(ext)

        accept_value = base64.b64encode(sha1(key.encode('utf-8') + WS_KEY).digest())
        if py3k:
            accept_value = accept_value.decode('utf-8')
        upgrade_headers = [
            ('Upgrade', 'websocket'),
            ('Connection', 'Upgrade'),
            ('Sec-WebSocket-Version', '%s' % version),
            ('Sec-WebSocket-Accept', accept_value),
        ]
        if ws_protocols:
            upgrade_headers.append(('Sec-WebSocket-Protocol', ', '.join(ws_protocols)))
        if ws_extensions:
            upgrade_headers.append(('Sec-WebSocket-Extensions', ','.join(ws_extensions)))

        write_func = start_response("101 Switching Protocols", upgrade_headers)
        write_func('')  # flush the handshake data

        return websock_class(sock=environ['ws4py.socket'], environ=environ)


class MyWorker(GeventPyWSGIWorker):
    server_class = WSGIServer
    wsgi_handler = MyWebSocketWSGIHandler