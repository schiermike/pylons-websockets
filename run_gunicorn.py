from paste.deploy import loadapp
from gunicorn.app.pasterapp import paste_server
from pylons101.config.server import MyWorker


if __name__ == '__main__':
    app = loadapp('config:development.ini', relative_to='.')
    paste_server(app, host='0.0.0.0', port=5000, workers=1, worker_class=MyWorker, timeout=0)