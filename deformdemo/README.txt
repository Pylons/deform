deformdemo
==========

Software which demonstrates the operation of the ``deform`` form
generation package.

Running the Demo
----------------

- Create a virtualenv::

    $ virtualenv2.6 --no-site-packages /path/to/my/venv

  Hereafter ``/path/to/my/venv`` will be referred to as $VENV in steps
  below.

- Install ``repoze.bfg``, ``pygments`` and ``Babel`` into your
  virtualenv using ``easy_install``::

    $ $VENV/bin/easy_install repoze.bfg pygments Babel

- Get a checkout of deform::

    $ svn co http://svn.repoze.org/deform/trunk deform

- ``cd`` to the newly checked out deform package::

    $ cd deform

- Run ``setup.py develop`` using the virtualenv's ``python`` command::

    $ $VENV/bin/python setup.py develop

- While your working directory is still ``deform``, start the demo
  application::

    $ $VENV/bin/paster serve deformdemo/demo.ini

- Visit http://localhost:8521 in a browser to see the demo.

Running the Demo's Selenium Tests
---------------------------------

The ``deformdemo`` application serves as a target for functional
testing during Deform's development.  A suite of Selenium tests may be
run against a local instance of the demonstration application.  It is
wise to run these tests before submitting a patch.  Here's how:

- Make sure you have a Java interpreter installed.

- Start the ``deformdemo`` application as described above in "Running
  the Demo".  Leave the terminal window running this application open,
  and open another terminal window to perform the below steps.

- Download `Selenium RC <http://seleniumhq.org/download/>`.

- Unpack the resulting zipfile into a directory (perhaps
  ``$HOME/opt/selenium``).

- ``cd`` to the ``selenium-server-1.0.3`` subdirectory of the
  directory to which you unpacked the zipfile.

- Run ``java -jar selenium-server.jar``.  Success is defined as seeing
  output on the console that ends like this::

   01:49:06.105 INFO - Started SocketListener on 0.0.0.0:4444
   01:49:06.105 INFO - Started org.openqa.jetty.jetty.Server@7d2a1e44

- Leave the terminal window in which the selenium server is now
  running open, and open (yet) another terminal window.

- In the newest terminal window, cd to the "deform" checkout directory
  you created above in "Running the Demo"::

   $ cd /path/to/my/deform/checkout

- Run the tests::

   $ $VENV/bin/python deformdemo/test.py

  ``$VENV`` is defined as it was in "Running the Demo" above.

- You will (hopefully) see Firefox pop up in a two-windowed
  arrangement, and it will begin to display in quick succession the
  loading of pages in the bottom window and some test output in the
  top window.  The tests will run for a minute or two.

- Test success means that the console window on which you ran
  ``test.py`` shows a bunch of dots, a test summary, then ``OK``.  If
  it shows a traceback, ``FAILED``, or anything other than a straight
  line of dots, it means there was an error.

- Fix any errors by modifying your code or by modifying the tests to
  expect the changes you've made.
