.. _overview:

Deform
======

:mod:`deform` is a Python HTML form generation library.  It runs under Python
3.8, 3.9, 3.10, 3.11, and 3.12 and PyPy3.

Deform is a Python form library for generating HTML forms on the server side.
`Date and time picking widgets <https://deformdemo.pylonsproject.org/datetimeinput/>`_,
`rich text editors <https://deformdemo.pylonsproject.org/richtext/>`_, `forms with
dynamically added and removed items
<https://deformdemo.pylonsproject.org/sequence_of_mappings/>`_ and a few other `complex
use cases <https://deformdemo.pylonsproject.org/>`_ are supported out of the box.

Deform integrates with the `Pyramid web framework <https://trypyramid.com/>`_
and several other web frameworks. Deform comes with `Chameleon templates
<https://chameleon.readthedocs.io/en/latest/>`_ and `Bootstrap 5
<https://getbootstrap.com/docs/5.3/>`_ styling. Under the hood, `Colander schemas
<https://github.com/Pylons/colander>`_ are used for serialization and
validation. The `Peppercorn <https://github.com/Pylons/peppercorn>`_ library
maps HTTP form submissions to nested structure.

Although Deform uses Chameleon templates internally, you can embed rendered
Deform forms into any template language.

Topics
======

.. toctree::
   :maxdepth: 1

   basics
   retail
   common_needs
   components
   serialization
   templates
   widget
   validation
   app
   ajax
   i18n
   api
   interfaces
   glossary
   changes

Demonstration Site
==================

Visit `deformdemo.pylonsproject.org <https://deformdemo.pylonsproject.org>`_ to view an
application which demonstrates most of Deform's features.  The source code
for this application is also available in the `deformdemo package on GitHub
<https://github.com/Pylons/deformdemo>`_.

Community and links
===================

* `Deform on PyPI <https://pypi.org/project/deform/>`_
* `Deform issue tracker <https://github.com/Pylons/deform/issues>`_
* `Support <https://pylonsproject.org/community-support.html>`_

Thanks
======

The design of :mod:`deform` is heavily influenced by the `formish
<https://pypi.org/project/formish/>`_ form generation library.  Some
might even say it's a shameless rip-off; this would not be completely
inaccurate.  It differs from formish mostly in ways that make the
implementation (arguably) simpler and smaller.

Without these people, this software would not exist:

- The Formish guys
- Tres Seaver
- `Fear Factory <http://fearfactory.com>`_
- `Midlake <https://www.midlake.net/>`_

Index and Glossary
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
