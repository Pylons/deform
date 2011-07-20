.. _templates:

Templates
=========

A set of :term:`Chameleon` templates is used by the default widget set
present in :mod:`deform` to make it easier to customize the look and
feel of form renderings.

Overriding the default templates
--------------------------------

The default widget set uses templates that live in the ``templates``
directory of the :mod:`deform` package. If you are comfortable using
the :term:`Chameleon` templating system, but you simply need to
override some of these templates you can create your own template
directory and copy the template you wish to customize into it. You can
then either configure your new template directory to be used for all
forms or for specific forms as described below.

For relevant API documentation see the
:class:`deform.ZPTRendererFactory` class and the :class:`deform.Field`
class ``renderer`` argument.

Overriding for all forms
~~~~~~~~~~~~~~~~~~~~~~~~

To globally override templates use the
:meth:`deform.Field.set_zpt_renderer` class method to change the
settings associated with the default ZPT renderer:

.. code-block:: python

   from pkg_resources import resource_filename
   from deform import Form

   deform_templates = resource_filename('deform', 'templates')
   search_path = ('/path/to/my/templates', deform_templates)

   Form.set_zpt_renderer(search_path)

Now, the templates in ``/path/to/my/templates`` will be used in
preference to the default templates whenever a form is rendered.
Any number of template directories can be put into the search path and
will be searched in the order specified with the first matching
template found being used.

Overriding for specific forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you only want to change the templates used for a specific form, or
even for the specific rendering of a form, you can pass a ``renderer``
argument to the :class:`deform.Form` constructor, e.g.:

.. code-block:: python

   from deform import ZPTRendererFactory
   from deform import Form
   from pkg_resources import resource_filename

   deform_templates = resource_filename('deform', 'templates')
   search_path = ('/path/to/my/templates', deform_templates)
   renderer = ZPTRendererFactory(search_path)

   form = Form(someschema, renderer=renderer)

When the above form is rendered, the templates in
``/path/to/my/templates`` will be used in  preference to the default
templates. Any number of template directories can be put into the
search path and will be searched in the order specified with the first
matching template found being used.

.. _creating_a_renderer:

Using an alternative templating system
--------------------------------------

A :term:`renderer` is used by the each widget implementation in
:mod:`deform` to render HTML from a set of templates. By default, each
of the default Deform widgets uses a template written in the Chameleon
ZPT templating language. If you'd rather use a different templating
system for your widgets, you can. To do so, you need to:

- Write an alternate renderer that uses the templating system of your
  choice.

- Optionally, convert all the existing Deform templates to your
  templating language of choice.  This is only necessary if you choose
  to use the widgets that ship as part of Deform.

- Set the default renderer of the :class:`deform.Form` class.

Creating a Renderer
~~~~~~~~~~~~~~~~~~~

A renderer is simply a callable that accepts a single positional
argument, which is the template name, and a set of keyword arguments.
The keyword arguments it will receive are arbitrary, and differ per
widget, but the keywords usually include ``field``, a :term:`field`
object, and ``cstruct``, the data structure related to the field that
must be rendered by the template itself.

Here's an example of a (naive) renderer that uses the Mako templating
engine:

.. code-block:: python
   :linenos:


   from mako.template import Template

   def mako_renderer(tmpl_name, **kw):
       template = Template(filename='/template_dir/%s.mak' % tmpl_name)
       return template.render(**kw)

.. note:: A more robust implementation might use a template loader
   that does some caching, or it might allow the template directory to
   be configured.

Note the ``mako_renderer`` function we've created actually appends a
``.mak`` extension to the ``tmpl_name`` it is passed.  This is because
Deform passes a template name without any extension to allow for
different templating systems to be used as renderers.

Our ``mako_renderer`` renderer is now ready to have some templates
created for it.

Converting the Default Deform Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :mod:`deform` package contains a directory named ``templates``.  You can
see the current trunk contents of this directory by `browsing the source
repository
<https://github.com/Pylons/deform/tree/master/deform/templates>`_. Each file
within this directory and any of its subdirectories is a Chameleon ZPT
template that is used by a default Deform widget.

For example, ``textinput.pt`` ZPT template, which is used by the
:class:`deform.widget.TextInputWidget` widget and which renders a text
input control looks like this:

.. literalinclude:: ../deform/templates/textinput.pt
   :language: xml
   :linenos:

If we created a Mako renderer, we would need to create an analogue of
this template.  Such an analogue should be named ``textinput.mak`` and
might look like this:

.. code-block:: text
   :linenos:

   <input type="text" name="${field.name}" value="${cstruct}"
   % if field.widget.size:
   size=${field.widget.size}
   % endif
   />

Whatever the body of the template looks like, the resulting
``textinput.mak`` should be placed in a directory that is meant to
house other Mako template files which are going to be consumed by
Deform.  You'll need to convert each of the templates that exist in
the Deform ``templates`` directory and its subdirectories, and put all
of the resulting templates into your private mako ``templates`` dir
too, retaining any directory structure (e.g., retaining the fact that
there is a ``readonly`` directory and converting its contents).

Configuring Your New Renderer as the Default
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've created a new renderer and created templates that match
all the existing Deform templates, you can now configure your renderer
to be used by Deform.  In startup code, add something like:

.. code-block:: python
   :linenos:

   from mymakorenderer import mako_renderer

   from deform import Form
   Form.set_default_renderer(mako_renderer)

The deform widget system will now use your renderer as the default
renderer.

Note that calling :meth:`deform.Field.set_default_renderer` will cause this
renderer to be used by default by all consumers in the process it's invoked
in.  This is potentially undesirable: you may need the same process to use
more than one renderer perhaps because that same process houses two different
Deform-using systems.  In this case, instead of using the
``set_default_renderer`` method, you can write your application in such a way
that it passes a renderer to the Form constructor:

.. code-block:: python
   :linenos:

   from mymakorenderer import mako_renderer
   from deform import Form

   ...
   schema = SomeSchema()
   form = Form(schema, renderer=mako_renderer)

