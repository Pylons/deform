import unittest

def invalid_exc(func, *arg, **kw):
    from colander import Invalid
    try:
        func(*arg, **kw)
    except Invalid, e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover

class TestString(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.schema import String
        return String(**kw)

    def test_serialize_value_is_unicode(self):
        node = DummySchemaNode()
        typ = self._makeOne()
        result = typ.serialize(node, u'unicode')
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'unicode')

    def test_serialize_value_is_str(self):
        node = DummySchemaNode()
        typ = self._makeOne()
        result = typ.serialize(node, 'str')
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'str')

class TestSet(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.schema import Set
        return Set(**kw)

    def test_serialize(self):
        node = DummySchemaNode()
        typ = self._makeOne()
        provided = []
        result = typ.serialize(node, provided)
        self.failUnless(result is provided)

    def test_deserialize_no_iter(self):
        node = DummySchemaNode()
        typ = self._makeOne()
        e = invalid_exc(typ.deserialize, node, 'str')
        self.assertEqual(e.msg, "'str' is not iterable")

    def test_deserialize_empty_required_no_default(self):
        node = DummySchemaNode()
        typ = self._makeOne()
        e = invalid_exc(typ.deserialize, node, ())
        self.assertEqual(e.msg, "Required")

    def test_deserialize_empty_required_with_default(self):
        node = DummySchemaNode()
        typ = self._makeOne()
        node.default = ('abc',)
        node.required = False
        result = typ.deserialize(node, ())
        self.assertEqual(result, set(('abc',)))

    def test_deserialize_valid(self):
        node = DummySchemaNode()
        typ = self._makeOne()
        result = typ.deserialize(node, ('a',))
        self.assertEqual(result, set(('a',)))

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
        
class TestFileData(unittest.TestCase):
    def _makeOne(self):
        from deform.schema import FileData
        return FileData()

    def test_deserialize_required_None(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        e = invalid_exc(typ.deserialize, node, None)
        self.assertEqual(e.msg, 'Required')
        
    def test_deserialize_notrequired_None(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        node.required = False
        result = typ.deserialize(node, None)
        self.assertEqual(result, None)

    def test_deserialize_not_None(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        result = typ.deserialize(node, '123')
        self.assertEqual(result, '123')

    def test_serialize_not_a_dict(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        e = invalid_exc(typ.serialize, node, None)
        self.assertEqual(e.msg, 'None is not a dictionary')

    def test_serialize_no_filename(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        e = invalid_exc(typ.serialize, node, {'uid':'uid'})
        self.assertEqual(e.msg, "{'uid': 'uid'} has no filename key")

    def test_serialize_no_uid(self):
        typ = self._makeOne()
        node = DummySchemaNode()
        e = invalid_exc(typ.serialize, node, {'filename':'filename'})
        self.assertEqual(e.msg, "{'filename': 'filename'} has no uid key")

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
        

class DummySchemaNode(object):
    def __init__(self, typ=None, name='', exc=None, default=None):
        self.typ = typ
        self.name = name
        self.exc = exc
        self.required = default is None
        self.default = default
        self.children = []

