.. _overview:

Deform
======

:mod:`deform` is a Python HTML form generation library.  It runs under Python
2.6, 2.7, 3.2 and 3.3.

The design of :mod:`deform` is heavily influenced by the `formish
<http://ish.io/projects/show/formish>`_ form generation library.  Some
might even say it's a shameless rip-off; this would not be completely
inaccurate.  It differs from formish mostly in ways that make the
implementation (arguably) simpler and smaller.

:mod:`deform` uses :term:`Colander` as a schema library,
:term:`Peppercorn` as a form control deserialization library, and
:term:`Chameleon` to perform HTML templating.

:mod:`deform` depends only on Peppercorn, Colander, Chameleon and an
internationalization library named translationstring, so it may be
used in most web frameworks (or antiframeworks) as a result.

Alternate templating languages may be used, as long as all templates
are translated from the native Chameleon templates to your templating
system of choice and a suitable :term:`renderer` is supplied to
:mod:`deform`.

.. warning::

   Despite the version number at the top, this documentation has not been
   updated for the 2.X release line of Deform.  Most of the documentation
   will still apply, but where it does not, see the :ref:`changelog` for
   an overview of changes between 0.9.9 and this release.
   Also, please see http://deform2demo.repoze.org .

Topics
======

.. toctree::
   :maxdepth: 2

   basics.rst
   retail.rst
   common_needs.rst
   components.rst
   serialization.rst
   templates.rst
   widget.rst
   app.rst
   ajax.rst
   i18n.rst
   contributing.rst
   community.rst
   api.rst
   interfaces.rst
   glossary.rst
   changes.rst

Demonstration Site
==================

Visit `deform2demo.repoze.org <http://deform2demo.repoze.org>`_ to view an
application which demonstrates most of Deform's features.  The source code
for this application is also available in the `deform package on GitHub
<https://github.com/Pylons/deform>`_.

Index and Glossary
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Thanks
======

Without these people, this software would not exist:

- The Formish guys (http://ish.io)

- Tres Seaver

- Fear Factory (http://fearfactory.com)

- Midlake (http://midlake.net)

