import unittest

class TestValidationFailure(unittest.TestCase):
    def _makeOne(self, field, cstruct, error):
        from deform.exception import ValidationFailure
        return ValidationFailure(field, cstruct, error)

    def test_render(self):
        widget = DummyWidget()
        form = DummyForm(widget)
        cstruct = {}
        e = self._makeOne(form, cstruct, None)
        result = e.render()
        self.assertEqual(result, cstruct)

class DummyForm(object):
    def __init__(self, widget):
        self.widget = widget
    
class DummyWidget(object):
    def serialize(self, field, cstruct):
        return cstruct
    
