deform.demo
===========

Software which demonstrates the operation of the ``deform`` form
generation package.

To use it, install deform with the "demo" extra; preferably from
within a virtualenv::

   bin/easy_install deform[demo]

This will cause ``repoze.bfg``, ``Pygments``, ``Babel``, and a number
of other dependencies to be installed along with deform.

To subsequently start it, run:

  bin/paster serve lib/pythonX.X/site-packages/deform/demo/demo.ini

Visit http://localhost:8521 to see the demo.


