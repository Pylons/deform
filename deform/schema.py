import colander

from deform import widget

# data types

class Mapping(colander.Mapping):
    default_widget_maker = widget.MappingWidget

class Sequence(colander.Sequence):
    default_widget_maker = widget.SequenceWidget

class String(colander.String):
    default_widget_maker = widget.TextInputWidget

class Integer(colander.Integer):
    default_widget_maker = widget.TextInputWidget

class Float(colander.Integer):
    default_widget_maker = widget.TextInputWidget

class Boolean(colander.Boolean):
    default_widget_maker = widget.CheckboxWidget

# schema nodes

class SchemaNode(colander.SchemaNode):
    pass

class MappingSchema(colander.MappingSchema):
    schema_type = Mapping
    node_type = SchemaNode

Schema = MappingSchema

class SequenceSchema(colander.SequenceSchema):
    schema_type = Sequence
    node_type = SchemaNode
    

    
