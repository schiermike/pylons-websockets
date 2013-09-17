from setuptools import setup, find_packages


setup(
    name='pylons101',
    install_requires=[
        "Pylons>=1.0.1rc1",
        "SQLAlchemy>=0.5",
        'gevent-websocket>=0.3.6',
        'redis>=2.8'
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'pylons101': ['i18n/*/LC_MESSAGES/*.mo']},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = pylons101.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [paste.server_factory]
    gevent_patched = pylons101.config.pastegevent:server_factory_patched
    """
)
