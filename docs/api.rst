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

.. autoclass:: TemplateError
   :members:

Internationalization (i18n) -Related
------------------------------------

.. autoclass:: MessageFactory

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

.. autoclass:: SingleSelectWidget
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

Template-Related
----------------

.. autoclass:: ZPTRendererFactory

.. attribute:: default_renderer

   The default ZPT template :term:`renderer` (uses the
   ``deform/templates/`` directory as a template source).

