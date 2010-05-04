API Documentation
=================

Form-Related
------------

.. automodule:: deform

.. autoclass:: Field
   :members:

.. autoclass:: Form
   :members:

.. autoclass:: Button
   :members:

Type-Related
------------

.. autoclass:: Mapping
   :members:

.. autoclass:: Sequence
   :members:

.. autoclass:: Tuple
   :members:

.. autoclass:: Set
   :members:

.. autoclass:: String
   :members:

.. autoclass:: Integer
   :members:

.. autoclass:: Float
   :members:

.. autoclass:: Decimal
   :members:

.. autoclass:: Boolean
   :members:

.. autoclass:: FileData
   :members:

Schema-Related
--------------

.. autoclass:: SchemaNode
   :members:

.. autoclass:: Schema
   :members:

.. autoclass:: MappingSchema
   :members:

.. autoclass:: SequenceSchema
   :members:

.. autoclass:: TupleSchema
   :members:

Exception-Related
-----------------

.. autoclass:: ValidationFailure
   :members:

.. autoclass:: Invalid
   :members:

   .. attribute:: parent

      A reference to the parent exception.

   .. attribute:: pos

      An integer representing the position of this exception's
      schema node relative to all other child nodes of this
      exception's parent schema node.  For example, if this
      exception is related to the third child node of its parent's
      schema, ``pos`` might be the integer ``3``.  ``pos`` may also
      be ``None``, in which case this exception is the root
      exception.

   .. attribute:: children

      A list of child exceptions.  Each element in this list (if
      any) will also be an :exc:`deform.Invalid` exception,
      recursively, representing the error circumstances for a
      particular schema deserialization.

   .. attribute:: msg

     A ``str`` or ``unicode`` object, or a *translation string*
     instance representing a freeform error value set by a
     particular type during an unsuccessful deserialization.  If
     this exception is only structural (only exists to be a parent
     to some inner child exception), this value will be ``None``.

   .. attribute:: node

     The schema node to which this exception relates.

   .. attribute:: value

     The value of a field when a widget raises this exception.

.. autoclass:: TemplateError
   :members:

Template-Related
----------------

.. autoclass:: ZPTRendererFactory

.. attribute:: default_renderer

   The default ZPT template :term:`renderer` (uses the
   ``deform/templates/`` directory as a template source).

Widget-Related
--------------

.. automodule:: deform.widget

.. autoclass:: Widget
   :members:

.. autoclass:: TextInputWidget
   :members:

.. autoclass:: HiddenWidget
   :members:

.. autoclass:: TextAreaWidget
   :members:

.. autoclass:: CheckboxWidget
   :members:

.. autoclass:: CheckedInputWidget
   :members:

.. autoclass:: CheckedPasswordWidget
   :members:

.. autoclass:: CheckboxChoiceWidget
   :members:

.. autoclass:: SelectWidget
   :members:

.. autoclass:: RadioChoiceWidget
   :members:

.. autoclass:: MappingWidget
   :members:

.. autoclass:: SequenceWidget
   :members:

.. autoclass:: FileUploadWidget
   :members:

.. autoclass:: DatePartsWidget
   :members:

.. autoclass:: FormWidget
   :members:

.. autoclass:: TextAreaCSVWidget
   :members:

