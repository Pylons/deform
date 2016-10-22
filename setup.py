##############################################################################
#
# Copyright (c) 2011 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except:
    README = ''
    CHANGES = ''

requires = [
    'Chameleon>=2.5.1',  # Markup class
    'colander>=1.0a1',  # cstruct_children/appstruct_children, Set
    'iso8601',
    'peppercorn>=0.3',  # rename operation type
    'translationstring>=1.0',  # add format mapping with %
    'zope.deprecation',
    ]

testing_extras = [
    'nose',
    'coverage',
    'beautifulsoup4'
    ]

# Needed to run deformdemo tests
functional_testing_extra = [
    'selenium<3',
    'pyramid',
    'pygments',
    'waitress',
    'lingua'
]

docs_extras = [
    'Sphinx >= 1.3.4',
    'repoze.sphinx.autointerface',
    'pylons_sphinx_latesturl',
    'pylons-sphinx-themes',
    ]

setupkw = dict(
    name='deform',
    version='2.0b1',
    description='Form library with advanced features like nested forms',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        ],
    keywords='web forms form generation schema validation pyramid',
    author="Chris McDonough, Agendaless Consulting",
    author_email="pylons-discuss@googlegroups.com",
    url="http://docs.pylonsproject.org/projects/deform/en/latest/",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=testing_extras,
    install_requires=requires,
    test_suite="deform.tests",
    extras_require={
        'testing': testing_extras,
        'docs': docs_extras,
        'functional': functional_testing_extra,
        },
    )

setup(**setupkw)
