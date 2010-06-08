.. _writing_a_widget:

Writing Your Own Widget
=======================

A widget is a bit of code that is willing to:

- serialize a data structure to HTML for display in a form rendering

- deserialize data obtained from a form post to a data structure
  suitable for consumption by a :term:`schema node`

- handle validation errors

Deform ships with a good number of default widgets.  You hopefully
needn't create your own widget unless you're trying to do something
that the default widget set didn't anticipate.  When a default Deform
widget doesn't do exactly what you want, you can extend Deform by
creating a new widget that is more suitable for the task.

The Widget Interface
--------------------

Writing a Deform widget means creating an object that supplies the
notional Widget interface, which is described in the docstrings of the
:class:`deform.widget.Widget` class.  The easiest way to create
something that implements this interface is to create a class which
inherits directly from the :class:`deform.widget.Widget` class itself.

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

All widgets *must* check if the value passed as ``cstruct`` is
``colander.null`` during ``serialize``.  Widgets are responsible for
handling this eventuality, often by serializing a logically "empty"
value.

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

Each of the default Deform widgets (the widget implementations in
:mod:`deform.widget`) happens to use a template in order to make it
easier for people to override how each widget looks when rendered
without needing to change Deform-internal Python code.  Instead of
needing to change the Python code related to the widget itself, users
of the default widgets can often perform enough customization by
replacing the template associated with the default widget
implementation.  However, this is purely a convenience; templates are
a widget set implementation detail, not an integral part of the
core Deform framework.

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
    from colander import default
    import cgi

    class MyInputWidget(Widget):
        def serialize(self, field, cstruct, readonly=False):
            if cstruct is null:
                cstruct = u''
            return '<input type="text" value="%s">' % cgi.escape(cstruct)

        def deserialize(self, field, pstruct):
            if cstruct is null:
                return default
            return pstruct

Note that both the deserialize method of a widget must also deal with
the ``colander.null`` value (usually by returning `colander.default``,
which signifies to the schema that the default value should be used if
it exists).  ``colander.null`` will be passed to the widget when a
value is missing from the pstruct.

The only other real constraint of the deserialize method is that the
``serialize`` method must be able to reserialize the return value of
``deserialize``.  One caveat exists: if ``deserialize`` returns
``colander.default``, the ``serialize`` method needn't deal with it
explicitly; it's handled at a higher level.

