from deform import widget
from deform import field

class Form(field.Field):
    """
    Field representing an entire form.

    Arguments:

    schema
        A :class:`deform.schema.SchemaNode` object representing a
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

    """
    def __init__(self, schema, action='.', method='POST',
                 buttons=(), renderer=None, translate=None):
        field.Field.__init__(self, schema, renderer=renderer,
                             translate=translate)
        _buttons = []
        for button in buttons:
            if isinstance(button, basestring):
                button = Button(button)
            _buttons.append(button)
        self.action = action
        self.method = method
        self.buttons = _buttons
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

