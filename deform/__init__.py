import colander
from colander import SchemaNode # API
from colander import Invalid # API

# application domain definitions
#
#   appstruct: the raw application data structure (complex Python objects)
#   cstruct: a set of mappings, sequences, and strings (colander structures)
#   schema: can serialize an appstruct to a cstruct and deserialize a
#     cstruct to an appstruct (object derived from
#     ``colander.SchemaNode`` or ``colander.Schema``)

# widget domain definitions
#
#   formfields: a sequence of form fields (e.g. the rfc 2388 def of "field") 
#   pstruct: the data deserialized by peppercorn from a set of formfields
#   widget: can serialize a cstruct to a form and deserialize a pstruct to
#     a cstruct

# serialization
#
#   appstruct -> cstruct -> form
#             |          |
#             v          v
#          schema      widget
#
#     for each structure in the schema, create a widget node
#     pass a cstruct to the root widget node's ``serialize`` method to
#       generate a form

# deserialization
#
#   formfields -> pstruct -> cstruct -> appstruct
#              |          |          |
#              v          v          v
#          peppercorn   widget    schema
#
#     for each structure in the schema, create a widget node
#     pass a pstruct to the root widget node's ``deserialize`` method to
#       generate a cstruct

# widgets

class Widget(object):
    default = None
    def __init__(self, schema):
        self.schema = schema
        self.name = self.schema.name
        self.widgets = []
        if not self.schema.required:
            self.default = self.schema.serialize(self.schema.default)
        for node in schema.nodes:
            widget_type = getattr(node.typ, 'widget_type', TextInputWidget)
            widget = widget_type(node)
            self.widgets.append(widget)

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

class TextInputWidget(Widget):
    def _default(self, value):
        if value is None:
            return ''
        return value

    def serialize(self, cstruct=None):
        name = self.schema.name
        value = self._default(cstruct)
        return '<input type="text" name="%s" value="%s"/>' % (name, value)

    def deserialize(self, pstruct):
        if not pstruct:
            pstruct = ''
        return pstruct

class CheckboxWidget(Widget):
    def serialize(self, cstruct=None):
        name = self.schema.name
        if cstruct == 'true':
            return '<input type="checkbox" name="%s" checked="true"/>' % name
        else:
            return '<input type="checkbox" name="%s"/>' % name

    def deserialize(self, pstruct):
        if pstruct == 'true':
            return 'true'
        return 'false'

class MappingWidget(Widget):
    def serialize(self, cstruct=None):
        if cstruct is None:
            cstruct = {}
        out = []
        out.append('<input type="hidden" name="__start__" '
                   'value="%s:mapping">' % self.schema.name)
        for widget in self.widgets:
            name = widget.name
            out.append(widget.serialize(cstruct.get(name)))
        out.append('<input type="hidden" name="__end__" '
                   'value="%s:mapping">' % self.schema.name)
        return '\n'.join(out)

    def deserialize(self, pstruct):

        result = {}
        error = None

        for num, widget in enumerate(self.widgets):
            name = widget.name
            substruct = pstruct.get(name)
            try:
                if substruct is None:
                    substruct = widget.default
                    if substruct is None:
                        raise Invalid(self, '%r required but missing' % name)
                result[name] = widget.deserialize(substruct)
            except Invalid, e:
                if error is None:
                    error = Invalid(self)
                e.pos = num
                error.add(e)
        if error is not None:
            raise error

        return result

class SequenceWidget(Widget):
    def serialize(self, cstruct=None):
        if cstruct is None:
            cstruct = []
        out = []
        out.append('<input type="hidden" name="__start__" '
                   'value="%s:sequence">' % self.schema.name)
        for item in cstruct:
            widget = self.widgets[0]
            out.append(widget.serialize(item))
        out.append('<input type="hidden" name="__end__" '
                   'value="%s:sequence">' % self.schema.name)
        return '\n'.join(out)

    def deserialize(self, pstruct):
        if pstruct is None:
            pstruct = []
        error = None
        result = []
        for num, substruct in enumerate(pstruct):
            try:
                val = self.widgets[0].deserialize(substruct)
                result.append(val)
            except Invalid, e:
                if error is None:
                    error = Invalid(self)
                e.pos = num
                error.add(e)

        if error is not None:
            raise error

        return result
        

class Form(MappingWidget):
    def __init__(self, schema, action='.', method='POST'):
        self.action = action
        self.method = method
        MappingWidget.__init__(self, schema)

    def serialize(self, cstruct=None):
        if cstruct is None:
            cstruct = {}
        out = []
        out.append('<form name="%s" method="%s" action="%s" '
                   'encoding="multipart/form-data">' % (
                       self.schema.name,
                       self.method,
                       self.action,
                       ))
        for widget in self.widgets:
            name = widget.schema.name
            out.append(widget.serialize(cstruct.get(name)))
        out.append('</form>')
        return '\n'.join(out)

# data types
        
class Mapping(colander.Mapping):
    widget_type = MappingWidget

class Sequence(colander.Sequence):
    widget_type = SequenceWidget

class String(colander.String):
    widget_type = TextInputWidget

class Integer(colander.Integer):
    widget_type = TextInputWidget

class Float(colander.Integer):
    widget_type = TextInputWidget

class Boolean(colander.Boolean):
    widget_type = CheckboxWidget

# schema nodes

class MappingSchema(colander.MappingSchema):
    schema_type = Mapping

Schema = MappingSchema

class SequenceSchema(colander.SequenceSchema):
    schema_type = Sequence

