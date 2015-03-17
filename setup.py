# -*- coding: utf-8 -*-
"""
**Mongu** is yet another Python Object-Document Mapper on top of ``PyMongo``. It's lightweight, intuitive to use and easy to understand.

If those **heavy and slow layers** have nothing or more than you need, Mongu maybe the one for you.

You are the only one who knows what you reall need.

Therefor **Mongu does nothing but a skeleton for you to fill**.

Actually, if you have ever tried to write your own ODM, you may already implemented parts of **Mongu** :D

Copyright (c) 2014, Tevin Zhang.
License: MIT (see LICENSE for details)
"""

__author__ = 'Tevin Zhang'
__version__ = '0.4.4'
__license__ = 'MIT'

from setuptools import setup

setup(name='mongu',
      version=__version__,
      description='Yet another Python Object-Document Mapper on top of PyMongo.',
      long_description=__doc__,
      author=__author__,
      author_email='mail2tevin@gmail.com',
      url='http://github.com/tevino/mongu',
      py_modules=['mongu'],
      scripts=['mongu.py'],
      install_requires=['pymongo>=2.7'],
      license=__license__,
      platforms='any',
      test_suite='tests.suite')
