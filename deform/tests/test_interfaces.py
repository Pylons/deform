import unittest

class TestFileUploadTempStore(unittest.TestCase):
    def _makeOne(self):
        from deform.interfaces import FileUploadTempStore
        return FileUploadTempStore()

    def test_all_empty_funcs(self):
        myfuts = self._makeOne()
        myfuts.__setitem__("dummy", "nothing")
        myfuts.__getitem__("dummy")
        myfuts.get("dummy", default="nothing")
        myfuts.__contains__("dummy")
        myfuts.preview_url("dummy")
