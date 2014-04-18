# -*- coding: utf-8 -*-

from setuptools import setup
import mongu

setup(name='mongu',
      version=mongu.__version__,
      description='Yet another Python Object-Document Mapper on top of ``PyMongo``.',
      long_description=mongu.__doc__,
      author=mongu.__author__,
      author_email='mail2tevin@gmail.com',
      url='http://github.com/tevino/mongu',
      py_modules=['mongu'],
      scripts=['mongu.py'],
      install_requires=['pymongo>=2.7'],
      license=mongu.__license__,
      platforms='any')
