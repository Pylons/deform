Deform Components
=================

A developer dealing with Deform has to understand a few fundamental
types of objects and their relationships to one another.  These types
are:

- schema nodes

- field objects

- widgets

The Relationship Between Widgets, Fields, and Schema Objects
------------------------------------------------------------

The relationship between widgets, fields, and schema node objects is
as follows:

- A schema is created by a developer.  It is a collection of
  :term:`schema node` objects.

- When a root schema node is passed to the :class:`deform.Form`
  constructor, the result is a :term:`field` object.  For each node
  defined by the developer in the schema recursively, a corresponding
  :term:`field` is created.

- Each field in the resulting field tree has a default widget type.
  If the ``widget`` attribute of a field object is not set directly by
  the developer, a property is used to create an instance of the
  default widget type when ``field.widget`` is first requested.  Sane
  defaults for each schema type typically exist; if a sane default
  cannot be found, the :class:`deform.widget.TextInputWidget` widget
  is used.

.. note::

   The `Colander documentation
   <http://docs.pylonsproject.org/projects/colander/dev/>`_ is a resource
   useful to Deform developers.  In particular, it details how a
   :term:`schema` is created and used.  Deform schemas are Colander schemas.
   The Colander documentation about how they work applies to creating Deform
   schemas as well.

A widget is related to one or more :term:`schema node` type objects.
For example, a notional "TextInputWidget" may be responsible for
serializing textual data related to a schema node which has
:class:`colander.String` as its type into a text input control, while
a notional "MappingWidget" might be responsible for serializing a
:class:`colander.Mapping` object into a sequence of controls.  In both
cases, the data type being serialized is related to the schema node
type to which the widget is related.

A widget has a relationship to a schema node via a :term:`field`
object.  A :term:`field` object has a reference to both a widget and a
:term:`schema node`.  These relationships look like this::

   field object (``field``)
        |
        |
        |----- widget object  (``field.widget``)
        |
        |
        \----- schema node object (``field.schema``)

