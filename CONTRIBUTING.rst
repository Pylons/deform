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

All features must be covered by functional tests and have example use.

Preparing compatible browser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functional tests run on Firefox 43 and Selenium 2.56. Below are instructions for OSX:

* `Download Firefox 45 ESR <https://ftp.mozilla.org/pub/firefox/releases/45.0.2esr/>`_ (`OSX <https://ftp.mozilla.org/pub/firefox/releases/45.0.2esr/mac/en-US/>`_)

* Rename ``Firefox.app`` to ``Firefox-45.app``

* Copy ``Firefox-45.app`` to ``Applications``

* Prepare your test run ``export FIREFOX_PATH=/Applications/Firefox-45.app/Contents/MacOS/firefox``


Running test suite
~~~~~~~~~~~~~~~~~~

To run functional tests::

    tox -e functional

Stop on error::

    tox -e functional -- -x

Rerun single test::

    tox -e functional -- deformdemo.test:CheckedInputWidgetWithMaskTests

To run/edit/fix functional tests::

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


