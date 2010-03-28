import unittest

class TestMappingSchema(unittest.TestCase):
    def test_construction(self):
        from deform.schema import MappingSchema
        from deform.schema import SchemaNode
        from deform.schema import Mapping
        class MyMappingSchema(MappingSchema):
            name = SchemaNode(None)
        my_schema = MyMappingSchema()
        self.assertEqual(my_schema.__class__, SchemaNode)
        self.assertEqual(my_schema.typ.__class__, Mapping)
        self.assertEqual(len(my_schema.children), 1)
        
        
class TestSequenceSchema(unittest.TestCase):
    def test_construction(self):
        from deform.schema import SequenceSchema
        from deform.schema import SchemaNode
        from deform.schema import Sequence
        class MyMappingSchema(SequenceSchema):
            name = SchemaNode(None)
        my_schema = MyMappingSchema()
        self.assertEqual(my_schema.__class__, SchemaNode)
        self.assertEqual(my_schema.typ.__class__, Sequence)
        self.assertEqual(len(my_schema.children), 1)
        
        
