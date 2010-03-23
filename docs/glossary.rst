.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   renderer
     A callable with the signature ``(template_name, **kw)`` which is
     capable of rendering a template for use in a deform widget.

   cstruct
     Data serialized by :term:`Colander` to a representation suitable
     for consumption by a deform serializer.

   pstruct
     Data deserialized by :term:`Peppercorn` to a representation
     suitable for consumption by a deform deserializer.

   Colander
     A `schema package <http://docs.repoze.org/colander>`_ used by deform
     to provide serialization and validation facilities.

   Peppercorn
     A `package <http://docs.repoze.org/peppercorn>`_ used by deform
     for strutured form submission value deserialization.
