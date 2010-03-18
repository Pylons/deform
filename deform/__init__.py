import colander
from colander import SchemaNode

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
    def __init__(self, schema):
        self.schema = schema
        self.widgets = []
        for node in schema.nodes:
            widget_type = getattr(node.typ, 'widget_type', TextInput)
            widget = widget_type(node)
            self.widgets.append(widget)

    def serialize(self, value=None):
        """
        Serialize a cstruct value to a form rendering and return the
        rendering.  The result of this method should always be a
        string (containing HTML).
        """
        return value

    def deserialize(self, value=None):
        """
        Deserialize a pstruct value to a cstruct value and return the
        cstruct value.
        """
        return value

class TextInput(Widget):
    def serialize(self, value=None):
        name = self.schema.name
        if value is None:
            return '<input type="text" name="%s"/>' % name
        return '<input type="text" name="%s" value="%s"/>' % (name, value)

class CheckboxWidget(Widget):
    def serialize(self, value=None):
        name = self.schema.name
        if value is None:
            return '<input type="checkbox" name="%s"/>' % name
        if value == 'true':
            return '<input type="checkbox" name="%s" checked="true"/>' % name
        else:
            return '<input type="checkbox" name="%s"/>' % name

    def deserialize(self, value=None):
        if value == 'true':
            return 'true'
        return 'false'

class MappingWidget(Widget):
    def serialize(self, value=None):
        if value is None:
            value = {}
        out = []
        out.append('<input type="hidden" name="__start__" '
                   'value="%s:mapping">' % self.schema.name)
        for widget in self.widgets:
            name = widget.schema.name
            out.append(widget.serialize(value.get(name)))
        out.append('<input type="hidden" name="__end__" '
                   'value="%s:mapping">' % self.schema.name)
        return '\n'.join(out)

class SequenceWidget(Widget):
    def serialize(self, value=None):
        if value is None:
            value = []
        out = []
        out.append('<input type="hidden" name="__start__" '
                   'value="%s:sequence">' % self.schema.name)
        for item in value:
            widget = self.widgets[0]
            out.append(widget.serialize(item))
        out.append('<input type="hidden" name="__end__" '
                   'value="%s:sequence">' % self.schema.name)
        return '\n'.join(out)

class Form(Widget):
    def serialize(self, value=None):
        if value is None:
            value = {}
        out = []
        out.append('<form name="%s" method="POST" action="." '
                   'encoding="multipart/form-data">' % self.schema.name)
        for widget in self.widgets:
            name = widget.schema.name
            out.append(widget.serialize(value.get(name)))
        out.append('</form>')
        return '\n'.join(out)

# data types
        
class Mapping(colander.Mapping):
    widget_type = MappingWidget

class Sequence(colander.Sequence):
    widget_type = SequenceWidget

class String(colander.String):
    widget_type = TextInput

class Integer(colander.Integer):
    widget_type = TextInput

class Float(colander.Integer):
    widget_type = TextInput

class Boolean(colander.Boolean):
    widget_type = CheckboxWidget

# schema nodes

class MappingSchema(colander.MappingSchema):
    schema_type = Mapping

Schema = MappingSchema

class SequenceSchema(colander.SequenceSchema):
    schema_type = Sequence

if __name__ == '__main__':
    cstruct = {
        'name': 'project1',
        'title': 'Cool project',
        'cool': 'true',
        'series': {
            'name':'date series 1',
            'dates': [{'month':'10', 'day':'12', 'year':'2008'},
                      {'month':'10', 'day':'12', 'year':'2009'}],
            }
        }

    class DateSchema(MappingSchema):
        month = SchemaNode(Integer())
        year = SchemaNode(Integer())
        day = SchemaNode(Integer())

    class DatesSchema(SequenceSchema):
        date = DateSchema()

    class SeriesSchema(MappingSchema):
        name = SchemaNode(String())
        dates = DatesSchema()

    class MySchema(MappingSchema):
        name = SchemaNode(String())
        title = SchemaNode(String())
        cool = SchemaNode(Boolean())
        series = SeriesSchema()

    schema = MySchema()
    form = Form(schema)

    # add form
    print form.serialize(
        {'series':{'dates':[{'day':'', 'month':'', 'year':''}]}})
    """
    <form name="" method="POST" action="." encoding="multipart/form-data">
    <input type="text" name="name"/>
    <input type="text" name="title"/>
    <input type="hidden" name="__start__" value="series:mapping">
    <input type="text" name="name"/>
    <input type="hidden" name="__start__" value="dates:sequence">
    <input type="hidden" name="__start__" value="date:mapping">
    <input type="text" name="month" value=""/>
    <input type="text" name="year" value=""/>
    <input type="text" name="day" value=""/>
    <input type="hidden" name="__end__" value="date:mapping">
    <input type="hidden" name="__end__" value="dates:sequence">
    <input type="hidden" name="__end__" value="series:mapping">
    </form>
    """

    # edit form
    print form.serialize(cstruct)
    """
    <form name="" method="POST" action="." encoding="multipart/form-data">
    <input type="text" name="name" value="project1"/>
    <input type="text" name="title" value="Cool project"/>
    <input type="hidden" name="__start__" value="series:mapping">
    <input type="text" name="name" value="date series 1"/>
    <input type="hidden" name="__start__" value="dates:sequence">
    <input type="hidden" name="__start__" value="date:mapping">
    <input type="text" name="month" value="10"/>
    <input type="text" name="year" value="2008"/>
    <input type="text" name="day" value="12"/>
    <input type="hidden" name="__end__" value="date:mapping">
    <input type="hidden" name="__start__" value="date:mapping">
    <input type="text" name="month" value="10"/>
    <input type="text" name="year" value="2009"/>
    <input type="text" name="day" value="12"/>
    <input type="hidden" name="__end__" value="date:mapping">
    <input type="hidden" name="__end__" value="dates:sequence">
    <input type="hidden" name="__end__" value="series:mapping">
    </form>
    """
    
    

