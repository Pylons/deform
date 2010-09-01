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

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'deform',
    'repoze.bfg',
    'Pygments',
    'PasteScript',
    ]

## TODO: read version from ../setup.py

setupkw = dict(
    name='deformdemo',
    version='0.5',
    description='Another form generation library',
    long_description='',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    keywords='web forms form generation schema validation demo',
    author="Agendaless Consulting",
    author_email="repoze-dev@lists.repoze.org",
    url="http://www.repoze.org",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    package_dir = {'': '.'},
    include_package_data=True,
    zip_safe=False,
    tests_require=requires,
    install_requires=requires,
    entry_points = """\
    [paste.app_factory]
    demo = deformdemo.app:run
    """
    )


setup(**setupkw)
