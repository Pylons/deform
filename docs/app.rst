Example App
===========

An example is worth a thousand words.  Here's an example `repoze.bfg
<http://bfg.repoze.org>`_ application demonstrating how one might use
:mod:`deform` to render a form.

.. warning:: :mod:`deform` is not dependent on :mod:`repoze.bfg` at
   all; we use BFG in the examples below only to facilitate
   demonstration of an actual end-to-end working application that uses
   Deform.

Here's the Python code:

.. code-block:: python
   :linenos:

   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   from colander import MappingSchema
   from colander import SequenceSchema
   from colander import SchemaNode
   from colander import String
   from colander import Boolean
   from colander import Integer
   from colander import Length
   from colander import OneOf

   from deform import ValidationFailure
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
       title = SchemaNode(String(), validator=Length(max=20),
                          description=LONG_DESC)
       password = SchemaNode(String(), validator=Length(min=5))
       is_cool = SchemaNode(Boolean(), default=True)
       dates = DatesSchema()
       color = SchemaNode(String(), validator=OneOf(('red', 'blue')))

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

.. code-block:: xml
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
