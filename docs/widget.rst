.. _widget:

Widgets
=======

A widget is a bit of code that is willing to:

- serialize a :term:`cstruct` into HTML for display in a form
  rendering

- deserialize data obtained from a form post (a :term:`pstruct`) into
  a data structure suitable for deserialization by a :term:`schema
  node` (a :term:`cstruct`).

- handle validation errors

Deform ships with a number of built-in widgets.  You hopefully needn't
create your own widget unless you're trying to do something that the
built-in widget set didn't anticipate.  However, when a built-in
Deform widget doesn't do exactly what you want, you can extend Deform
by creating a new widget that is more suitable for the task.

Widget Templates
----------------

A widget needn't use a template file, but each of the built-in widgets
does.  A template is usually assigned to a default widget via its
``template`` and ``readonly_template`` attributes; those attributes
are then used in the ``serialize`` method of the widget, ala:

.. code-block:: python
   :linenos:

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ''
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

The :meth:`deform.field.renderer` method is a method which accepts a
logical template name (such as ``texinput``) and renders it using the
active Deform :term:`renderer`; the default renderer is the ZPT
renderer, which uses the templates within the ``deform/templates``
directory within the :mod:`deform` package.  See :ref:`templates` for
more information about widget templates.

Widget Javascript
-----------------

Some built-in Deform widgets require JavaScript.  In order for the
built-in Deform widgets that require JavaScript to function properly,
the ``deform.load()`` JavaScript function must be called when the
page containing a form is renderered.

Some built-in Deform widgets include JavaScript which operates against
a local input element when it is loaded.  For example, the
:class:`deform.widget.AutocompleteInputWidget` template looks like
this:

.. code-block:: html
   :linenos:

    <span tal:omit-tag="">
        <input type="text"
               name="${field.name}"
               value="${cstruct}" 
               tal:attributes="size field.widget.size;
                               class field.widget.css_class"
               id="${field.oid}"/>
        <script tal:condition="field.widget.values" type="text/javascript">
          deform.addCallback(
            '${field.oid}',
            function (oid) {
                $('#' + oid).autocomplete({source: ${values}});
                $('#' + oid).autocomplete("option", ${options});
            }
          );
        </script>
    </span>

``field.oid`` refers to the ordered identifier that Deform gives to
each field widget rendering.  You can see that the script which runs
when this widget is included in a rendering calls a function named
``deform.addCallback``, passing it the value of ``field.oid`` and a
callback function as ``oid`` and ``callback`` respectively.  When it
is executed, the callback function calls the ``autocomplete`` method
of the JQuery selector result for ``$('#' + oid)``.

The callback define above will be called under two circumstances:

- When the page first loads and the ``deform.load()`` JavaScript
  function is called.

- When a :term:`sequence` is involved, and a sequence item is added,
  resulting in a call to the ``deform.addSequenceItem()`` JavaScript
  function.

The reason that default Deform widgets call ``deform.addCallback``
rather than simply using ``${field.oid}`` directly in the rendered
script is becase sequence item handling happens entirely client side
by cloning an existing prototype node, and before a sequence item can
be added, all of the ``id`` attributes in the HTML that makes up the
field must be changed to be unique.  The ``addCallback`` indirection
assures that the callback is executed with the *modified* oid rather
than the protoype node's oid.  Your widgets should do the same if they
are meant to be used as part of sequences.

.. _widget_requirements:

Widget Requirements and Resources
---------------------------------

Some widgets require external resources to work properly (such as CSS
and Javascript files).  Deform provides mechanisms that will allow you
to determine *which* resources are required by a particular form
rendering, so that your application may include them in the HEAD of
the page which includes the rendered form.

.. _get_widget_requirements:

The (Low-Level) :meth:`deform.Field.get_widget_requirements` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After a form has been fully populated with widgets, the
:meth:`deform.Field.get_widget_requirements` method called on the form
object will return a sequence of two-tuples.  When a non-empty
sequence is returned by :meth:`deform.Field.get_widget_requirements`,
it means that one or more CSS or JavaScript resources will need to be
loaded by the page performing the form rendering in order for some
widget on the page to function properly.

The first element in each two-tuple represents a *requirement name*.
It represents a logical reference to one *or more* Javascript or CSS
resources.  The second element in each two-tuple is the reqested
version of the requirement.  It may be ``None``, in which case the
version required is unspecified.  When the version required is
unspecified, a default version of the resource set will be chosen.

The requirement name / version pair implies a set of resources, but it
is not a URL, nor is it a filename or a filename prefix.  The caller
of :meth:`deform.Field.get_widget_requirements` must use the resource
names returned as *logical* references.  For example, if the
requirement name is ``jquery``, and the version id is ``1.4.2``, the
caller can take that to mean that the JQuery library should be loaded
within the page header via, for example the inclusion of the HTML
``<script type="text/javascript"
src="http://deformdemo.repoze.org/static/scripts/jquery-1.4.2.min.js"></script>``
within the HEAD tag of the rendered HTML page.

Users will almost certainly prefer to use the
:meth:`deform.Field.get_widget_resources` API (explained in the
succeeding section) to obtain a fully expanded list of relative
resource paths required by a form rendering.
:meth:`deform.Field.get_widget_requirements`, however, may be used if
custom requirement name to resource mappings need to be done without
the help of a :term:`resource registry`.

See also the description of ``requirements`` in
:class:`deform.Widget`.

.. _get_widget_resources:

The (High-Level) :meth:`deform.Field.get_widget_resources` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A mechanism to resolve the requirements of a form into relative
resource filenames exists as a method:
:meth:`deform.Field.get_widget_resources`.

.. note::

   Because Deform is framework-agnostic, this method only *reports* to
   its caller the resource paths required for a successful form
   rendering, it does not (cannot) arrange for the reported
   requirements to be satisfied in a page rendering; satisfying these
   requirements is the responsibility of the calling code.

The :meth:`deform.Field.get_widget_resources` method returns a
dictionary with two keys: ``js`` and ``css``.  The value related to
each key in the dictionary is a list of *relative* resource names.
Each resource name is assumed to be relative to the static directory
which houses your application's Deform resources (usually a copy of
the ``static`` directory inside the Deform package).  If the method is
called with no arguments, it will return a dictionary in the same form
representing resources it believes are required by the current form.
If it is called with a set of requirements (the value returned by the
:meth:`deform.Field.get_widget_requirements` method), it will attempt
to resolve the requirements passed to it.  You might use it like so:

.. code-block:: python
   :linenos:

   import deform

   form = deform.Form(someschema)
   resources = form.get_widget_resources()
   js_resources = resources['js']
   css_resources = resources['css']
   js_links = [ 'http://my.static.place/%s' % r for r in js_resources ]
   css_links = [ 'http://my.static.place/%s' % r for r in css_resources ]
   js_tags = ['<script type="text/javascript" src="%s"></script>' % link
              for link in js_links]
   css_tags = ['<link rel="stylesheet" href="%s"/>' % link
              for link in css_links]
   tags = js_tags + css_tags
   return {'form':form.render(), 'tags':tags}

The template rendering the return value would need to make sense of
"tags" (it would inject them wholesale into the HEAD).  Obviously,
other strategies for rendering HEAD tags can be devised using the
result of ``get_widget_resources``, this is just an example.
   
:meth:`deform.Field.get_widget_resources` uses a :term:`resource
registry` to map requirement names to resource paths.  If
:meth:`deform.Field.get_widget_resources` cannot resolve a requirement
name, or it cannot find a set of resources related to the supplied
*version* of the requirement name, an :exc:`ValueError` will be
raised.  When this happens, it means that the :term:`resource
registry` associated with the form cannot resolve a requirement name
or version.  When this happens, a resource registry that knows about
the requirement will need to be associated with the form explicitly,
e.g.:

.. code-block:: python
   :linenos:

   registry = deform.widget.ResourceRegistry()
   registry.set_js_resources('requirement', 'ver', 'bar.js', 'baz.js')
   registry.set_css_resources('requirement', 'ver', 'foo.css', 'baz.css')

   form = Form(schema, resource_registry=registry)
   resources = form.get_widget_resources()
   js_resources = resources['js']
   css_resources = resources['css']
   js_links = [ 'http://my.static.place/%s' % r for r in js_resources ]
   css_links = [ 'http://my.static.place/%s' % r for r in css_resources ]
   js_tags = ['<script type="text/javascript" src="%s"></script>' % link
              for link in js_links]
   css_tags = ['<link type="text/css" href="%s"/>' % link
              for link in css_links]
   tags = js_tags + css_tags
   return {'form':form.render(), 'tags':tags}

An alternate default resource registry can be associated with *all*
forms by calling the
:meth:`deform.Field.set_default_resource_registry` class method:

.. code-block:: python
   :linenos:

   registry = deform.widget.ResourceRegistry()
   registry.set_js_resources('requirement', 'ver', 'bar.js', 'baz.js')
   registry.set_css_resources('requirement', 'ver', 'foo.css', 'baz.css')
   Form.set_default_resource_registry(registry)

This will result in the ``registry`` registry being used as the
default resource registry for all form instances created after the
call to ``set_default_resource_registry``, hopefully allowing resource
resolution to work properly again.

See also the documentation of the ``resource_registry`` argument in
:class:`deform.Field` and the documentation of
:class:`deform.widget.ResourceRegistry`.

.. _specifying_widget_requirements:

Specifying Widget Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a new widget, you may specify its requirements by using
the ``requirements`` attribute:

.. code-block:: python
   :linenos:

   from deform.widget import Widget

   class MyWidget(Widget):
       requirements = ( ('jquery', '1.4.2'), )

There are no hard-and-fast rules about the composition of a
requirement name.  Your widget's docstring should explain what its
requirement names mean, and how map to the logical requirement name to
resource paths within a a :term:`resource registry`.  For example,
your docstring might have text like this: "This widget uses a library
name of ``jquery.tools`` in its requirements list.  The name
``jquery.tools`` implies that the JQuery Tools library must be loaded
before rendering the HTML page containing any form which uses this
widget; JQuery Tools depends on JQuery, so JQuery should also be
loaded.  The widget expects JQuery Tools version X.X (as specified in
the version field), which expects JQuery version X.X to be loaded
previously.".  It might go on to explain that a set of resources need
to be added to a :term:`resource registry` in order to resolve the
logical ``jquery.tools`` name to a set of relative resource paths, and
that the resulting custom resource registry should be used when
constructing the form.  The default resource registry
(:attr:`deform.widget.resource_registry`) does not contain resource
mappings for your newly-created requirement.

.. _writing_a_widget:

Writing Your Own Widget
-----------------------

Writing a Deform widget means creating an object that supplies the
notional Widget interface, which is described in the
:class:`deform.widget.Widget` class documentation.  The easiest way to
create something that implements this interface is to create a class
which inherits directly from the :class:`deform.widget.Widget` class
itself.

The :class:`deform.widget.Widget` class has a concrete implementation
of a constructor and the ``handle_error`` method as well as default
values for all required attributes.  The :class:`deform.widget.Widget`
class also has abstract implementations of ``serialize`` and
``deserialize`` each of which which raises a
:exc:`NotImplementedError` exception; these must be overridden by your
subclass; you may also optionally override the ``handle_error`` method
of the base class.

For example:

.. code-block:: python
   :linenos:

    from deform.widget import Widget

    class MyInputWidget(Widget):
        def serialize(self, field, cstruct=None, readonly=False):
            ...

        def deserialize(self, field, pstruct=None):
            ...

        def handle_error(self, field, error):
            ...

We describe the ``serialize``, ``deserialize`` and ``handle_error``
methods below.

The ``serialize`` Method
~~~~~~~~~~~~~~~~~~~~~~~~

The ``serialize`` method of a widget must serialize a :term:`cstruct`
value to an HTML rendering.  A :term:`cstruct` value is the value
which results from a :term:`Colander` schema serialization for the
schema node associated with this widget.  The result of this method
should always be a ``unicode`` type containing some HTML.

The ``field`` argument passed to ``serialize`` is the :term:`field`
object to which this widget is attached.  Because a :term:`field`
object itself has a reference to the widget it uses (as
``field.widget``), the field object is passed to the ``serialize``
method of the widget rather than the widget having a ``field``
attribute in order to avoid a circular reference.

If the ``readonly`` argument passed to ``serialize`` is ``True``, it
indicates that the result of this serialization should be a read-only
rendering (no active form controls) of the ``cstruct`` data to HTML.

Let's pretend our new ``MyInputWidget`` only needs to create a text
input control during serialization.  Its ``serialize`` method might
get defined as so:

.. code-block:: python
   :linenos:

    from deform.widget import Widget
    from colander import null
    import cgi

    class MyInputWidget(Widget):
        def serialize(self, field, cstruct=None, readonly=False):
            if cstruct is null:
                cstruct = u''
            quoted = cgi.escape(cstruct, quote='"')
            return u'<input type="text" value="%s">' % quoted

Note that every ``serialize`` method is responsible for returning a
serialization, no matter whether it is provided data by its caller or
not.  Usually, the value of ``cstruct`` will contain appropriate data
that can be used directly by the widget's rendering logic.  But
sometimes it will be ``colander.null``.  It will be ``colander.null``
when a form which uses this widget is serialized without any data; for
example an "add form".

All widgets *must* check if the value passed as ``cstruct`` is the
``colander.null`` sentinel value during ``serialize``.  Widgets are
responsible for handling this eventuality, often by serializing a
logically "empty" value.

Regardless of how the widget attempts to compute the default value, it
must still be able to return a rendering when ``cstruct`` is
``colander.null``.  In the example case above, the widget uses the
empty string as the ``cstruct`` value, which is appropriate for this
type of "scalar" input widget; for a more "structural" kind of widget
the default might be something else like an empty dictionary or list.

The ``MyInputWidget`` we created in the example does not use a
template. Any widget may use a template, but using one is not
required; whether a particular widget uses a template is really none
of Deform's business: deform simply expects a widget to return a
Unicode object containing HTML from the widget's ``serialize`` method;
it doesn't really much care how the widget creates that Unicode
object.

Each of the built-in Deform widgets (the widget implementations in
:mod:`deform.widget`) happens to use a template in order to make it
easier for people to override how each widget looks when rendered
without needing to change Deform-internal Python code.  Instead of
needing to change the Python code related to the widget itself, users
of the built-in widgets can often perform enough customization by
replacing the template associated with the built-in widget
implementation.  However, this is purely a convenience; templates are
largely a built-in widget set implementation detail, not an integral
part of the core Deform framework.

Note that "scalar" widgets (widgets which represent a single value as
opposed to a collection of values) are not responsible for providing
"page furniture" such as a "Required" label or a surrounding div which
is used to provide error information when validation fails.  This is
the responsibility of the "structural" widget which is associated with
the parent field of the scalar widget's field (the "parent widget");
the parent widget is usually one of
:class:`deform.widget.MappingWidget` or
:class:`deform.widget.SequenceWidget`.

The ``deserialize`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``deserialize`` method of a widget must deserialize a
:term:`pstruct` value to a :term:`cstruct` value and return the
:term:`cstruct` value.  The ``pstruct`` argument is a value resulting
from the ``parse`` method of the :term:`Peppercorn` package. The
``field`` argument is the field object to which this widget is
attached.

.. code-block:: python
   :linenos:

    from deform.widget import Widget
    from colander import null
    import cgi

    class MyInputWidget(Widget):
        def serialize(self, field, cstruct, readonly=False):
            if cstruct is null:
                cstruct = u''
            return '<input type="text" value="%s">' % cgi.escape(cstruct)

        def deserialize(self, field, pstruct):
            if pstruct is null:
                return null
            return pstruct

Note that the ``deserialize`` method of a widget must, like
``serialize``, deal with the possibility of being handed a
``colander.null`` value.  ``colander.null`` will be passed to the
widget when a value is missing from the pstruct. The widget usually
handles being passed a ``colander.null`` value in ``deserialize`` by
returning `colander.null``, which signifies to the underlying schema
that the default value for the schema node should be used if it
exists.

The only other real constraint of the deserialize method is that the
``serialize`` method must be able to reserialize the return value of
``deserialize``.

The ``handle_error`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`deform.widget.Widget` class already has a suitable
implementation; if you subclass from :class:`deform.widget.Widget`,
overriding the default implementation is not necessary unless you need
special error-handling behavior.

Here's an implementation of the
:meth:`deform.widget.Widget.handle_error` method in the MyInputWidget
class:

.. code-block:: python
   :linenos:

    from deform.widget import Widget
    from colander import null
    import cgi

    class MyInputWidget(Widget):
        def serialize(self, field, cstruct, readonly=False):
            if cstruct is null:
                cstruct = u''
            return '<input type="text" value="%s">' % cgi.escape(cstruct)

        def deserialize(self, field, pstruct):
            if pstruct is null:
                return null
            return pstruct

        def handle_error(self, field, error):
            if field.error is None:
                field.error = error
            for e in error.children:
                for num, subfield in enumerate(field.children):
                    if e.pos == num:
                        subfield.widget.handle_error(subfield, e)

The ``handle_error`` method of a widget must:

- Set the ``error`` attribute of the ``field`` object it is passed if
  the ``error`` attribute has not already been set.

- Call the ``handle_error`` methods of any subfields which
  also have errors.

The ability to override ``handle_error`` exists purely for advanced
tasks, such as presenting all child errors of a field on a parent
field.  For example:

.. code-block:: python
   :linenos:

    def handle_error(self, field, error):
        msgs = []
        if error.msg:
            field.error = error
        else:
            for e in error.children:
                msgs.append('line %s: %s' % (e.pos+1, e))
            field.error = Invalid(field.schema, '\n'.join(msgs))

This implementation does not attach any errors to field children;
instead it attaches all of the child errors to the field itself for
review.

The Template
~~~~~~~~~~~~

The template you use to render a widget will receive input from the
widget object, including ``field``, which will be the field object
represented by the widget.  It will usually use the ``field.name``
value as the ``name`` input element of the primary control in the
widget, and the ``field.oid`` value as the ``id`` element of the
primary control in the widget.

