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

This will run tests for Python 2.x, Python 3.x, PyPy, functional3, coverage,
and documentation.


Functional tests
----------------

All features must be covered by functional3 tests and have example use. We use the following for running functional3 tests:

* Firefox 
* `gettext <https://www.gnu.org/software/gettext/>`_
* `tox <https://tox.readthedocs.io/en/latest/>`_
* `deformdemo <https://github.com/pylons/deformdemo>`_

If you add or change a feature that reduces test coverage or causes a functional3 test to fail, then you also must submit a pull request to the `deformdemo <https://github.com/pylons/deformdemo>`_ repository to go along with your functional3 test change to deform.

.. warning::

    Fun fact: Functional tests behave differently depending on if you are looking at the browser window or using Xvfb which is a X virtual framebuffer to run graphics in memory and in server instead of forwarding the display to desktop using X11 forwarding and Xwindows.


Preparing Selenium And Firefox on Linux(Debian)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functional tests run on Firefox and Selenium:

* `Download latest version of Firefox:   
    https://ftp.mozilla.org/pub/firefox/releases/  

    In our case it would be:   
    wget https://ftp.mozilla.org/pub/firefox/releases/75.0/linux-x86_64/en-US/firefox-75.0.tar.bz2   
    tar -xjf firefox-75.0.tar.bz2   
 
    export PATH=/Full_Path_To_Extracted_Directory/:$PATH   
    export FIREFOX_PATH=/Full_Path_To_Extracted_Directory/firefox    


    Download the lastes version geckodriver:   
    https://github.com/mozilla/geckodriver/releases    

    In our case it would be:   
    mkdir ~/geckodriver   
    cd ~/geckodriver   
    wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz   
    tar -xzf geckodriver-v0.26.0-linux64.tar.gz    

    export PATH=/Full_Path_To_Extracted_Directory/:$PATH    
    export WEBDRIVER=/Full_Path_To_Extracted_Directory/geckodriver   

    Note:  
        To use google-chrome or Chromium, you would have to download the browser and respected webdriver   
        which in this case would be chromiumdriver:   
        https://chromedriver.chromium.org/downloads   
        Then set the WEBDRIVER environment variable to point to new webdriver:   
        


    Install latest version of Selenium Python bindings:   
    pip install selenium    

    Note:   
        You don't need the Selenium stand alone server, unless your tests are distributed accross multiple servers.   


    Install Xvfb:   
    apt-get install xvfb   
    
    Set display and start Xvfb in back ground:   
    export DISPLAY=:99   
    Xvfb :99 &    
    
    At this point a single test can be run to verify environment has set properly:   
    tox -e functional3 -- deformdemo.test:CheckboxChoiceReadonlyTests    

    Note:  
        port is set to 8522 in demo.ini, in case this port is blocked by server firewall   
        port can be changed:   
        vi deformdemo_functional_tests/demo.ini   
        port = NEW_PORT   
        
        export URL = SERVER_FQDN:NEW_PORT    

`


Install gettext
~~~~~~~~~~~~~~~

The functional3 tests require the installation of the GNU ``gettext`` utilities, specifically ``msgmerge`` and ``msgfmt``.  Use your package manager to install these requirements.  On Debian_:

.. code-block::

    apt-get install gettext
    apt-get install gettext-base

Running test suite
~~~~~~~~~~~~~~~~~~

Tox is used to run all tests.  For functional3 tests, tox run the shell script `run-selenium-tests.bash <https://github.com/Pylons/deform/blob/master/run-selenium-tests.bash>`_, located at the root of the deform repository.  See its comments for a description.

`Install tox <https://tox.readthedocs.io/en/latest/install.html>`_.

To run functional3 tests::

    tox -e functional3

Stop on error::

    tox -e functional3 -- -x

Rerun single test::

    tox -e functional3 -- deformdemo.test:CheckedInputWidgetWithMaskTests

To run/edit/fix functional3 tests::

    source .tox/functional3/bin/activate
    cd deformdefom  # Checked out by tox functional3
    pserve demo.ini  # Start web server

    # Run functional3 test suite using Chrome
    WEBDRIVER="chrome" nosetests -x

    # Run functional3 test suite using Chrome, stop on pdb on exception
    WEBDRIVER="chrome" nosetests -x --pdb

    # Run one functional3 test case using Chrome
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
