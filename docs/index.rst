Deform
======

:mod:`deform` is a form generation library.  :mod:`deform` uses
:term:`Colander` as a schema library and :term:`Peppercorn` as a form
control deserialization library, and :term:`Chameleon` to perform HTML
templating.  :mod:`deform` depends only on Peppercorn, Colander,
Chameleon and an internationalization library named translationstring,
so it may be used in most web frameworks (or antiframeworks) as a
result.

Alternate templating languages may be used, as long as all templates
are translated from the native Chameleon templates to your templating
system of choice and a suitable :term:`renderer` is supplied to
:mod:`deform`.

The design of :mod:`deform` is heavily influenced by the `formish
<http://ish.io/projects/show/formish>`_ form generation library.  Some
might even say it's a shameless rip-off, which would not be
inaccurate.  It differs from formish mostly in ways that make the
implementation (arguably) simpler and smaller.

Example App
-----------

An example is worth a thousand words.  Here's an example `repoze.bfg
<http://bfg.repoze.org>`_ application demonstrating how one might use
:mod:`deform` to render a form.

.. warning:: :mod:`deform` is not dependent on :mod:`repoze.bfg` at
   all; we use BFG in the examples below to facilitate demonstration
   of an actual end-to-end working application that uses Deform.

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

Topics
======

.. toctree::
   :maxdepth: 2

   components.rst
   serialization.rst
   renderer.rst
   widget.rst
   api.rst
   glossary.rst

Thanks To
---------

- The Formish guys (http://ish.io)

- Fear Factory (http://fearfactory.com)

- Midlake (http://midlake.net)

Topics Needing Documentation
----------------------------

- Setting a widget on a field.

- Default values in schemas.

- The Form class (and thee Button class).

- Internationalization

- Creating a schema

- Templates

- form.css / structure.css / theme.css

- JS (deform.js / jquery...js / wufoo.js)

- Changing the close button image.

Demonstrations and Development
==============================

Demo Site
---------

Visit `deformdemo.repoze.org <http://deformdemo.repoze.org>`_ to view
an application which demonstrates most of Deform's features.  The
source code for this application is also available in the `deform
package within the Repoze SVN repository
<http://svn.repoze.org/deform/trunk/deformdemo>`_.

Development
-----------

You can check the deform package out of the Repoze SVN repository via
the following command::

   svn co http://svn.repoze.org/deform/trunk deform

Index and Glossary
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
