#!/usr/bin/env python

import os
import sys

from setuptools import setup

__author__ = 'Andrew Matteson'
__version__ = '0.1.0'

packages = [
    'twinfo',
    'twinfo.plotting'
    ]

setup(
    name='twinfo',
    version=__version__,
    install_requires=['twython==3.0.0'],
    author='Andrew Matteson',
    author_email='drew.matteson@gmail.com',
    url='https://github.com/matteson/twinfo/tree/master',
    keywords='twitter pointwise mutual information',
    packages=packages
) 
