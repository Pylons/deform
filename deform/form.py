from deform import widget
from deform import field

class Form(field.Field):
    """
    Field representing an entire form.

    Arguments:

    schema
        A :class:`colander.SchemaNode` object representing a
        schema to be rendered.  Required.

    action
        The form action (inserted into the ``action`` attribute of
        the form's form tag when rendered).  Default ``.`` (single
        dot).

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
        The identifier for this form.  This value, if not ``None``,
        will be used as the value of a hidden form input control
        (``__formid__``) which will be placed in this form's
        rendering.  You should pass a non-``None`` value for
        ``formid`` when more than one Deform form is placed into a
        single page and both share the same action.  When one of the
        forms on the page is posted, your code will to be able to
        decide which of those forms was posted based on the value of
        ``__formid__``.  If this value is ``None``, a hidden
        ``__formid__`` control will not be placed into the form's
        rendering.

    The :class:`deform.Form` constructor also accepts all the keyword
    arguments accepted by the :class`deform.Field` class.  These
    keywords mean the same thing in the context of a Form as they do
    in the context of a Field.
    """
    def __init__(self, schema, action='.', method='POST', buttons=(),
                 formid=None, **kw):
        field.Field.__init__(self, schema, **kw)
        _buttons = []
        for button in buttons:
            if isinstance(button, basestring):
                button = Button(button)
            _buttons.append(button)
        self.action = action
        self.method = method
        self.buttons = _buttons
        self.formid = formid
        self.widget = widget.FormWidget()

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

    value
        The value used as the value of the button when rendered (the
        ``value`` attribute of the button or input tag resulting from
        a form rendering).  Default: same as ``name`` passed.
    """
    def __init__(self, name='submit', title=None, value=None):
        if title is None:
            title = name.capitalize()
        if value is None:
            value = name
        self.name = name
        self.title = title
        self.value = value

