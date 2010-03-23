Deform
======

Another form generation library.  Uses :mod:`Colander` as a schema
library and :mod:`Peppercorn` as a form post deserialization library.

Definitions
-----------

Application Domain Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

appstruct
   the raw application data structure (complex Python objects)

cstruct
   a set of mappings, sequences, and strings (colander serialization)

schema
   can serialize an appstruct to a cstruct and deserialize a cstruct
   to an appstruct (object derived from :class:`colander.SchemaNode`
   or one of the colander Schema classes).

Widget Domain Definitions
~~~~~~~~~~~~~~~~~~~~~~~~~

form fields
    a sequence of form fields (e.g. the rfc 2388 def of "field")

pstruct
    the data deserialized by :term:`Peppercorn` from a set of form fields.

widget
    serializes a cstruct to a form and deserializes a pstruct to
    a cstruct

Serialization and Deserialization
---------------------------------

Serialization
~~~~~~~~~~~~~

- For each structure in the schema, create a widget node.

- Pass a cstruct to the root widget node's ``serialize`` method to
  generate a form

.. code-block:: text

   appstruct -> cstruct -> form
              |          |
              v          v
           schema      widget
 
Deserialization
~~~~~~~~~~~~~~~

- For each structure in the schema, create a widget node.

- Pass a pstruct to the root widget node's ``deserialize`` method to
  generate a cstruct.

.. code-block:: text


   formfields -> pstruct -> cstruct -> appstruct
              |          |          |
              v          v          v
          peppercorn   widget    schema

.. toctree::
   :maxdepth: 2

   api.rst
   glossary.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
