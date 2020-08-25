"""Form."""
# Standard Library
import re

from chameleon.utils import Markup

from . import compat
from . import field
from . import widget


class Form(field.Field):
    """
    Field representing an entire form.

    Arguments:

    schema
        A :class:`colander.SchemaNode` object representing a
        schema to be rendered.  Required.

    action
        The form action (inserted into the ``action`` attribute of
        the form's form tag when rendered).  Default: the empty string.

    method
        The form method (inserted into the ``method`` attribute of
        the form's form tag when rendered).  Default: ``POST``.

    buttons
        A sequence of strings or :class:`deform.form.Button`
        objects representing submit buttons that will be placed at
        the bottom of the form.  If any string is passed in the
        sequence, it is converted to
        :class:`deform.form.Button` objects.

    formid
        The identifier for this form.  This value will be used as the
        HTML ``id`` attribute of the rendered HTML form.  It will also
        be used as the value of a hidden form input control
        (``__formid__``) which will be placed in this form's
        rendering.  You should pass a string value for ``formid`` when
        more than one Deform form is placed into a single page and
        both share the same action.  When one of the forms on the page
        is posted, your code will to be able to decide which of those
        forms was posted based on the differing values of
        ``__formid__``.  By default, ``formid`` is ``deform``.

    autocomplete
        Controls this form's ``autocomplete`` attribute.  If ``autocomplete``
        is ``None``, no autocomplete attribute will be added to the form tag.
        If ``autocomplete`` is a true value, an ``autocomplete='on'``
        attribute will be added to the form tag.  If ``autocomplete`` is a
        false value, an ``autocomplete='off'`` attribute will be added to the
        form tag.  Default: ``None``.

    focus
        Determines this form's input focus.

        -   If ``focus`` is ``on``, and at least one field has an ``autofocus``
            schema parameter set to ``on``, the first of these fields will
            receive focus on page load.
        -   If ``focus`` is ``on`` or omitted, and no field has an
            ``autofocus`` schema parameter set to ``on``, the first input of
            the first form on the page will receive focus on page load.
        -   If ``focus`` is ``off``, no focusing will be done.

        Default: ``on``.

    use_ajax
       If this option is ``True``, the form will use AJAX (actually
       AJAH); when any submit button is clicked, the DOM node related
       to this form will be replaced with the result of the form post
       caused by the submission.  The page will not be reloaded.  This
       feature uses the ``jquery.form`` library ``ajaxForm`` feature
       as per `http://jquery.malsup.com/form/
       <http://jquery.malsup.com/form/>`_.  Default: ``False``.  If
       this option is ``True``, the ``jquery.form.js`` library must be
       loaded in the HTML page which embeds the form.  A copy of it
       exists in the ``static`` directory of the ``deform`` package.

    ajax_options
       A *string* which must represent a JavaScript object
       (dictionary) of extra AJAX options as per
       `http://jquery.malsup.com/form/#tab3
       <http://jquery.malsup.com/form/#tab3>`_.  For
       example:

       .. code-block:: python

           '{"success": function (rText, sText, xhr, form) {alert(sText)};}'

       Default options exist even if ``ajax_options`` is not provided.
       By default, ``target`` points at the DOM node representing the
       form and and ``replaceTarget`` is ``true``.

       A success handler calls the ``deform.processCallbacks`` method
       that will ajaxify the newly written form again.  If you pass
       these values in ``ajax_options``, the defaults will be
       overridden.  If you want to override the success handler, don't
       forget to call ``deform.processCallbacks``, otherwise
       subsequent form submissions won't be submitted via AJAX.

       This option has no effect when ``use_ajax`` is False.

       The default value of ``ajax_options`` is a string
       representation of the empty object.

    The :class:`deform.Form` constructor also accepts all the keyword
    arguments accepted by the :class:`deform.Field` class.  These
    keywords mean the same thing in the context of a Form as they do
    in the context of a Field (a Form is just another kind of Field).
    """

    css_class = "deform"  # bw compat only; pass a widget to override

    def __init__(
        self,
        schema,
        action="",
        method="POST",
        buttons=(),
        formid="deform",
        use_ajax=False,
        ajax_options="{}",
        autocomplete=None,
        focus="on",
        **kw
    ):
        if autocomplete:
            autocomplete = "on"
        elif autocomplete is not None:
            autocomplete = "off"
        self.autocomplete = autocomplete
        if str(focus).lower() == "off":
            self.focus = "off"
        else:
            self.focus = "on"
        # Use kwargs to pass flags to descendant fields; saves cluttering
        # the constructor
        kw["focus"] = self.focus
        field.Field.__init__(self, schema, **kw)
        _buttons = []
        for button in buttons:
            if isinstance(button, compat.string_types):
                button = Button(button)
            _buttons.append(button)
        self.action = action
        self.method = method
        self.buttons = _buttons
        self.formid = formid
        self.use_ajax = use_ajax
        self.ajax_options = Markup(ajax_options.strip())
        form_widget = getattr(schema, "widget", None)
        if form_widget is None:
            form_widget = widget.FormWidget()
        self.widget = form_widget


class Button(object):
    """
    A class representing a form submit button.  A sequence of
    :class:`deform.widget.Button` objects may be passed to the
    constructor of a :class:`deform.form.Form` class when it is
    created to represent the buttons renderered at the bottom of the
    form.

    Arguments:

    name
        The string or unicode value used as the ``name`` of the button
        when rendered (the ``name`` attribute of the button or input
        tag resulting from a form rendering).  Default: ``submit``.

    title
        The value used as the title of the button when rendered (shows
        up in the button inner text).  Default: capitalization of
        whatever is passed as ``name``.  E.g. if ``name`` is passed as
        ``submit``, ``title`` will be ``Submit``.

    type
        The value used as the type of button. The HTML spec supports
        ``submit``, ``reset`` and ``button``.  A special value of
        ``link`` will create a regular HTML link that's styled to look
        like a button.  Default: ``submit``.

    value
        The value used as the value of the button when rendered (the
        ``value`` attribute of the button or input tag resulting from
        a form rendering).  If the button ``type`` is ``link`` then
        this setting is used as the URL for the link button.
        Default: same as ``name`` passed.

    icon
        glyph icon name to include as part of button.  (Ex. If you
        wanted to add the glyphicon-plus to this button then you'd pass
        in a value of ``plus``)  Default: ``None`` (no icon is added)

    disabled
        Render the button as disabled if True.

    css_class
        The name of a CSS class to attach to the button. In the default
        form rendering, this string will replace the default button type
        (either ``btn-primary`` or ``btn-default``) on the the ``class``
        attribute of the button. For example, if ``css_class`` was
        ``btn-danger`` then the resulting default class becomes
        ``btn btn-danger``. Default: ``None`` (use default class).

    attributes
        HTML5 attributes passed in as a dictionary. This is especially
        useful for a Cancel button where you do not want the client to
        validate the form inputs, for example
        ``attributes={"formnovalidate": "formnovalidate"}``.
    """

    def __init__(
        self,
        name="submit",
        title=None,
        type="submit",  # noQA
        value=None,
        disabled=False,
        css_class=None,
        icon=None,
        attributes=None,
    ):
        if attributes is None:
            attributes = {}
        if title is None:
            title = name.capitalize()
        name = re.sub(r"\s", "_", name)
        if value is None and type != "link":
            value = name
        self.name = name
        self.title = title
        self.type = type  # noQA
        self.value = value
        self.disabled = disabled
        self.css_class = css_class
        self.icon = icon
        self.attributes = attributes
