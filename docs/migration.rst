.. _migration_3_to_4:

Migrating from Deform 3.x to 4.0
================================

Deform 4.0 is a major, breaking release. **All jQuery dependencies have been
removed** and replaced with modern, maintained, framework-agnostic libraries.

For most applications the Python-facing API (schemas, widgets, and the
:class:`deform.Form` constructor) is unchanged, so upgrading is mostly a matter
of updating the static assets your page loads. This document lists everything
you need to check.

Overview of what changed
------------------------

- jQuery, ``jquery.form``, ``jquery-sortable``, ``jquery.maskedinput`` and
  ``jquery.maskMoney`` are **no longer bundled or required**. ``deform.js`` is
  now plain, dependency-free JavaScript.
- AJAX forms (``use_ajax=True``) now use **vanilla JavaScript** (``fetch()``)
  instead of ``jquery.form``.
- The ``boost`` argument is deprecated and now a no-op; passing it to
  :class:`deform.Form` emits a ``DeprecationWarning`` and has no effect.
- Widget JavaScript libraries were replaced (see
  :ref:`migration_library_table`).

.. _migration_library_table:

Library replacements
--------------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Feature / widget
     - Old (jQuery)
     - New (jQuery-free)
   * - ``Select2Widget`` / ``SelectizeWidget``
     - select2 / selectize.js *(archived)*
     - `Tom Select <https://tom-select.js.org/>`_ (Apache-2.0)
   * - ``AutocompleteInputWidget``
     - typeahead.js / jQuery UI autocomplete
     - `Tom Select <https://tom-select.js.org/>`_ (Apache-2.0)
   * - Text / checked input masks
     - ``jquery.maskedinput``
     - `IMask <https://imask.js.org/>`_ (MIT)
   * - ``MoneyInputWidget``
     - ``jquery.maskMoney``
     - `IMask <https://imask.js.org/>`_ (MIT)
   * - Date / time / datetime pickers
     - pickadate + Modernizr
     - `flatpickr <https://flatpickr.js.org/>`_ (MIT)
   * - Orderable ``SequenceWidget`` drag-and-drop
     - jquery-sortable
     - `SortableJS <https://sortablejs.github.io/Sortable/>`_ (MIT)
   * - ``RichTextWidget``
     - TinyMCE + jQuery glue
     - TinyMCE (jQuery glue removed)
   * - AJAX form submission
     - ``jquery.form`` ``ajaxForm``
     - Vanilla JS (``fetch()``) in ``deform.js``

What you must change
--------------------

Static assets in your page template
+++++++++++++++++++++++++++++++++++

- **Remove the jQuery ``<script>`` tag.** Deform no longer ships or needs
  jQuery. If your own application code still needs jQuery, load it yourself.
- ``deform.js`` no longer depends on jQuery, so the previous "load jQuery
  first" ordering requirement is gone.
- Continue to render the per-form JavaScript and CSS returned by
  :meth:`deform.field.Field.get_widget_resources` (the ``js`` and ``css``
  lists). See :ref:`widget_requirements`.

AJAX form responses (only if you use ``use_ajax=True``)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

The AJAX server contract changed:

- On **validation failure**, return the rendered form fragment with **HTTP
  status 422**.
- On **success**, return your success fragment with status 200 — it replaces
  the form (the form element is swapped via ``outerHTML``).
- To **redirect on success**, send the ``X-Redirect`` response header with
  the target URL.

The ``ajax_options`` argument
+++++++++++++++++++++++++++++

``Form(ajax_options=...)`` is **deprecated and now a no-op**. Passing a
non-empty value emits a ``DeprecationWarning``.

The ``boost`` argument
++++++++++++++++++++++

``Form(boost=True)`` is **deprecated and now a no-op**. Passing ``boost=True``
to :class:`deform.Form` emits a ``DeprecationWarning`` and has no effect.

Custom resource registries and widget requirements
+++++++++++++++++++++++++++++++++++++++++++++++++++

The logical requirement names in the default
:term:`resource registry` changed. The old keys ``jquery.form``,
``jquery.maskedinput``, ``jquery.maskMoney``, ``modernizr``, ``typeahead`` and
``pickadate`` **no longer exist**. The current keys are:

``deform``, ``sortable``, ``tom-select``, ``imask``, ``flatpickr``
(plus the existing ``tinymce``).

If you built a custom ``ResourceRegistry`` or set a custom ``requirements``
tuple on a widget referencing the old names, update them to the new ones.

Custom CSS and functional tests
++++++++++++++++++++++++++++++++++++++++++++++++

The markup and CSS classes emitted by the select, date/time and autocomplete
widgets changed. Update any custom CSS or Selenium selectors:

- Select2 / Selectize: ``.select2-*`` / ``.selectize-*`` →
  Tom Select ``.ts-*`` (dropdown options are ``.ts-dropdown .option``; the
  editable control is ``#<oid>-ts-control``).
- Date / time pickers: pickadate ``.picker__*`` → flatpickr ``.flatpickr-*``.
- Autocomplete: typeahead ``.tt-suggestion`` / ``<p>`` suggestions →
  ``.ts-dropdown .option``.

Money input behavior
+++++++++++++++++++++

``MoneyInputWidget`` now formats currency **left-to-right** (typing ``100.01``
yields ``100.01``), whereas jquery.maskMoney filled right-to-left, cents-first.

What stayed compatible
----------------------

- The Colander schema and widget APIs, widget class names and (almost) all
  widget arguments.
- The :class:`deform.Form` constructor arguments, apart from the deprecated
  ``ajax_options`` and ``boost``.
- The client-side ``deform.addCallback(oid, fn)`` /
  ``deform.processCallbacks()`` JavaScript API used by widget templates.

Sequences of enhanced widgets
++++++++++++++++++++++++++++++

When you add an item to a :term:`sequence` that contains an enhanced widget
(mask, date picker, select, rich text, autocomplete), deform now re-executes
the cloned item's initialization script so the widget is set up correctly in
the newly added row. This happens automatically; no code changes are required.
