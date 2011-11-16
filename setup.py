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
import sys

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    README = ''
    CHANGES = ''

requires = [
    'Chameleon>=1.2.3', # debug arg
    'colander>=0.8', # Bindings-providing
    'peppercorn>=0.3', # rename operation type
    'translationstring',
    'lingua', # if chameleon >= 2, for i18n message extraction
    ]

if sys.version_info <(2,6,0):
    requires.append('simplejson')

setupkw = dict(
    name='deform',
    version='0.9.3',
    description='Another form generation library',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    keywords='web forms form generation schema validation',
    author="Chris McDonough, Agendaless Consulting",
    author_email="pylons-discuss@googlegroups.com",
    url="http://pylonsproject.org",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=requires + ['BeautifulSoup'],
    install_requires=requires,
    test_suite="deform",
    )

try:
    import babel
    babel = babel # PyFlakes
    # if babel is installed, advertise message extractors (if we pass
    # this to setup() unconditionally, and babel isn't installed,
    # distutils warns pointlessly)
    setupkw['message_extractors'] = { ".": [
        #("deform/**.py",     "chameleon_python", None ), #chameleon < 2
        #("deform/**.pt",     "chameleon_xml", None ),    #chameleon < 2
        ("deform/**.py",     "lingua_python", None ),     #chameleon >= 2
        ("deform/**.pt",     "lingua_xml", None ),        #chameleon >= 2
        ]}
except ImportError:
    pass

setup(**setupkw)
