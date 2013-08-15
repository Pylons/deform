import unittest

def invalid_exc(func, *arg, **kw):
    from colander import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover


class TestFileData(unittest.TestCase):
    def _makeOne(self):
        from deform.schema import FileData
        return FileData()

    def test_deserialize_null(self):
        from colander import null
        typ = self._makeOne()
        node = DummySchemaNode()
        result = typ.deserialize(node, null)
        self.assertEqual(result, null)

    def test_deserialize_not_null(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        result = typ.deserialize(node, '123')
        self.assertEqual(result, '123')

    def test_serialize_null(self):
        from colander import null
        typ = self._makeOne()
        node = DummySchemaNode()
        result = typ.serialize(node, null)
        self.assertEqual(result, null)

    def test_serialize_not_a_dict(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        e = invalid_exc(typ.serialize, node, None)
        self.assertEqual(e.msg, '${value} is not a dictionary')

    def test_serialize_no_filename(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        e = invalid_exc(typ.serialize, node, {'uid':'uid'})
        self.assertEqual(e.msg, "${value} has no ${key} key")

    def test_serialize_no_uid(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        e = invalid_exc(typ.serialize, node, {'filename':'filename'})
        self.assertEqual(e.msg, "${value} has no ${key} key")

    def test_serialize_with_values(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        result = typ.serialize(node, {'filename':'filename', 'uid':'uid',
                                      'mimetype':'mimetype', 'size':'size',
                                      'fp':'fp', 'preview_url':'preview_url'})
        self.assertEqual(result['filename'], 'filename')
        self.assertEqual(result['uid'], 'uid')
        self.assertEqual(result['mimetype'], 'mimetype')
        self.assertEqual(result['size'], 'size')
        self.assertEqual(result['fp'], 'fp')
        self.assertEqual(result['preview_url'], 'preview_url')

    def test_serialize_with_only_required_values(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        result = typ.serialize(node, {'filename':'filename', 'uid':'uid'})
        self.assertEqual(result['filename'], 'filename')
        self.assertEqual(result['uid'], 'uid')
        self.assertEqual(result['mimetype'], None)
        self.assertEqual(result['size'], None)
        self.assertEqual(result['fp'], None)
        self.assertEqual(result['preview_url'], None)

    def test_serialize_with_unexpected_value(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        result = typ.serialize(
            node,
            {'filename':'filename', 'uid':'uid', 'morg':'moo'}
            )
        self.assertEqual(result['filename'], 'filename')
        self.assertEqual(result['uid'], 'uid')
        self.assertEqual(result['morg'], 'moo')

class DummySchemaNode(object):
    def __init__(self, typ=None, name='', exc=None, default=None):
        self.typ = typ
        self.name = name
        self.exc = exc
        self.required = default is None
        self.default = default
        self.children = []
