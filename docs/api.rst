API Documentation
=================

Form-Related
------------

.. automodule:: deform

.. autoclass:: Field
   :members:

   .. automethod:: __getitem__

   .. automethod:: __iter__

   .. automethod:: translate

.. autoclass:: Form
   :members:

.. autoclass:: Button
   :members:

Type-Related
------------

.. autoclass:: Set
   :members:

.. autoclass:: FileData
   :members:

See also the type- and schema-related documentation in :term:`Colander`.

Exception-Related
-----------------

.. autoclass:: ValidationFailure
   :members:


.. autoclass:: TemplateError
   :members:

See also the exception-related documentation in :term:`Colander`.

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

.. autoclass:: AutocompleteInputWidget
   :members:

.. autoclass:: HiddenWidget
   :members:

.. autoclass:: TextAreaWidget
   :members:

.. autoclass:: RichTextWidget
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

.. autoclass:: DateInputWidget
   :members:

.. autoclass:: DateTimeInputWidget
   :members:

.. autoclass:: DatePartsWidget
   :members:

.. autoclass:: FormWidget
   :members:

.. autoclass:: TextAreaCSVWidget
   :members:

.. autoclass:: TextInputCSVWidget
   :members:

.. autoclass:: ResourceRegistry
   :members:

   .. automethod:: __call__

.. attribute:: default_resource_registry

   The default :term:`resource registry` (maps Deform-internal
   :term:`widget requirement` strings to resource paths).  This
   resource registry is used by forms which do not specify their own
   as a constructor argument, unless
   :meth:`deform.Field.set_default_resource_registry` is used to
   change the default resource registry.
