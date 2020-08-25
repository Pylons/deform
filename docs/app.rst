Example App
===========

An example is worth a thousand words.  Here's an example `Pyramid
<https://trypyramid.com>`_ application demonstrating how one might use
:mod:`deform` to render a form.  For it to work you'll need to have
``deform``, ``pyramid``, and ``pyramid_chameleon`` installed in your
python environment.

.. warning::

   :mod:`deform` is not dependent on :mod:`pyramid` at all; we use
   Pyramid in the examples below only to facilitate demonstration of
   an actual end-to-end working application that uses Deform.

Here's the Python code:

.. code-block:: python
   :linenos:

   import os

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator

   from colander import (
       Boolean,
       Integer,
       Length,
       MappingSchema,
       OneOf,
       SchemaNode,
       SequenceSchema,
       String
   )

   from deform import (
       Form,
       ValidationFailure,
       widget
   )


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
       template_values = {}
       template_values.update(myform.get_widget_resources())

       if 'submit' in request.POST:
           controls = request.POST.items()
           try:
               myform.validate(controls)
           except ValidationFailure as e:
               template_values['form'] = e.render()
           else:
               template_values['form'] = 'OK'
           return template_values

       template_values['form'] = myform.render()
       return template_values

   if __name__ == '__main__':
       settings = dict(reload_templates=True)
       config = Configurator(settings=settings)
       config.include('pyramid_chameleon')
       config.add_view(form_view, renderer=os.path.join(here, 'form.pt'))
       config.add_static_view('static', 'deform:static')
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

Here's the Chameleon ZPT template named ``form.pt``, placed in the
same directory:

.. code-block:: html
   :linenos:

   <!doctype html>
   <html>
     <head>
       <meta charset="utf-8">
       <title>Deform Sample Form App</title>
       <meta name="viewport" content="width=device-width, initial-scale=1">

       <!-- JavaScript -->
       <script src="static/scripts/jquery-2.0.3.min.js"></script>
       <script src="static/scripts/bootstrap.min.js"></script>
       <tal:loop tal:repeat="js_resource js">
         <script src="${request.static_path(js_resource)}"></script>
       </tal:loop>

       <!-- CSS -->
       <link rel="stylesheet" href="static/css/bootstrap.min.css"
             type="text/css">
       <link rel="stylesheet" href="static/css/form.css" type="text/css">
       <tal:loop tal:repeat="css_resource css">
         <link rel="stylesheet" href="${request.static_path(css_resource)}"
               type="text/css">
       </tal:loop>

     </head>
     <body>
       <div class="container">
         <div class="row">
           <div class="col-md-12">
             <h1>Sample Form</h1>
             <span tal:replace="structure form"/>
           </div>
         </div>
       </div>
     </body>
   </html>
