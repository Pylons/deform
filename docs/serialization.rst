Serialization and Deserialization
=================================

Serialization is the act of converting application data into a
form rendering.  Deserialization is the act of converting data
resulting from a form submission into application data.

Serialization
-------------

Serialization is what happens when you ask Deform to render a form
given a :term:`schema`.  Here's a high-level overview of what happens
when you ask Deform to do this:

- For each :term:`schema node` in the :term:`schema` provided by the
  application developer, Deform creates a :term:`field`.  This happens
  recursively for each node in the schema.  As a result, a tree of
  fields is created, mirroring the nodes in the schema.

- Each field object created as a result of the prior step knows about
  its associated schema node (it has a ``field.schema`` attribute);
  each field also knows about an associated :term:`widget` object (it
  has a ``field.widget`` attribute).  This widget object may be a
  default widget based on the schema node type or it might be
  overridden by the application developer for a particular rendering.

- Deform passes an :term:`appstruct` to the root schema node's
  ``serialize`` method to obtain a :term:`cstruct`.  The root schema
  node is responsible for consulting its children nodes during this
  process to serialilize the entirety of the data into a
  single :term:`cstruct`.

- Deform passes the resulting :term:`cstruct` to the root widget
  object's ``serialize`` method to generate an HTML form rendering.
  The root widget object is responsible for consulting its children
  nodes during this process to serialilize the entirety of the data
  into an HTML form.

If you were to attempt to produce a high-level overview diagram this
process, it might look like this:

.. code-block:: text

   appstruct -> cstruct -> form
              |          |
              v          v
           schema      widget

Peppercorn Structure Markers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You'll see the default deform widget "serializations" (form
renderings) make use of :term:`Peppercorn` *structure markers*.

Peppercorn is a library that is used by Deform; it allows Deform to
treat the :term:`form controls` in an HTML form submission as a
*stream* instead of a flat mapping of name to value.  To do so, it
uses hidden form elements to denote structure.

Peppercorn structure markers come in pairs which have a begin token
and an end token.  For example, a given form rendering might have a
part that looks like so:

.. code-block:: xml
   :linenos:

     <html>
      ...
       <input type="hidden" name="__start__" value="date:mapping"/>
       <input name="day"/>
       <input name="month"/>
       <input name="year"/>
       <input type="hidden" name="__end__"/>
      ...
     </html>
  
The above example shows an example of a pair of peppercorn structure
markers which begin and end a *mapping*.  The example uses this pair
to means that a the widget related to the *date* node in the schema
will be be passed a :term:`pstruct` that is a dictionary with multiple
values during deserialization: the dictionary will include the keys
``day`` , ``month``, and ``year``, and the values will be the values
provided by the person interacting with the related form controls.

Other uses of Peppercorn structure markers include: a "confirm
password" widget can render a peppercorn mapping with two text inputs
in it, a "mapping widget" can serve as a substructure for a fieldset.
Basically, Peppercorn makes it more pleasant to deal with form
submission data by pre-converting the data from a flat mapping into a
set of mappings, sequences, and strings during deserialization.

However, if a widget doesn't want to do anything fancy and a particular
widget is completely equivalent to one form control, it doesn't need
to use any Peppercorn structure markers in its rendering.

.. note:: See the `Peppercorn documentation
   <http://docs.pylonsproject.org/projects/peppercorn/dev/>`_ for more
   information about using peppercorn structure markers in HTML.
 
Deserialization
---------------

High-level overview of how "deserialization" (converting form control
data resulting from a form submission to application data) works:

- For each :term:`schema node` in the :term:`schema` provided by the
  application developer, Deform creates a :term:`field`.  This happens
  recursively for each node in the schema.  As a result, a tree of
  fields is created, mirroring the nodes in the schema.

- Each field object created as a result of the prior step knows about
  its associated schema node (it has a ``field.schema`` attribute);
  each field also knows about an associated :term:`widget` object (it
  has a ``field.widget`` attribute).  This widget object may be a
  default widget based on the schema node type or it might be
  overridden by the application developer for a particular rendering.

- Deform passes a set of :term:`form controls` to the ``parse`` method
  of :term:`Peppercorn` in order to obtain a :term:`pstruct`.

- Deform passes the resulting :term:`pstruct` to the root widget
  node's ``deserialize`` method in order to generate a
  :term:`cstruct`.

- Deform passes the resulting :term:`cstruct` to the root schema
  node's ``deserialize`` method to generate an :term:`appstruct`.
  This may result in a validation error.  If a validation error
  occurs, the form may be rerendered with error markers in place.

If you were to attempt to produce a high-level overview diagram this
process, it might look like this:

.. code-block:: text

   formcontrols -> pstruct -> cstruct -> appstruct
                |          |          |
                v          v          v
            peppercorn   widget    schema

When a user presses the submit button on any Deform form, Deform
itself runs the resulting :term:`form controls` through the
``peppercorn.parse`` method.  This converts the form data into a
mapping.  The *structure markers* in the form data indicate the
internal structure of the mapping.

For example, if the form submitted had the following data:

.. code-block:: xml
   :linenos:

     <html>
      ...
       <input type="hidden" name="__start__" value="date:mapping"/>
       <input name="day"/>
       <input name="month"/>
       <input name="year"/>
       <input type="hidden" name="__end__"/>
      ...
     </html>

There would be a ``date`` key in the root of the pstruct mapping which
held three keys: ``day``, ``month``, and ``year``.

.. note:: See the `Peppercorn documentation
   <http://docs.pylonsproject.org/projects/peppercorn/dev/>`_ for more
   information about the result of the ``peppercorn.parse`` method and how it
   relates to form control data.

The bits of code that are "closest" to the browser are called
"widgets".  A chapter about creating widgets exists in this
documentation at :ref:`writing_a_widget`.

A widget has a ``deserialize`` method.  The deserialize method is
passed a structure (a :term:`pstruct`) which is shorthand for
"Peppercorn structure".  A :term:`pstruct` might be a string, it might
be a mapping, or it might be a sequence, depending on the output of
``peppercorn.parse`` related to its schema node against the form
control data.

The job of the deserialize method of a widget is to convert the
pstruct it receives into a :term:`cstruct`.  A :term:`cstruct` is a
shorthand for "Colander structure".  It is often a string, a mapping
or a sequence.

An application eventually wants to deal in types less primitive than
strings: a model instance or a datetime object.  An :term:`appstruct`
is the data that an application that uses Deform eventually wants to
deal in.  Therefore, once a widget has turned a :term:`pstruct` into a
:term:`cstruct`, the :term:`schema node` related to that widget is
responsible for converting that cstruct to an :term:`appstruct`.  A
schema node possesses its very own ``deserialize`` method, which is
responsible for accepting a :term:`cstruct` and returning an
:term:`appstruct`.

Raising Errors During Deserialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a widget determines that a pstruct value cannot be converted
successfully to a cstruct value during deserialization, it may raise
an :exc:`colander.Invalid` exception.

When it raises this exception, it can use the field object as a
"scratchpad" to hold on to other data, but it must pass a ``value``
attribute to the exception constructor.  For example:

.. code-block:: python
   :linenos:

    import colander

    def serialize(self, field, cstruct, readonly=False):
        if cstruct is colander.null:
            cstruct = ''
        confirm = getattr(field, 'confirm', '')
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct,
                              confirm=confirm, subject=self.subject,
                              confirm_subject=self.confirm_subject,
                              )

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null
        value = pstruct.get('value') or ''
        confirm = pstruct.get('confirm') or ''
        field.confirm = confirm
        if value != confirm:
            raise Invalid(field.schema, self.mismatch_message, value)
        return value

The schema type associated with this widget is expecting a single
string as its cstruct.  The ``value`` passed to the exception
constructor raised during the ``deserialize`` when ``value !=
confirm`` is used as that ``cstruct`` value when the form is
rerendered with error markers.  The ``confirm`` value is picked off
the field value when the form is rerendered at this time.

Say What?
---------

Q: "So deform colander and peppercorn are pretty intertwingled?"

A: "Colander and Peppercorn are unrelated; Deform is effectively
    something that integrates colander and peppercorn together."

