import unittest

class TestValidationFailure(unittest.TestCase):
    def _makeOne(self, field, cstruct, error):
        from deform.exception import ValidationFailure
        return ValidationFailure(field, cstruct, error)

    def test_render(self):
        form = DummyForm()
        cstruct = {}
        e = self._makeOne(form, cstruct, None)
        result = e.render()
        self.assertEqual(result, cstruct)

class DummyForm(object):
    def render(self, cstruct):
        return cstruct
    
