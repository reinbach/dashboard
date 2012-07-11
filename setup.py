#!/usr/bin/env python
from setuptools import setup

requires = [
    'gevent==0.13.7',
    'gevent-socketio==0.3.5-beta',
    'Flask==0.8',
    'pyzmq==2.2.0',
]

setup(
    name='Mini Triage',
    version='1.0',
    description='A prototype app that allows user(s) to triage events into various categories.',
    author='Greg Reinbach',
    author_email='greg@reinbach.com',
    url='https://github.com/reinbach/mini-triage',
    install_requires=requires,
)