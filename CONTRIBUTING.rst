============
Contributing
============

All projects under the Pylons Projects, including this one, follow the
guidelines established at [How to
Contribute](https://pylonsproject.org/community-how-to-contribute.html) and
[Coding Style and
Standards](https://pylonsproject.org/community-coding-style-standards.html).

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

All features must be covered by functional tests and have example use. We use the following for running functional tests:

* Firefox 45 ESR (see :ref:`preparing-compatible-browser`)
* `gettext <https://www.gnu.org/software/gettext/>`_
* `tox <https://tox.readthedocs.io/en/latest/>`_
* `deformdemo <https://github.com/pylons/deformdemo>`_

If you add or change a feature that reduces test coverage or causes a functional test to fail, then you also must submit a pull request to the `deformdemo <https://github.com/pylons/deformdemo>`_ repository to go along with your functional test change to deform.

.. warning::

    Fun fact: Functional tests behave differently depending on if you are looking at the browser window or not.


.. _preparing-compatible-browser:

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

.. note::

    Selenium 3: As of this writing, the Marionette geckodriver for Firefox is incomplete and cannot
    run all the tests.

.. note::

    Chrome: Tests do not run correctly on Chrome due to various timing issues. Some effort was put forth to fix this, but it's a never ending swamp.


Install gettext
~~~~~~~~~~~~~~~

The functional tests require the installation of the GNU ``gettext`` utilities, specifically ``msgmerge`` and ``msgfmt``.  Use your package manager to install these requirements.  On macOS using `Homebrew <https://brew.sh/>`_:

.. code-block::

    brew install gettext
    brew link gettext --force

If you ever have problems building packages, you can always unlink it.

.. code-block::

    brew unlink gettext


Running test suite
~~~~~~~~~~~~~~~~~~

Tox is used to run all tests.  For functional tests, tox run the shell script `run-selenium-tests.bash <https://github.com/Pylons/deform/blob/master/run-selenium-tests.bash>`_, located at the root of the deform repository.  See its comments for a description.

`Install tox <https://tox.readthedocs.io/en/latest/install.html>`_.

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
