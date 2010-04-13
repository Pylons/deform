import unittest

class TestAPI(unittest.TestCase):
    def test_it(self):
        # none of these imports should fail
        from deform import Mapping 
        from deform import Sequence
        from deform import String
        from deform import Integer
        from deform import Float
        from deform import Boolean
        from deform import Date
        from deform import FileData
        from deform import SchemaNode
        from deform import MappingSchema
        from deform import Schema
        from deform import SequenceSchema

        from deform import Form
        from deform import Button
        from deform import Field

        from deform import Invalid
        from deform import ValidationFailure
        from deform import TemplateError

        from deform import MessageFactory
        
        
        
