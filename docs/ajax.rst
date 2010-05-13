Using Ajax Forms
================

To create a form object that uses AJAX, we do this:

.. code-block:: python
   :linenos:

   from deform import Form
   myform = Form(schema, buttons=('submit',), use_ajax=True)

:ref:`creating_a_form` indicates how to create a Form object based on
a schema and some buttons.  Creating an AJAX form uses the same
constructor as creating a non-AJAX form: the only difference between
the example provided in the :ref:`creating_a_form` section and the
example above of creating an AJAX form is the additional
``use_ajax=True`` argument passed to the Form constructor.

If ``use_ajax`` is passed as ``True`` to the constructor of a
:class:`deform.Form` object, the form page is rendered in such a way
that when a submit button is pressed, the page is not reloaded.
Instead, the form is posted, and the result of the post replaces the
form element's DOM node.

Examples of using the AJAX facilities in Deform are showcased on the
`http://deformdemo.repoze.org <http://deformdemo.repoze.org>`_
demonstration website:

- `Redirection on validation success
  <http://deformdemo.repoze.org/ajaxform/>`_

- `No redirection on validation success
  <http://deformdemo.repoze.org/ajaxform/>`_

Note that for AJAX forms to work, the ``jquery.form.js`` library must
be included in the rendering of the page that includes the form
itself.  This is the responsibility of the wrapping page; Deform does
not help here.  This library is present in the ``static`` directory of
the :mod:`deform` package itself.

