.. _retail:

Retail Form Rendering
=====================

.. contents:: :local:

Introduction
------------

In the previous chapter we demonstrated how to use Deform to render a complete
form, including the input fields, the buttons, and so forth.  We used the
:meth:`deform.Field.render()` method, and injected the resulting HTML snippet
into a larger HTML page in our application.  That is an effective and quick way
to put a form on a page, but sometimes you need more fine-grained control over
the way form HTML is rendered.  For example, you may need form elements to be
placed on the page side-by-side or you might need the form's styling to be
radically different than the form styling used by the default rendering of
Deform forms.  Often it's easier to use Deform slightly differently, where you
do more work yourself to draw the form within a template, and only use Deform
for some of its features.  We refer to this as "retail form rendering".

Live example
------------

`See pop-up example on Deform demo site <https://deformdemo.pylonsproject.org/popup/>`_.

`Source code <https://github.com/Pylons/deformdemo/blob/master/deformdemo/__init__.py>`_ (search popup).

A Basic Example
---------------

Our schema and form object:

.. code-block:: python
   :linenos:

   import colander

   class Person(colander.MappingSchema):
       name = colander.SchemaNode(colander.String())
       age = colander.SchemaNode(colander.Integer(),
                                 validator=colander.Range(0, 200))

   schema = Person()
   form = deform.Form(schema, resource_registry=resource_registry)

We feed the schema into a template as the ``form`` value.  It doesn't matter
what kind of templating system you use to do this, but this example will use
ZPT.  Below, the name ``form`` refers to the form we just created above:

.. code-block:: xml

     <div class="row"
          tal:repeat="field form">
         <div class="span2">
             ${structure:field.title}
             <span class="req" tal:condition="field.required">*</span>
         </div>
         <div class="span2">
             ${structure:field.serialize()}
         </div>
         <ul tal:condition="field.error">
             <li tal:repeat="error field.error.messages()">
                 ${structure:error}
             </li>
         </ul>
     </div>

The above template iterates over the fields in the form, using the attributes of
each field to draw the title.

You can use the ``__getitem__`` method of a form to grab named form fields
instead of iterating over all of its fields.  For example:

.. code-block:: xml

     <div tal:define="field form['name']">
         <div class="span2">
             ${structure:field.title}
             <span class="req" tal:condition="field.required">*</span>
         </div>
         <div class="span2">
             ${structure:field.serialize()}
         </div>
         <ul tal:condition="field.error">
             <li tal:repeat="error field.error.messages()">
                 ${structure:error}
             </li>
         </ul>
     </div>

You can use as little or as much of the Deform Field API to draw the widget as
you like.  The above examples use the :meth:`deform.Field.serialize` method,
which is an easy way to let Deform draw the field HTML, but you can draw it
yourself instead if you like, and just rely on the field object for its
validation errors (if any).  Note that the ``serialize`` method accepts
arbitrary keyword arguments that will be passed as top-level arguments to the
Deform widget templates, so if you need to change how a particular widget is
rendered without doing things completely by hand, you may want to take a look
at the existing widget template and see if your need has been anticipated.

In the POST handler for the form, just do things like we did in the last
chapter, except if validation fails, just re-render the template with the same
form object.

.. code-block:: python

       controls = request.POST.items() # get the form controls

       try:
           appstruct = form.validate(controls)  # call validate
       except ValidationFailure as e: # catch the exception
            # .. rerender the form .. its field's .error attributes
            # will be set

It is also possible to pass an ``appstruct`` argument to the
:class:`deform.Form` constructor to create "edit forms".  Form/field objects
are initialized with this appstruct (recursively) when they're created.  This
means that accessing ``form.cstruct`` will return the current set of rendering
values.  This value is reset during validation, so after a validation is done
you can re-render the form to show validation errors.

Note that existing Deform widgets are all built using "retail mode" APIs, so if
you need examples, you can look at their templates.

Other methods that might be useful during retail form rendering are:

- :meth:`deform.Field.__contains__`

- :meth:`deform.Field.start_mapping`

- :meth:`deform.Field.end_mapping`

- :meth:`deform.Field.start_sequence`

- :meth:`deform.Field.end_sequence`

- :meth:`deform.Field.start_rename`

- :meth:`deform.Field.end_rename`

- :meth:`deform.Field.set_appstruct`

- :meth:`deform.Field.set_pstruct`

- :meth:`deform.Field.render_template`

- :meth:`deform.Field.validate_pstruct` (and the ``subcontrol`` argument to
  :meth:`deform.Field.validate`)


