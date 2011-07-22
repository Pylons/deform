Example App
===========

An example is worth a thousand words.  Here's an example `Pyramid
<http://pylonsproject.org>`_ application demonstrating how one might use
:mod:`deform` to render a form.

.. warning::

   :mod:`deform` is not dependent on :mod:`pyramid` at all; we use Pyramid in
   the examples below only to facilitate demonstration of an actual
   end-to-end working application that uses Deform.

Here's the Python code:

.. code-block:: python
   :linenos:

   import os

   from paste.httpserver import serve
   from pyramid.config import Configurator

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


   here = os.path.dirname(os.path.abspath(__file__))
   
   colors = (('red', 'Red'), ('green', 'Green'), ('blue', 'Blue'))

   class DateSchema(MappingSchema):
       month = SchemaNode(Integer())
       year = SchemaNode(Integer())
       day = SchemaNode(Integer())

   class DatesSchema(SequenceSchema):
       date = DateSchema()

   class MySchema(MappingSchema):
       name = SchemaNode(String(),
                         description = 'The name of this thing')
       title = SchemaNode(String(),
                          widget = widget.TextInputWidget(size=40),
                          validator = Length(max=20),
                          description = 'A very short title')
       password = SchemaNode(String(),
                             widget = widget.CheckedPasswordWidget(),
                             validator = Length(min=5))
       is_cool = SchemaNode(Boolean(),
                            default = True)
       dates = DatesSchema()
       color = SchemaNode(String(),
                          widget = widget.RadioChoiceWidget(values=colors),
                          validator = OneOf(('red', 'blue')))

   def form_view(request):
       schema = MySchema()
       myform = Form(schema, buttons=('submit',))

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
       config.add_view(form_view, renderer=os.path.join(here, 'form.pt'))
       config.add_static_view('static', 'deform:static')
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
   <script type="text/javascript" src="static/scripts/deform.js"></script>
   <!-- CSS -->
   <link rel="stylesheet" href="static/css/form.css" type="text/css" />
   </head>
   <body id="public">
   <div id="container">
   <h1>Sample Form</h1>
   <span tal:replace="structure form"/>
   </div>
   </body>
   </html>
