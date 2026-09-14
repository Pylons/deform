Using Ajax Forms
================

To create a form object that uses AJAX, pass ``use_ajax=True`` to the
:class:`deform.Form` constructor:

.. code-block:: python

    from deform import Form
    myform = Form(schema, buttons=('submit',), use_ajax=True)

:ref:`creating_a_form` shows how to create a Form based on a schema and some
buttons. An AJAX form uses the same constructor as a non-AJAX form; the only
difference is the additional ``use_ajax=True`` argument.

.. versionchanged:: 4.0

   AJAX form submission now uses vanilla JavaScript (``fetch()``) instead of
   the old ``jquery.form`` plugin. Deform no longer depends on jQuery.

How it works
------------

When ``use_ajax`` is ``True``, the ``<form>`` element is rendered with a
``data-deform-ajax="true"`` attribute. The ``deform.js`` library intercepts
the submit event, POSTs the form via ``fetch()``, and swaps the form element
with the response (``outerHTML``).

The ``deform.js`` library is included in the form's widget resources
automatically, so make sure your page emits the JavaScript returned by
:meth:`deform.field.Field.get_widget_resources` (see
:ref:`widget_requirements`).

Server response contract
------------------------

Your view should detect the AJAX request (the ``X-Requested-With:
XMLHttpRequest`` header) and return only the rendered form fragment:

- **Validation failure:** return the re-rendered form with HTTP status **422**.
- **Success:** return your success markup with status **200**; it replaces the
  form.
- **Redirect on success:** send the ``X-Redirect`` response header with the
  destination URL to trigger a client-side redirect.

.. note::

   The ``ajax_options`` argument is deprecated as of 4.0 and has no effect.
