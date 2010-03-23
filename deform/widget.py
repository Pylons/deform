import colander
import peppercorn

from deform import template
from deform import exceptions

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
          :exc:`deform.exceptions.FormValidationError` is raised.

        The ``serialize`` method of a
        :exc:`deform.exceptions.FormValidationError` exception can be
        used to reserialize the form in such a way that the user will
        see error markers in the form HTML.  Therefore, the typical
        usage of ``validate`` in the wild is often something like this
        (at least in terms of code found within the body of a
        :mod:`repoze.bfg` view function, the particulars may differ in
        your web framework)::

          from webob.exc import HTTPFound

          if 'submit' in request.POST:  # the form was submitted
              fields = request.POST.items()
              try:
                  deserialized = form.validate(fields)
                  do_something(deserialized)
                  return HTTPFound(location='http://example.com/success')
              except FormValidationError, e:
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
            raise exceptions.FormValidationError(self, cstruct, e)

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

        widget = self.widgets[0]
        for num, substruct in enumerate(pstruct):
            val = widget.deserialize(substruct)
            result.append(val)

        return result

class Button(object):
    def __init__(self, name='', title=None, value=None):
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
        self.action = action
        self.method = method
        self.buttons = []
        for button in buttons:
            if isinstance(button, basestring):
                button = Button(button)
            self.buttons.append(button)
        MappingWidget.__init__(self, schema, renderer=renderer)

