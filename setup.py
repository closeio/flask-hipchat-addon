"""
Flask-HipChat-Addon
-------------

A library to help write a Flask-based HipChat add-on
"""
from setuptools import setup


setup(
    name='Flask-HipChat-Addon',
    version='0.1',
    url='https://github.com/congocongo/flask-hipchat-addon',
    license='APLv2',
    long_description=__doc__,
    packages=['flask_hipchat_addon'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Cache',
        'requests',
        'PyJWT'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
