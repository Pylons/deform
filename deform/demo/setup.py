##############################################################################
#
# Copyright (c) 2010 Agendaless Consulting and Contributors.
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
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'deform',
    'repoze.bfg',
    'pygments',
    'translationstring',
    'Babel'
    ]

setupkw = dict(
    name='deformsite',
    version='0.0',
    description='Demonstrate deform form generation system',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Framework :: BFG",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    keywords='web wsgi deform form generation',
    author="Agendaless Consulting",
    author_email="repoze-dev@lists.repoze.org",
    url="http://www.repoze.org",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require = requires,
    install_requires = requires,
    test_suite="deformsite",
    entry_points = """\
    [paste.app_factory]
    app = deformsite.app:run
    """,
    )

try:
    import babel
    babel = babel # PyFlakes
    # if babel is installed, advertise message extractors (if we pass
    # this to setup() unconditionally, and babel isn't installed,
    # distutils warns pointlessly)
    setupkw['message_extractors'] = { ".": [
        ("**.py",   "chameleon_python", None ),
        ("**.pt",   "chameleon_xml", None ),
        ]}
except ImportError:
    pass

setup(**setupkw)

