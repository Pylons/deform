Basic Usage
===========

In this chapter, we'll walk through basic usage of Deform to render a
form, and capture and validate input.

The steps one must take to cause a form to be renderered and
subsequently be ready to accept form submission input are:

- Define a schema

- Create a form object.

- Assign non-default widgets to fields in the form (optional).

- Render the form.

Once the form is rendered, a user will interact with the form in his
browser, and some point, submit it.

When the user submits the form, the data provided by the user will
either validate properly, or the form will need to be rerendered with
error markers which help to inform the user of which parts need to be
filled in "properly" (as defined by the schema). 

Defining A Deform Schema
------------------------

The first step to using Deform is to create a :term:`schema` which
represents the data structure you wish to be captured via a form
rendering.

For example, let's imagine you want to create a form based roughly on
a data structure you'll obtain by reading data from a relational
database.  An example of such a data structure might look something
like this:

.. code-block:: python
   :linenos:

   [
   {
    'name':'keith',
    'age':20,
    'friends':['jim', 'bob', 'joe', 'fred'],
    'phones':[{'location':'home', 'number':'555-1212'},
              {'location':'work', 'number':'555-8989'},],
   },
   {
    'name':'fred',
    'age':23,
    'friends':['keith', 'bob', 'joe'],
    'phones':[{'location':'home', 'number':'555-7777'}],
   },
   ]

In other words, the database query we make returns a sequence of
*people*; each person is represented by some data.  We need to edit
this data.  There won't be many people in this list, so we don't need
any sort of paging or batching to make our way through the list; we
can display it all on one form page.

The name that Deform has a structure like the above is an
:term:`appstruct`.  The term "appstruct" is shorthand for "application
structure", because it's the kind of high-level structure that an
application usually cares about: the data present in an appstruct is
useful directly to an application itself.

.. note:: An appstruct differs from other structures that Deform uses
   (such as :term:`pstruct` and :term:`cstruct` structures): pstructs
   and cstructs are typically only useful during intermediate parts of
   the rendering process.

Usually, given some appstruct, you can divine a :term:`schema` that
would allow you to edit the data related to the appstruct.  Let's
define a schema which will attempt to serialize this particular
appstruct to a form.  Our application has these requirements of the
resulting form:

- It must be possible to add, edit and remove a person.

- It must be possible to, given a person, add, edit, or remove a
  location for that person.

Here's a schema that will help us meet those requirements:

.. code-block:: python
   :linenos:

   import colander

   class Phone(colander.MappingSchema):
       location = colander.SchemaNode(colander.String(), 
                                      validator=colander.OneOf(['home','work']))
       number = colander.SchemaNode(colander.String())

   class Friends(colander.SequenceSchema):
       friend = colander.SchemaNode(colander.String())

   class Phones(colander.SequenceSchema):
       phone = Phone()

   class Person(colander.MappingSchema):
       name = colander.SchemaNode(colander.String())
       age = colander.SchemaNode(colander.Int(),
                                 validator=colander.Range(0, 200))
       friends = Friends()
       phones = Phones()

   class People(colander.SequenceSchema):
       person = Person()

   schema = People()
       
For ease of reading, we've actually defined *five* schemas above, but
we coalesce them all into a single ``People`` schema instance as
``schema`` in the last step.  A ``People`` schema is a collection of
``Person`` schema nodes.  As the result of our definitions, a
``Person`` represents:

- A ``name``, which must be a string.

- An ``age``, which must be deserializable to an integer; after
  deserialization happens, a validator ensures that the integer is
  between 0 and 200 inclusive.

- A sequence of ``friend`` names, which are strings.

- A sequence of ``phone`` structures.  Each phone structure is a
  mapping.  Each phone mapping has two keys: ``location`` and
  ``number``.  The ``location`` must be one of ``work`` or ``home``.
  The number must be a string.

.. note:: schema-related objects are usually imported from the
   :mod:`colander` package.  The canonical documentation for Colander
   exists at `http://docs.repoze.org/colander
   <http://docs.repoze.org/colander>`_.  Deform is a consumer of the
   schema services offered by Colander.

Schema Node Objects
~~~~~~~~~~~~~~~~~~~

A schema is composed of one or more *schema node* objects, each
typically of the class :class:`colander.SchemaNode`, usually in a nested
arrangement.  Each schema node object has a required *type*, an
optional *validator*, an optional *default*, an optional *title*, an
optional *description*, and a slightly less optional *name*.

The *type* of a schema node indicates its data type (such as
:class:`colander.Int` or :class:`colander.String`).

The *validator* of a schema node is called after deserialization; it
makes sure the deserialized value matches a constraint.  An example of
such a validator is provided in the schema above:
``validator=colander.Range(0, 200)``.  A validator is not called after
serialization, only after deserialization.

The *default* of a schema node indicates its default value if a value
for the schema node is not found in the input data during
serialization.  It should be the *deserialized* representation.  If a
schema node does not have a default, it is considered a required
schema node.

The *name* of a schema node is used to relate schema nodes to each
other.  It is also used as the title if a title is not provided.

The *title* of a schema node is metadata about a schema node.  It
shows up as the legend above the form field(s) related to the schema
node.  By default, it is a capitalization of the *name*.

The *description* of a schema node is metadata about a schema node.
It shows up as a tooltip when someone hovers over one a form field.
By default, it is empty.

The name of a schema node that is introduced as a class-level
attribute of a :class:`colander.MappingSchema`,
:class:`colander.TupleSchema` or a :class:`colander.SequenceSchema` is
its class attribute name.  For example:

.. code-block:: python
   :linenos:

   import colander

   class Phone(colander.MappingSchema):
       location = colander.SchemaNode(colander.String(), 
                                      validator=colander.OneOf(['home','work']))
       number = colander.SchemaNode(colander.String())

The name of the schema node defined via ``location =
colander.SchemaNode(..)`` within the schema above is ``location``.
The title of the same schema node is ``Location``.

Schema Objects
~~~~~~~~~~~~~~

In the examples above, if you've been paying attention, you'll have
noticed that we're defining classes which subclass from
:class:`colander.MappingSchema`, and :class:`colander.SequenceSchema`.

It's turtles all the way down: the result of creating an instance of
any of :class:`colander.MappingSchema`, :class:`colander.TupleSchema` or
:class:`colander.SequenceSchema` object is *also* a
:class:`colander.SchemaNode` object.

Instantiating a :class:`colander.MappingSchema` creates a schema node
which has a *type* value of :class:`colander.Mapping`.

Instantiating a :class:`colander.TupleSchema` creates a schema node
which has a *type* value of :class:`colander.Tuple`.

Instantiating a :class:`colander.SequenceSchema` creates a schema node
which has a *type* value of :class:`colander.Sequence`.

Deserializing A Data Structure Using a Schema
---------------------------------------------

Earlier we defined a schema:

.. code-block:: python
   :linenos:

.. code-block:: python
   :linenos:

   import colander

   class Phone(colander.MappingSchema):
       location = colander.SchemaNode(colander.String(), 
                                      validator=colander.OneOf(['home','work']))
       number = colander.SchemaNode(colander.String())

   class Friends(colander.SequenceSchema):
       friend = colander.SchemaNode(colander.String())

   class Phones(colander.SequenceSchema):
       phone = Phone()

   class Person(colander.MappingSchema):
       name = colander.SchemaNode(colander.String())
       age = colander.SchemaNode(colander.Int(),
                                 validator=colander.Range(0, 200))
       friends = Friends()
       phones = Phones()

   class People(colander.SequenceSchema):
       person = Person()

   schema = People()

Let's now use this schema to try to deserialize some concrete data
structures to HTML.

Deserializing A Valid Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
   :linenos:

     data = {
            'name':'keith',
            'age':'20',
            'friends':[('1', 'jim'),('2', 'bob'), ('3', 'joe'), ('4', 'fred')],
            'phones':[{'location':'home', 'number':'555-1212'},
                      {'location':'work', 'number':'555-8989'},],
            }
     schema = Person()
     deserialized = schema.deserialize(data)

When ``schema.deserialize(data)`` is called, because all the data in
the schema is valid, and the structure represented by ``data``
conforms to the schema, ``deserialized`` will be the following:

.. code-block:: python
   :linenos:

     {
     'name':'keith',
     'age':20,
     'friends':[(1, 'jim'),(2, 'bob'), (3, 'joe'), (4, 'fred')],
     'phones':[{'location':'home', 'number':'555-1212'},
               {'location':'work', 'number':'555-8989'},],
     }

Note that all the friend rankings have been converted to integers,
likewise for the age.

Deserializing An Invalid Serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below, the ``data`` structure has some problems.  The ``age`` is a
negative number.  The rank for ``bob`` is ``t`` which is not a valid
integer.  The ``location`` of the first phone is ``bar``, which is not
a valid location (it is not one of "work" or "home").  What happens
when a data structure cannot be deserialized due to a data type error
or a validation error?

.. code-block:: python
   :linenos:

     import colander

     data = {
            'name':'keith',
            'age':'-1',
            'friends':[('1', 'jim'),('t', 'bob'), ('3', 'joe'), ('4', 'fred')],
            'phones':[{'location':'bar', 'number':'555-1212'},
                      {'location':'work', 'number':'555-8989'},],
            }
     schema = Person()
     schema.deserialize(data)

The ``deserialize`` method will raise an exception, and the ``except``
clause above will be invoked, causing an error messaage to be printed.
It will print something like:

.. code-block:: python
   :linenos:

   Invalid: {'age':'-1 is less than minimum value 0',
            'friends.1.0':'"t" is not a number',
            'phones.0.location:'"bar" is not one of "home", "work"'}

The above error is telling us that:

- The top-level age variable failed validation.

- Bob's rank (the Friend tuple name ``bob``'s zeroth element) is not a
  valid number.

- The zeroth phone number has a bad location: it should be one of
  "home" or "work".

We can optionally catch the exception raised and obtain the raw error
dictionary:

.. code-block:: python
   :linenos:

     import colander

     data = {
            'name':'keith',
            'age':'-1',
            'friends':[('1', 'jim'),('t', 'bob'), ('3', 'joe'), ('4', 'fred')],
            'phones':[{'location':'bar', 'number':'555-1212'},
                      {'location':'work', 'number':'555-8989'},],
            }
     schema = Person()
     try:
         schema.deserialize(data)
     except colander.Invalid, e:
         errors = e.asdict()
         print errors

This will print something like:

.. code-block:: python
   :linenos:

   {'age':'-1 is less than minimum value 0',
    'friends.1.0':'"t" is not a number',
    'phones.0.location:'"bar" is not one of "home", "work"'}
