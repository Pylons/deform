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
`https://deformdemo.pylonsproject.org <https://deformdemo.pylonsproject.org>`_
demonstration website:

- `Redirection on validation success
  <https://deformdemo.pylonsproject.org/ajaxform_redirect/>`_

- `No redirection on validation success
  <https://deformdemo.pylonsproject.org/ajaxform/>`_

.. note::

   As with widgets, you must ensure the required JavaScript
   files are included for the AJAX functionality to work.  See
   :ref:`widget_requirements` for a way to detect which JavaScript
   libraries are required for a particular form rendering.


