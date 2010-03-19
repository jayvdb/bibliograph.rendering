# -*- coding: utf-8 -*-
"""
This module contains the tool of bibliograph.rendering
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0.0' 

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('bibliograph', 'rendering', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

entry_points="""
# -*- Entry points: -*-
"""

setup(name='bibliograph.rendering',
      version=version,
      description="Bibliographic renderers",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='bibtex bibliography',
      author='Tom Gross',
      author_email='itconsense@gmail.com',
      url='http://pypi.python.org/pypi/bibliograph.rendering',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bibliograph'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'bibliograph.core'
                        ],
      tests_require=['zope.testing'],
      entry_points=entry_points,
      )
