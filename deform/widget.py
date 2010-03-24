import urllib
import colander
import peppercorn

from deform import template
from deform import exception

class Widget(object):
    """
    A widget is the building block for forms and form elements.  The
    :class:`deform.widget.Widget` class is never instantiated
    directly: it is the abstract class from which all other widget
    (and form) types within :mod:`deform.widget` derive.  It should
    likely also be subclassed by application-developer-defined
    widgets.

    Each widget instance is associated with a schema element instance.
    Widget instances related to schema instances are created when a
    :class:`deform.widget.Form` object is created (a Form object takes
    a schema object as a required input).

    All widgets have the following attributes:

    ``error``

        The exception raised by the last attempted validation of the
        schema element associated with this widget.  By default, this
        attribute is ``None``.  If non-None, this attribute is usually
        an instance of the exception class :class:`colander.Invalid`,
        which has a ``msg`` attribute providing a human-readable
        validation error message.

    ``default``

        The (serialized) default value provided by the schema object
        associated with this widget.  By default this is ``None``.  If
        the schema object has a default, the ``default`` attribute of
        the associated widget will be automatically set to the
        serialized default value of the schema element at widget
        construction time.

    ``hidden``

        An attribute indicating the hidden state of this widget.  The
        default is ``False``.  If this attribute is not ``False``, the
        widget will not be rendered in the form (although, if this
        widget is a container widget, its children will be; it is not
        a recursive flag).

    ``error_class``

        The name of the CSS class attached to various tags in the form
        renderering indicating an error condition for this widget.  By
        default, this is ``error``.

    ``renderer``

        The template :term:`renderer` associated with this form.  If a
        renderer is not passed to the constructor, the default deform
        renderer will be used (only templates from
        ``deform/templates`` will be used).

    ``name``

        The name of this widget.  By default, it is the same as the
        name of the associated schema element.  Changing this
        attribute is discouraged; it is mostly just an alias for use
        in templates.

    ``required``

        The required state of the schema element associated with this
        widget.  Changing this attribute is discouraged; it is mostly
        just an alias for use in templates.

    ``title``

        The title of this widget, which shows up in various places
        within the generated form.  By default, it is the same as the
        associated schema element's title attribute.

    ``description``

        The description of this widget, which shows up in various
        places within the generated form (such as in an associated
        tooltip).  By default, it is the same as the associated schema
        element's description attribute.

    ``widgets``

        A sequence representing the child widgets of this widget.
        Each child widget relates to a child schema node of the
        associated schema element.
        
    """
    error = None
    default = None
    hidden = False
    error_class = 'error'

    def __init__(self, schema, renderer=None):
        self.schema = schema
        if renderer is None:
            renderer = template.default_renderer
        self.renderer = renderer
        self.name = self.schema.name
        self.title = self.schema.title
        self.description = self.schema.description
        self.required = self.schema.required
        self.widgets = []
        if not self.schema.required:
            self.default = self.schema.serialize(self.schema.default)
        for node in schema.nodes:
            widget_type = getattr(node, 'widget_type', None)
            if widget_type is None:
                widget_type = getattr(node.typ, 'widget_type', TextInputWidget)
            widget = widget_type(node, renderer=renderer)
            self.widgets.append(widget)

    def __getitem__(self, name):
        """ Return the subwidget of this widget named ``name`` or
        raise a :exc:`KeyError` if a subwidget does not exist named
        ``name``."""
        for widget in self.widgets:
            if widget.name == name:
                return widget
        raise KeyError(name)

    def serialize(self, cstruct=None):
        """
        Serialize a :term:`cstruct` value to a form rendering and
        return the rendering.  The result of this method should always
        be a string (containing HTML).
        """
        raise NotImplementedError

    def deserialize(self, pstruct=None):
        """
        Deserialize a :term:`pstruct` value to a :term:`cstruct` value
        and return the :term:`cstruct` value.
        """
        raise NotImplementedError

    def validate(self, fields):
        """
        Validate the set of fields returned by a form submission
        against the schema associated with this form.  ``fields``
        should be a *document-ordered* sequence of two-tuples that
        represent the form submission data.  Each two-tuple should be
        in the form ``(key, value)``.

        Using WebOb, you can compute a suitable value for ``fields``
        via::

          request.POST.items()

        Using cgi.FieldStorage named ``fs``, you can compute a
        suitable value for ``fields`` via::

          fields = []
          if fs.list:
              for field in fs.list:
                  if field.filename:
                      fields.append((field.name, field))
                  else:
                      fields.append((field.name, field.value))

        Equivalent ways of computing ``fields`` should be available to
        any web framework.

        When the ``validate`` method is called:

        - if the fields are successfully validated, a data structure
          represented by the deserialization of the data as per the
          schema is returned.  It will be a mapping.

        - If the fields cannot be successfully validated, a
          :exc:`deform.exception.FormValidationError` is raised.

        The ``serialize`` method of a
        :exc:`deform.exception.FormValidationError` exception can be
        used to reserialize the form in such a way that the user will
        see error markers in the form HTML.  Therefore, the typical
        usage of ``validate`` in the wild is often something like this
        (at least in terms of code found within the body of a
        :mod:`repoze.bfg` view function, the particulars will differ
        in your web framework)::

          from webob.exc import HTTPFound

          if 'submit' in request.POST:  # the form submission needs validation
              fields = request.POST.items()
              try:
                  deserialized = form.validate(fields)
                  do_something(deserialized)
                  return HTTPFound(location='http://example.com/success')
              except deform.exception.FormValidationError, e:
                  return {'form':e.serialize()}
          else:
              return {'form':form.serialize()} # the form just needs rendering
        """
        pstruct = peppercorn.parse(fields)
        cstruct = self.deserialize(pstruct)
        try:
            return self.schema.deserialize(cstruct)
        except colander.Invalid, e:
            self.handle_error(e)
            raise exception.FormValidationError(self, cstruct, e)

    def handle_error(self, error):
        self.error = error
        # XXX exponential time
        for e in error.children:
            for widget in self.widgets:
                if e.node is widget.schema:
                    widget.handle_error(e)

class TextInputWidget(Widget):
    """
    Renders an <input type="text"/> widget.

    **Attributes**

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).
    """
    template = 'textinput.html'
    size = None
    def serialize(self, cstruct=None):
        if cstruct is None:
            cstruct = self.default
        if cstruct is None:
            cstruct = ''
        return self.renderer(self.template, widget=self, cstruct=cstruct)

    def deserialize(self, pstruct):
        if pstruct is None:
            pstruct = ''
        pstruct = pstruct.strip()
        return pstruct

class CheckboxWidget(Widget):
    """
    Renders an <input type="checkbox"/> widget.

    **Attributes**

    true_val
        The value which should be returned during deserialization if
        the box is checked.  Default: ``true``.

    false_val
        The value which should be returned during deserialization if
        the box was left unchecked.  Default: ``false``.
    """
    true_val = 'true'
    false_val = 'false'
    def serialize(self, cstruct=None):
        name = self.schema.name
        if cstruct is None:
            cstruct = self.default
        if cstruct == self.true_val:
            return ('<input type="checkbox" name="%s" value="%s" '
                    'checked="true"/>' % (name, self.true_val))
        else:
            return '<input type="checkbox" name="%s" value="%s"/>' % (
                name, self.true_val)

    def deserialize(self, pstruct):
        if pstruct is None:
            pstruct = self.false_val
        return (pstruct == self.true_val) and self.true_val or self.false_val

class RadioChoiceWidget(Widget):
    values = ()

    def serialize(self, cstruct=None):
        out = []
        if cstruct is None:
            cstruct = self.default
        for value, description in self.values:
            out.append('<label for="%s">%s</label>' % (self.schema.name,
                                                       description))
            if value == cstruct:
                out.append(
                    '<input type="radio" name="%s" value="%s" '
                    'checked="true"/>' % (self.schema.name, value))
            else:
                out.append(
                    '<input type="radio" name="%s" value="%s"/>' % (
                        self.schema.name, value))
        return '\n'.join(out)

    def deserialize(self, pstruct):
        if pstruct is None:
            pstruct = ''
        return pstruct

class CheckedPasswordWidget(Widget):
    _confirm = ''
    def serialize(self, cstruct=None):
        if cstruct is None:
            cstruct = self.default
        if cstruct is None:
            cstruct = ''
        out = []
        name = self.schema.name
        out.append(
            '<input type="hidden" name="__start__" value="%s:mapping"' % name)
        out.append('<label for="password">Password</label>')
        out.append(
            '<input type="password" name="password" value="%s"/>' % cstruct)
        out.append('<label for="confirm">Confirm Password</label>')
        out.append('<input type="password" name="confirm" value="%s"/>'
                   % self._confirm)
        out.append(
            '<input type="hidden" name="__end__" value="%s:mapping"' % name)
        return '\n'.join(out)
        
    def deserialize(self, pstruct):
        if pstruct is None:
            pstruct = {}
        passwd = pstruct.get('password') or ''
        confirm = pstruct.get('confirm') or ''
        self._confirm = confirm
        if passwd != confirm:
            self.error = colander.Invalid(
                self.schema,
                'Password did not match confirmation')
        return passwd

class MappingWidget(Widget):
    template = 'mapping.html'
    error_class = None
    hidden = True

    def serialize(self, cstruct=None):
        """
        Serialize a cstruct value to a form rendering and return the
        rendering.  The result of this method should always be a
        string (containing HTML).
        """
        if cstruct is None:
            cstruct = {}
        return self.renderer(self.template, widget=self, cstruct=cstruct)

    def deserialize(self, pstruct):

        result = {}

        if pstruct is None:
            pstruct = {}

        for num, widget in enumerate(self.widgets):
            name = widget.name
            substruct = pstruct.get(name)
            result[name] = widget.deserialize(substruct)

        return result

class SequenceWidget(Widget):
    hidden = True
    error_class = None

    def serialize(self, cstruct=None):
        out = []

        if cstruct is None:
            cstruct = []

        widget = self.widgets[0]
        proto_out = []
        proto_out.append('<div class="removeable"/>')
        proto_out.append('<span onclick="javascript:remove_parent(this);" '
                         'title="Remove">X</span>')
        proto_out.append(widget.serialize(None))
        proto_out.append('</div>')
        prototype = '\n'.join(proto_out)
        if isinstance(prototype, unicode):
            prototype = prototype.encode('utf-8')
        prototype = urllib.quote(prototype)
        out.append('<input type="hidden" name="__start__" '
                   'value="%s:sequence" prototype="%s">' % (
                       (self.schema.name, prototype)))
        out.append("""<div onclick="add_new_item(this)">Add %s</div>""" %
                   self.title)
        for item in cstruct:
            out.append('<div class="removeable"/>')
            out.append('<span onclick="remove_parent(this);" '
                       'title="Remove">X</span>')
            out.append(widget.serialize(item))
            out.append('</div>')
        out.append('<input type="hidden" name="__end__" '
                   'value="%s:sequence">' % self.schema.name)
        return '\n'.join(out)

    def deserialize(self, pstruct):
        result = []

        if pstruct is None:
            pstruct = []

        widget = self.widgets[0]
        for num, substruct in enumerate(pstruct):
            val = widget.deserialize(substruct)
            result.append(val)

        return result

class Button(object):
    """
    A class representing a form submit button.  A sequence of
    :class:`deform.widget.Button` objects may be passed to the
    constructor of a :class:`deform.form.Form` class when it is
    created to represent the buttons renderered at the bottom of the
    form.

    Arguments:

    ``name``

        The string or unicode value used as the ``name`` of the button
        when rendered (the ``name`` attribute of the button or input
        tag resulting from a form rendering).  Default: ``submit``.

    ``title``

        The value used as the title of the button when rendered (shows
        up in the button inner text).  Default: capitalization of
        whatever is passed as ``name``.  E.g. if ``name`` is passed as
        ``submit``, ``title`` will be ``Submit``.

    ``value``

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

class Form(MappingWidget):
    template = 'form.html'

    def __init__(self, schema, renderer=None, action='.', method='POST',
                 buttons=()):
        """
        Arguments:

        ``schema``

            A :class:`deform.schema.SchemaNode` object representing a
            schema to be rendered.  Required.

        ``renderer``

            A :term:`renderer` callable.  Defaults to ``None``, which
            causes the default renderer to be used.

        ``action``

            The form action (inserted into the ``action`` attribute of
            the form's form tag when rendered).  Default ``.`` (single
            dot).

        ``method``

            The form method (inserted into the ``method`` attribute of
            the form's form tag when rendered).  Default: ``POST``.

        ``buttons``

            A sequence of strings or :class:`deform.widget.Button`
            objects representing submit buttons that will be placed at
            the bottom of the form.  If any string is passed in the
            sequence, it is converted to
            :class:`deform.widget.Button` objects.

        """
        self.action = action
        self.method = method
        self.buttons = []
        for button in buttons:
            if isinstance(button, basestring):
                button = Button(button)
            self.buttons.append(button)
        MappingWidget.__init__(self, schema, renderer=renderer)

