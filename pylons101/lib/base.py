from pylons.controllers import WSGIController
from pylons101.model.meta import Session


class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        try:
            return WSGIController.__call__(self, environ, start_response)
        finally:
            Session.remove()
