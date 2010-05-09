Deform
======

:mod:`deform` is a Python HTML form generation library.

The design of :mod:`deform` is heavily influenced by the `formish
<http://ish.io/projects/show/formish>`_ form generation library.  Some
might even say it's a shameless rip-off, which would not be
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

Topics
======

.. toctree::
   :maxdepth: 2

   basics.rst
   components.rst
   serialization.rst
   renderer.rst
   widget.rst
   app.rst
   api.rst
   interfaces.rst
   glossary.rst

Topics Needing Documentation
----------------------------

- FileUploadWidget tmpstore.

- Multiple forms on the same page.

- Form post target changing.

- Associating a Colander type with a new default widget type.

- Setting a widget on a field.

- Internationalization

- Templates

- form.css / structure.css / theme.css

- JS (deform.js / jquery...js / wufoo.js)

- Changing the close button image.

- 

Documentation Done, But Could be Better
---------------------------------------

- The Form class (and thee Button class) explanations.

Thanks To
---------

Without these people, this software would not exist:

- The Formish guys (http://ish.io)

- Fear Factory (http://fearfactory.com)

- Midlake (http://midlake.net)


Demonstrations and Development
==============================

Demo Site
---------

Visit `deformdemo.repoze.org <http://deformdemo.repoze.org>`_ to view
an application which demonstrates most of Deform's features.  The
source code for this application is also available in the `deform
package within the Repoze SVN repository
<http://svn.repoze.org/deform/trunk/deformdemo>`_.

Development
-----------

You can check the deform package out of the Repoze SVN repository via
the following command::

   svn co http://svn.repoze.org/deform/trunk deform

Index and Glossary
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
