deformdemo
==========

Software which demonstrates the operation of the ``deform`` form
generation package.

Running the Demo
----------------

Running the Demo
----------------

- Run buildout::

    $ python bootstrap.py
    $ bin/buildout

- Fire up the instance::

    $ bin/paster serve demo.ini

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
