import colander
import peppercorn

from deform import template

class FormValidationError(Exception):
    def __init__(self, form, cstruct, e):
        Exception.__init__(self)
        self.form = form
        self.cstruct = cstruct
        self.invalid_exc = e

    def serialize(self):
        return self.form.serialize(self.cstruct)

class Widget(object):
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
            widget_type = getattr(node.typ, 'widget_type', TextInputWidget)
            widget = widget_type(node, renderer=renderer)
            self.widgets.append(widget)

    def __getitem__(self, name):
        for widget in self.widgets:
            if widget.name == name:
                return widget
        raise KeyError(name)

    def serialize(self, cstruct=None):
        """
        Serialize a cstruct value to a form rendering and return the
        rendering.  The result of this method should always be a
        string (containing HTML).
        """
        raise NotImplementedError

    def deserialize(self, pstruct=None):
        """
        Deserialize a pstruct value to a cstruct value and return the
        cstruct value.
        """
        raise NotImplementedError

    def validate(self, fields):
        pstruct = peppercorn.parse(fields)
        cstruct = self.deserialize(pstruct)
        try:
            return self.schema.deserialize(cstruct)
        except colander.Invalid, e:
            self.handle_error(e)
            raise FormValidationError(self, cstruct, e)

    def handle_error(self, error):
        self.error = error
        # XXX exponential time
        for e in error.children:
            for widget in self.widgets:
                if e.node is widget.schema:
                    widget.handle_error(e)

class TextInputWidget(Widget):
    template = 'textinput.html'
    size = None
    def serialize(self, cstruct=None):
        name = self.schema.name
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
            out.append('<div>')
            if value == cstruct:
                out.append(
                    '<input type="radio" name="%s" value="%s" '
                    'checked="true"/>' % (self.schema.name, value))
            else:
                out.append(
                    '<input type="radio" name="%s" value="%s"/>' % (
                        self.schema.name, value))
            out.append('<label for="%s">%s</label>' % (self.schema.name,
                                                       description))
            out.append('</div>')
        return '\n'.join(out)

    def deserialize(self, pstruct):
        if pstruct is None:
            pstruct = ''
        return pstruct

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
    def serialize(self, cstruct=None):
        out = []

        if cstruct is None:
            cstruct = []

        out.append('<input type="hidden" name="__start__" '
                   'value="%s:sequence">' % self.schema.name)
        widget = self.widgets[0]
        for item in cstruct:
            out.append(widget.serialize(item))
        out.append('<input type="hidden" name="__end__" '
                   'value="%s:sequence">' % self.schema.name)
        return '\n'.join(out)

    def deserialize(self, pstruct):
        result = []

        if pstruct is None:
            pstruct = []

        for num, substruct in enumerate(pstruct):
            val = self.widgets[0].deserialize(substruct)
            result.append(val)

        return result

class Button(object):
    def __init__(self, name='', title=None, value=None):
        if title is None:
            title = name
        if value is None:
            value = name
        self.name = name
        self.title = title
        self.value = value

class Form(MappingWidget):
    template = 'form.html'

    def __init__(self, schema, renderer=None, action='.', method='POST',
                 buttons=()):
        self.action = action
        self.method = method
        self.buttons = []
        for button in buttons:
            if isinstance(button, basestring):
                button = Button(button)
            self.buttons.append(button)
        MappingWidget.__init__(self, schema, renderer=renderer)

