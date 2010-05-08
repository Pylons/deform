import unittest

class TestAPI(unittest.TestCase):
    def test_it(self):
        # none of these imports should fail
        from deform import Form
        from deform import Button
        from deform import Field

        from deform import FileData
        from deform import Set

        from deform import ValidationFailure
        from deform import TemplateError

        from deform import ZPTRendererFactory
        from deform import default_renderer

        from deform import widget
        
        
        
        
        
