"""API tests."""
# Standard Library
import unittest


class TestAPI(unittest.TestCase):
    def test_it(self):
        """
        none of these imports should fail
        """
        # Deform
        from deform import Button  # noQA
        from deform import Field  # noQA
        from deform import FileData  # noQA
        from deform import Form  # noQA
        from deform import TemplateError  # noQA
        from deform import ValidationFailure  # noQA
        from deform import ZPTRendererFactory  # noQA
        from deform import default_renderer  # noQA
        from deform import widget  # noQA
