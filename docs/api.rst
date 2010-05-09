API Documentation
=================

Form-Related
------------

.. automodule:: deform

.. autoclass:: Field
   :members:

   .. automethod:: __getitem__

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

