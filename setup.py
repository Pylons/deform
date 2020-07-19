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

# Standard Library
import os

from setuptools import find_packages
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, "README.rst")) as f:
        README = f.read()
    with open(os.path.join(here, "CHANGES.txt")) as f:
        CHANGES = f.read()
except Exception:
    README = ""
    CHANGES = ""

requires = [
    "Chameleon>=2.5.1",  # Markup class
    "colander>=1.0a1",  # cstruct_children/appstruct_children, Set
    "iso8601",
    "peppercorn>=0.3",  # rename operation type
    "translationstring>=1.0",  # add format mapping with %
    "zope.deprecation",
]


lint_extras = [
    "black",
    "check-manifest",
    "flake8",
    "flake8-bugbear",
    "flake8-builtins",
    "isort",
    "readme_renderer",
]

testing_extras = ["beautifulsoup4", "coverage", "flaky", "nose"]

# Needed to run deformdemo tests
functional_testing_extras = [
    "selenium>=3",
    "pyramid",
    "pygments",
    "waitress",
    "lingua",
]

docs_extras = [
    "Sphinx >= 1.7.4",
    "repoze.sphinx.autointerface",
    "pylons_sphinx_latesturl",
    "pylons-sphinx-themes",
]

setupkw = dict(
    name="deform",
    version="3.0.0.dev0",
    description="Form library with advanced features like nested forms",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: Repoze Public License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords="web forms form generation schema validation pyramid",
    author="Chris McDonough, Agendaless Consulting",
    author_email="pylons-discuss@googlegroups.com",
    url="https://docs.pylonsproject.org/projects/deform/en/latest/",
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    tests_require=testing_extras,
    install_requires=requires,
    test_suite="deform.tests",
    extras_require={
        "lint": lint_extras,
        "testing": testing_extras,
        "docs": docs_extras,
        "functional": functional_testing_extras,
        "dev": (
            lint_extras
            + testing_extras
            + docs_extras
            + functional_testing_extras
        ),
    },
)

setup(**setupkw)
