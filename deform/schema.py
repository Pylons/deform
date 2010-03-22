import colander

from deform import widget

# data types

class Mapping(colander.Mapping):
    widget_type = widget.MappingWidget

class Sequence(colander.Sequence):
    widget_type = widget.SequenceWidget

class String(colander.String):
    widget_type = widget.TextInputWidget

class Integer(colander.Integer):
    widget_type = widget.TextInputWidget

class Float(colander.Integer):
    widget_type = widget.TextInputWidget

class Boolean(colander.Boolean):
    widget_type = widget.CheckboxWidget

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
    

    
