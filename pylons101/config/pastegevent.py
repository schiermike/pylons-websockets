"""Entry point for PasteDeploy."""

from gevent import reinit
from gevent.pywsgi import WSGIServer
from gevent.monkey import patch_all
from geventwebsocket.handler import WebSocketHandler

__all__ = ["server_factory_patched"]

def server_factory_patched(global_conf, host, port):
    port = int(port)
    def serve(app):
        reinit()
        patch_all(dns=False)
        WSGIServer((host, port), app, handler_class=WebSocketHandler).serve_forever()
    return serve