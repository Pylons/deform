Common Needs
============

This chapter collects solutions for requirements that will often crop
up once you start using Deform for real world applications.

.. _changing_a_default_widget:

Changing the Default Widget Associated With a Field
---------------------------------------------------

Let's take another look at our familiar schema:

.. code-block:: python
   :linenos:

   import colander

   class Person(colander.MappingSchema):
       name = colander.SchemaNode(colander.String())
       age = colander.SchemaNode(colander.Integer(),
                                 validator=colander.Range(0, 200))

   class People(colander.SequenceSchema):
       person = Person()

   class Schema(colander.MappingSchema):
       people = People()

   schema = Schema()

This schema renders as a *sequence* of *mapping* objects.  Each
mapping has two leaf nodes in it: a *string* and an *integer*.  If you
play around with the demo at
`http://deformdemo.repoze.org/sequence_of_mappings/
<http://deformdemo.repoze.org/sequence_of_mappings/>`_ you'll notice
that, although we don't actually specify a particular kind of widget
for each of these fields, a sensible default widget is used.  This is
true of each of the default types in :term:`Colander`.  Here is how
they are mapped by default.  In the following list, the schema type
which is the header uses the widget underneath it by default.

:class:`colander.Mapping`
   :class:`deform.widget.MappingWidget`

:class:`colander.Sequence`
    :class:`deform.widget.SequenceWidget`

:class:`colander.String`
    :class:`deform.widget.TextInputWidget`

:class:`colander.Integer`
    :class:`deform.widget.TextInputWidget`

:class:`colander.Float`
    :class:`deform.widget.TextInputWidget`

:class:`colander.Decimal`
    :class:`deform.widget.TextInputWidget`

:class:`colander.Boolean`
    :class:`deform.widget.CheckboxWidget`

:class:`colander.Date`
    :class:`deform.widget.DateInputWidget`

:class:`colander.DateTime`
    :class:`deform.widget.DateTimeInputWidget`

:class:`colander.Tuple`
    :class:`deform.widget.Widget`

.. note::

   Not just any widget can be used with any schema type; the
   documentation for each widget usually indicates what type it can be
   used against successfully.  If all existing widgets provided by
   Deform are insufficient, you can use a custom widget.  See
   :ref:`writing_a_widget` for more information about writing 
   a custom widget.

If you are creating a schema that contains a type which is not in this
list, or if you'd like to use a different widget for a particular
field, or you want to change the settings of the default widget
associated with the type, you need to associate the field with the
widget "by hand".  There are a number of ways to do so, as outlined in
the sections below.

As an argument to a :class:`colander.SchemaNode` constructor
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

As of Deform 0.8, you may specify the widget as part of the
schema:

.. code-block:: python
   :linenos:

   import colander

   from deform import Form
   from deform.widget import TextInputWidget

   class Person(colander.MappingSchema):
       name = colander.SchemaNode(colander.String(),
                                  widget=TextAreaWidget())
       age = colander.SchemaNode(colander.Integer(),
                                 validator=colander.Range(0, 200))

   class People(colander.SequenceSchema):
       person = Person()

   class Schema(colander.MappingSchema):
       people = People()

   schema = Schema()

   myform = Form(schema, buttons=('submit',))

Note above that we passed a ``widget`` argument to the ``name`` schema
node in the ``Person`` class above.  When a schema containing a node
with a ``widget`` argument to a schema node is rendered by Deform, the
widget specified in the node constructor is used as the widget which
should be associated with that node's form rendering.  In this case,
we'll be using a :class:`deform.widget.TextAreaWidget` as the ``name``
widget.

.. note::

  Widget associations done in a schema are always overridden by
  explicit widget assigments performed via
  :meth:`deform.Field.__setitem__` and
  :meth:`deform.Field.set_widgets`.

Using dictionary access to change the widget
++++++++++++++++++++++++++++++++++++++++++++

After the :class:`deform.Form` constructor is called with the schema
you can change the widget used for a particular field by using
dictionary access to get to the field in question.  A
:class:`deform.Form` is just another kind of :class:`deform.Field`, so
the method works for either kind of object.  For example:

.. code-block:: python
   :linenos:

   from deform import Form
   from deform.widget import TextInputWidget

   myform = Form(schema, buttons=('submit',))
   myform['people']['person']['name'].widget = TextInputWidget(size=10)

This associates the :class:`~colander.String` field named ``name``
in the rendered form with an explicitly created
:class:`deform.widget.TextInputWidget` by finding the ``name`` field
via a series of ``__getitem__`` calls through the field
structure, then by assigning an explicit ``widget`` attribute to the
``name`` field.

You might want to do this in order to pass a ``size``
argument to the explicit widget creation, indicating that the size of
the ``name`` input field should be 10em rather than the default.  

Although in the example above, we associated the ``name`` field with
the same type of widget as its default we could have just as easily
associated the ``name`` field with a completely different widget using
the same pattern.  For example:

.. code-block:: python
   :linenos:

   from deform import Form
   from deform.widget import TextInputWidget

   myform = Form(schema, buttons=('submit',))
   myform['people']['person']['name'].widget = TextAreaWidget()

The above renders an HTML ``textarea`` input element for the ``name``
field instead of an ``input type=text`` field.  This probably doesn't
make much sense for a field called ``name`` (names aren't usually
multiline paragraphs); but it does let us demonstrate how different
widgets can be used for the same field.

Using the :meth:`deform.Field.set_widgets` method
+++++++++++++++++++++++++++++++++++++++++++++++++

Equivalently, you can also use the :meth:`deform.Field.set_widgets`
method to associate multiple widgets with multiple fields in a form.
For example:

.. code-block:: python
   :linenos:

   from deform import Form
   from deform.widget import TextInputWidget

   myform = Form(schema, buttons=('submit',))
   myform.set_widgets({'people.person.name':TextAreaWidget(),
                       'people.person.age':TextAreaWidget()})

Each key in the dictionary passed to :meth:`deform.Field.set_widgets`
is a "dotted name" which resolves to a single field element.  Each
value in the dictionary is a widget instance.  See
:meth:`deform.Field.set_widgets` for more information about this
method and dotted name resolution, including special cases which
involve the "splat" (``*``) character and the empty string as a key
name.

.. _masked_input:

Using Text Input Masks
----------------------

The :class:`deform.widget.TextInputWidget` and
:class:`deform.widget.CheckedInputWidget` widgets allow for the use of
a fixed-length text input mask.  Use of a text input mask causes
placeholder text to be placed in the text field input, and restricts
the type and length of the characters input into the text field.

For example:

.. code-block: python

   form['ssn'].widget = TextInputWidget(mask='999-99-9999')

When using a text input mask:

``a`` represents an alpha character (A-Z,a-z)

``9`` represents a numeric character (0-9)

``*`` represents an alphanumeric character (A-Z,a-z,0-9)

All other characters in the mask will be considered mask literals.

By default the placeholder text for non-literal characters in the
field will be ``_`` (the underscore character).  To change this for a
given input field, use the ``mask_placeholder`` argument to the
TextInputWidget:

.. code-block:: python

   form['date'].widget = TextInputWidget(mask='99/99/9999', 
                                         mask_placeholder="-")

Example masks:

Date
    99/99/9999

US Phone
    (999) 999-9999

US SSN
    999-99-9999

When this option is used, the :term:`jquery.maskedinput` library must
be loaded into the page serving the form for the mask argument to have
any effect.  A copy of this library is available in the
``static/scripts`` directory of the :mod:`deform` package itself.

See `http://deformdemo.repoze.org/text_input_masks/
<http://deformdemo.repoze.org/text_input_masks/>`_ for a working
example.

Use of a text input mask is not a replacement for server-side
validation of the field; it is purely a UI affordance.  If the data
must be checked at input time a separate :term:`validator` should be
attached to the related schema node.


.. _autocomplete_input:

Using the AutocompleteInputWidget
---------------------------------

The :class:`deform.widget.AutocompleteInputWidget` widget allows for
client side autocompletion from provided choices in a text input
field. To use this you **MUST** ensure that :term:`jQuery` and the
:term:`JQuery UI` plugin are available to the page where the
:class:`deform.widget.AutocompleteInputWidget` widget is rendered.

For convenience a version of the :term:`JQuery UI` (which includes the
``autocomplete`` sublibrary) is included in the :mod:`deform` static
directory. Additionally, the :term:`JQuery UI` styles for the
selection box are also included in the :mod:`deform` ``static``
directory. See :ref:`serving_up_the_rendered_form` and
:ref:`get_widget_resources` for more information about using the 
included libraries from your application.

A very simple example of using
:class:`deform.widget.AutocompleteInputWidget` follows:

.. code-block:: python

   form['frozznobs'].widget = AutocompleteInputWidget(
                                values=['spam', 'eggs', 'bar', 'baz'])

Instead of a list of values a URL can be provided to values:

.. code-block:: python

   form['frobsnozz'].widget = AutocompleteInputWidget(
                                values='http://example.com/someapi')

In the above case a call to the url should provide results one item
per line in the response. Something like::

    item-one
    item-two
    item-three


Some options for the :term:`jquery.autocomplete` plugin are mapped and
can be passed to the widget. See
:class:`deform.widget.AutocompleteInputWidget` for details regarding the
available options. Passing options looks like:

.. code-block:: python

   form['nobsfrozz'].widget = AutocompleteInputWidget(
				values=['spam, 'eggs', 'bar', 'baz'],
                                min_length=1)

See `http://deformdemo.repoze.org/autocomplete_input/
<http://deformdemo.repoze.org/autocomplete_input/>`_ and
`http://deformdemo.repoze.org/autocomplete_remote_input/
<http://deformdemo.repoze.org/autocomplete_remote_input/>`_ for
working examples. A working example of a remote URL providing
completion data can be found at
`http://deformdemo.repoze.org/autocomplete_input_values/
<http://deformdemo.repoze.org/autocomplete_input_values/>`_.

Use of :class:`deform.widget.AutocompleteInputWidget` is not a
replacement for server-side validation of the field; it is purely a UI
affordance.  If the data must be checked at input time a separate
:term:`validator` should be attached to the related schema node.

Creating a New Schema Type
--------------------------

Sometimes the default schema types offered by Colander may not be sufficient
to model all the structures in your application.  

If this happens, refer to the Colander documentation on
:ref:`colander:defining_a_new_type`.
