Deform
======

:mod:`deform` is a Python HTML form generation library.

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

Topics
======

.. toctree::
   :maxdepth: 2

   basics.rst
   components.rst
   serialization.rst
   templates.rst
   widget.rst
   app.rst
   i18n.rst
   api.rst
   interfaces.rst
   glossary.rst

Demonstration Site
==================

Visit `deformdemo.repoze.org <http://deformdemo.repoze.org>`_ to view
an application which demonstrates most of Deform's features.  The
source code for this application is also available in the `deform
package within the Repoze SVN repository
<http://svn.repoze.org/deform/trunk/deformdemo>`_.

Support and Development
=======================

To report bugs, use the `bug tracker <http://bfg.repoze.org/trac>`_.

If you've got questions that aren't answered by this documentation,
contact the `Repoze-dev maillist
<http://lists.repoze.org/listinfo/repoze-dev>`_ or join the `#repoze
IRC channel <irc://irc.freenode.net/#repoze>`_.

Browse and check out tagged and trunk versions of :mod:`deform`
via the `Repoze Subversion repository
<http://svn.repoze.org/deform/>`_.  To check out the trunk
via Subversion, use this command::

   svn co http://svn.repoze.org/deform/trunk deform

To find out how to become a contributor to :mod:`deform`, please see
the `Repoze hacking documentation <http://docs.repoze.org/hacking/>`_
or the `contributor's page <http://repoze.org/contributing.html>`_.

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

