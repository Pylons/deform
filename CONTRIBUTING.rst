============
Contributing
============

All projects under the Pylons Projects, including this one, follow the
guidelines established at [How to
Contribute](http://www.pylonsproject.org/community/how-to-contribute) and
[Coding Style and
Standards](http://docs.pylonsproject.org/en/latest/community/codestyle.html).

You can contribute to this project in several ways.

* [File an Issue on GitHub](https://github.com/Pylons/pyramid/issues)
* Fork this project and create a branch with your suggested change. When ready,
  submit a pull request for consideration. [GitHub
  Flow](https://guides.github.com/introduction/flow/index.html) describes the
  workflow process and why it's a good practice. When submitting a pull
  request, sign
  [CONTRIBUTORS.txt](https://github.com/Pylons/deform/blob/master/CONTRIBUTORS.txt)
  if you have not yet done so.
* Join the IRC channel #pyramid on irc.freenode.net.


Discuss proposed changes first
------------------------------

To propose a change, open an issue on Github for discussion, preferably before
starting any coding. Ask the authors' opinion how the issue should be
approached, as this will make it easier to merge the pull request later.


Unit tests
----------

All features must be covered by unit tests, so that test coverage stays at
100%.

To run tests::

    pip install tox  # System wide installation
    tox

This will run tests for Python 2.x, Python 3.x, PyPy, functional, coverage,
and documentation.


Functional tests
----------------

All features must be covered by functional tests and have example use.

.. warning::

    Fun fact: Functional tests behave differently depending on if you are looking the browser window or not.

Preparing compatible browser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functional tests run on Firefox 45 and Selenium 2.56. Below are instructions
for OSX:

* `Download Firefox 45 ESR
  <https://ftp.mozilla.org/pub/firefox/releases/45.0.2esr/>`_ (`OSX
  <https://ftp.mozilla.org/pub/firefox/releases/45.0.2esr/mac/en-US/>`_)

* Rename ``Firefox.app`` to ``Firefox-45.app``

* Copy ``Firefox-45.app`` to ``Applications``

* Prepare your test run::

    export FIREFOX_PATH=/Applications/Firefox-45.app/Contents/MacOS/firefox

.. note ::

    Selenium 3: As the writing of this Marionette geckodriver for Firefox is incomplete and cannot
    run all the tests.

.. note ::

    Chrome: Tests do not run correctly on Chrome due to various timing issues. Some effort was put forth to fix this, but it's never ending swamp.

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

All features must be documented with code samples in narrative documentation,
API documentation, and deformdemo.


Changelog
---------

Update ``CHANGES.txt``.

Update ``CONTRIBUTORS.rst``.


Pull requests
-------------

Make a pull request on GitHub for deform or deformdemo.
