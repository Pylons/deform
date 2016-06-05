============
Contributing
============

.. contents:: :local:

Discuss first
-------------

For changes open an issue p on Github for discussion preferably before starting any coding. Ask the authors opinion how the issue should be approached as this will make it easier to merge the pull request later.

Unit tests
----------

All features must be covered by unit tests, so that test coverage stays in 100%.

To run tests::

    pip install tox  # System wide installation
    tox

This will run tests for Python 2.x, Python 3.x, PyPy, functional, coverage, documentation.

Functional tests
----------------

All features must be covered by functional tests and have example use. To run functional tests only::

    tox -e functional

.. to edit functional tests::

    source .tox/functional/bin/activate
    cd deformdefom  # Checked out by tox functional
    pserve demo.ini  # Start web server

    # Run functional test suite using Chrome
    WEBDRIVER="chrome" nosetests -x

    # Run functional test suite using Chrome, stop on pdb on exception
    WEBDRIVER="chrome" nosetests -x --pdb

    # Run one functional test case using Chrome
    WEBDRIVER="chrome" nosetests -x deformdemo.test:SequenceOfDateInputs

Documentation
-------------

All features must be documented with code samples in narrative documentation, API documentation or deformdeom.

Changelog
---------

Update ``CHANGES.txt``.

Update ``CONTRIBUTORS.rst``.

Pull requests
-------------

Make pull request on github for deform, deformdemo.


