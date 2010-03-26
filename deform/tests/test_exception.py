import unittest

class TestValidationFailure(unittest.TestCase):
    def _makeOne(self, widget, cstruct, error):
        from deform.exception import ValidationFailure
        return ValidationFailure(widget, cstruct, error)

    def test_serialize(self):
        form = DummyForm()
        cstruct = {}
        e = self._makeOne(form, cstruct, None)
        result = e.serialize()
        self.assertEqual(result, cstruct)

class DummyForm(object):
    def serialize(self, cstruct):
        return cstruct
    
