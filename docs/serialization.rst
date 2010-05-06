Serialization and Deserialization
=================================

Serialization is the act of converting application data to a form
rendering.  Deserialization is the act of converting :term:`form
controls` data resulting from a form submission into application data.

Serialization
-------------

High-level overview of how "serialization" (converting application
data to a form rendering) works:

- For each structure in the :term:`schema`, create a :term:`field`.  A
  tree of fields is created, mirroring the nodes in the schema.

- Each field knows about its associated schema element; each field
  also knows about a :term:`widget`.

- Pass an :term:`appstruct` to the root schema node's ``serialize``
  method to obtain a :term:`cstruct`.

- Pass the resulting :term:`cstruct` to the root widget's
  ``serialize`` method to generate a form.

.. code-block:: text

   appstruct -> cstruct -> form
              |          |
              v          v
           schema      widget
 
Deserialization
---------------

High-level overview of how "deserialization" (converting form control
data resulting from a form submission to application data) works:

- For each structure in the :term:`schema`, create a :term:`field`.

- Each field knows about its associated schema element; each field
  also knows about a :term:`widget`.

- Pass a set of :term:`form controls` to :term:`Peppercorn` in order
  to obtain a :term:`pstruct`.

- Pass the resulting :term:`pstruct` to the root widget node's
  ``deserialize`` method to generate a :term:`cstruct`.

- Pass the resulting :term:`cstruct` to the root schema node's
  ``deserialize`` method to generate an :term:`appstruct`.  This may
  result in a validation error.  If a validation error occurs, the
  form may be rerendered with error markers in place.

.. code-block:: text

   formcontrols -> pstruct -> cstruct -> appstruct
                |          |          |
                v          v          v
            peppercorn   widget    schema

