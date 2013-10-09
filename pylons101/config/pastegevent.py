"""Entry point for PasteDeploy."""

import socket
from gevent import reinit
from gevent.monkey import patch_all
from ws4py.server.geventserver import WebSocketWSGIHandler, WSGIServer

__all__ = ["server_factory_patched"]


def server_factory_patched(global_conf, host=None, port=None):
    port = int(port)
    patch_all(dns=False)

    def serve(app):
        listener = (host, port)
#        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        listener.bind((host, port))
#        listener.listen(port)

        reinit()
        WSGIServer(listener, app, handler_class=WebSocketWSGIHandler).serve_forever()
    return serve