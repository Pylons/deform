.. _overview:

Deform
======

:mod:`deform` is a Python HTML form generation library.  It runs under Python
2.x, 3.x and PyPy.

Deform is a Python form library for generating HTML forms on the server side.
`Date and time picking widgets <https://deformdemo.pylonsproject.org/datetimeinput/>`_,
`rich text editors <https://deformdemo.pylonsproject.org/richtext/>`_, `forms with
dynamically added and removed items
<https://deformdemo.pylonsproject.org/sequence_of_mappings/>`_ and a few other `complex
use cases <https://deformdemo.pylonsproject.org/>`_ are supported out of the box.

Deform integrates with the `Pyramid web framework <https://trypyramid.com/>`_
and several other web frameworks. Deform comes with `Chameleon templates
<https://chameleon.readthedocs.io/en/latest/>`_ and `Bootstrap 3
<https://getbootstrap.com>`_ styling. Under the hood, `Colander schemas
<https://github.com/Pylons/colander>`_ are used for serialization and
validation. The `Peppercorn <https://github.com/Pylons/peppercorn>`_ library
maps HTTP form submissions to nested structure.

Although Deform uses Chameleon templates internally, you can embed rendered
Deform forms into any template language.

Topics
======

.. toctree::
   :maxdepth: 1

   basics.rst
   retail.rst
   common_needs.rst
   components.rst
   serialization.rst
   templates.rst
   widget.rst
   validation.rst
   app.rst
   ajax.rst
   i18n.rst
   api.rst
   interfaces.rst
   glossary.rst
   changes.rst

Community and links
===================

* `Widget examples <https://deformdemo.pylonsproject.org>`_

* `PyPi <https://pypi.org/project/deform/>`_

* `Issue tracker <https://github.com/Pylons/deform/issues>`_

* `Widget examples repo <https://github.com/Pylons/deformdemo/>`_

* `Documentation <https://docs.pylonsproject.org/projects/deform/en/latest/>`_

* `Support <https://pylonsproject.org/community-support.html>`_

Demonstration Site
==================

Visit `deformdemo.pylonsproject.org <https://deformdemo.pylonsproject.org>`_ to view an
application which demonstrates most of Deform's features.  The source code
for this application is also available in the `deformdemo package on GitHub
<https://github.com/Pylons/deformdemo>`_.

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
