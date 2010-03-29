API Documentation
=================

Widget-Related
--------------

.. automodule:: deform.widget

.. autoclass:: Widget
   :members:

.. autoclass:: TextInputWidget
   :members:

.. autoclass:: CheckboxWidget
   :members:

.. autoclass:: RadioChoiceWidget
   :members:

.. autoclass:: MappingWidget
   :members:

.. autoclass:: SequenceWidget
   :members:

.. autoclass:: Button
   :members:

.. autoclass:: FileUpload
   :members:

.. autoclass:: Form
   :members:

Exception-Related
-----------------

.. automodule:: deform.exception

.. autoclass:: ValidationFailure
   :members:

.. autoclass:: Invalid
   :members:

Type-Related
------------

.. automodule:: deform.schema

.. autoclass:: Mapping
   :members:

.. autoclass:: Sequence
   :members:

.. autoclass:: String
   :members:

.. autoclass:: Integer
   :members:

.. autoclass:: Float
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

Template-Related
----------------

.. automodule:: deform.template

.. autofunction:: make_renderer

.. attribute:: default_renderer

   The default ZPT template :term:`renderer` (uses the
   ``deform/templates/`` directory as a template source).

