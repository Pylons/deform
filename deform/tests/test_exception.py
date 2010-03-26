import unittest

class TestFormValidationError(unittest.TestCase):
    def _makeOne(self, form, cstruct, e):
        from deform.exception import FormValidationError
        return FormValidationError(form, cstruct, e)

    def test_serialize(self):
        form = DummyForm()
        cstruct = {}
        e = self._makeOne(form, cstruct, None)
        result = e.serialize()
        self.assertEqual(result, cstruct)
        self.assertEqual(e.invalid_exc, None)

class DummyForm(object):
    def serialize(self, cstruct):
        return cstruct
    
