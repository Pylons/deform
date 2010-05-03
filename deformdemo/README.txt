deformdemo
==========

Software which demonstrates the operation of the ``deform`` form
generation package.

To use it, install deform with the "demo" extra; preferably from
within a virtualenv::

   bin/easy_install deform[demo]

This will cause ``repoze.bfg``, ``Pygments``, ``Babel``, and a number
of other dependencies to be installed along with deform.

Get a checkout of deform:

  svn co http://svn.repoze.org/svn/deform/trunk deform

cd to the deform package:

  cd deform

To start the demo, run:

  bin/paster serve deformdemo/demo.ini

Visit http://localhost:8521 to see the demo.


