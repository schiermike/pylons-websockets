from routes import Mapper


def make_map(config):
    map = Mapper(directory=config['pylons.paths']['controllers'], always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    map.connect('/', controller='home', action='home')
    map.connect('/ws', controller='home', action='ws')

    return map
