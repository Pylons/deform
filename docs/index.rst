Deform
======

:mod:`deform` is a form generation library.  Uses :term:`Colander` as
a schema library and :term:`Peppercorn` as a form control
deserialization library, and :term:`Chameleon` to perform HTML
templating.  :mod:`deform` depends only on Peppercorn, Colander and
Chameleon so it may be used in most web frameworks (or antiframeworks)
as a result.

Alternate templating languages may be used, as long as all templates
are translated from the native Chameleon templates to your templating
system of choice and a :term:`renderer` is supplied to :mod:`deform`.

The design of :mod:`deform` is a shameless rip-off of the `formish
<http://ish.io/projects/show/formish>`_ form generation library.  It
differs from formish mostly in ways that make it possible to use
:term:`Peppercorn` to ease sequence and form deserialization
operations.

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

Example App
-----------

Here's an example `repoze.bfg <http://bfg.repoze.org>`_ application
demonstrating how one might use :mod:`deform` to render a form.

Here's the Python code:

.. code-block:: python
   :linenos:

   import colander

   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   from deform import ValidationFailure
   from deform import MappingSchema
   from deform import SequenceSchema
   from deform import SchemaNode
   from deform import String
   from deform import Boolean
   from deform import Integer
   from deform import Form

   from deform import widget

   class DateSchema(MappingSchema):
       month = SchemaNode(Integer())
       year = SchemaNode(Integer())
       day = SchemaNode(Integer())

   class DatesSchema(SequenceSchema):
       date = DateSchema()

   class MySchema(MappingSchema):
       name = SchemaNode(String(), description=LONG_DESC)
       title = SchemaNode(String(), validator=colander.Length(max=20),
                          description=LONG_DESC)
       password = SchemaNode(String(), validator=colander.Length(min=5))
       is_cool = SchemaNode(Boolean(), default=True)
       dates = DatesSchema()
       color = SchemaNode(String(), validator=colander.OneOf(('red', 'blue')))

   def form_view(request):
       schema = MySchema()
       myform = Form(schema, buttons=('submit',))

       myform['password'].widget = widget.CheckedPasswordWidget()
       myform['title'].widget = widget.TextInputWidget(size=40)
       myform['color'].widget = widget.RadioChoiceWidget(
           values=(('red', 'Red'),('green', 'Green'),('blue', 'Blue')))

       if 'submit' in request.POST:
           controls = request.POST.items()
           try:
               myform.validate(controls)
           except ValidationFailure, e:
               return {'form':e.render()}
           return {'form':'OK'}
               
       return {'form':myform.render()}

   if __name__ == '__main__':
       settings = dict(reload_templates=True)
       config = Configurator(settings=settings)
       config.begin()
       config.add_view(form_view, renderer='form.pt')
       config.add_static_view('static', 'deform:static')
       config.end()
       app = config.make_wsgi_app()
       serve(app)

Here's the Chameleon ZPT template named ``form.pt``, placed in the
same directory:

.. code-block:: python
   :linenos:

   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
   <html xmlns="http://www.w3.org/1999/xhtml">
   <head>
   <title>
     Deform Sample Form App
   </title>
   <!-- Meta Tags -->
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
   <!-- JavaScript -->
   <script type="text/javascript" src="static/scripts/wufoo.js"></script>
   <script type="text/javascript" src="static/scripts/deform.js"></script>
   <!-- CSS -->
   <link rel="stylesheet" href="static/css/form.css" type="text/css" />
   <link rel="stylesheet" href="static/css/theme.css" type="text/css" />
   </head>
   <body id="public">
   <div id="container">
   <h1>Sample Form</h1>
   <span tal:replace="structure form"/>
   </div>
   </body>
   </html>

.. toctree::
   :maxdepth: 2

   api.rst
   glossary.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
