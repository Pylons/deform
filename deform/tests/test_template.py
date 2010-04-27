import unittest

class TestZPTTemplateLoader(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.template import ZPTTemplateLoader
        return ZPTTemplateLoader(**kw)

    def test_search_path_None(self):
        loader = self._makeOne()
        self.assertEqual(loader.search_path, [])

    def test_search_path_string(self):
        loader = self._makeOne(search_path='path')
        self.assertEqual(loader.search_path, ['path'])

    def test_load_exists(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        loader = self._makeOne(search_path=[fixtures])
        result = loader.load('test.pt')
        self.failUnless(result)

    def test_load_with_translate(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        loader = self._makeOne(search_path=[fixtures], translate='abc')
        result = loader.load('test.pt')
        self.assertEqual(result.translate, 'abc')

    def test_load_with_encoding(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        loader = self._makeOne(search_path=[fixtures], encoding='utf-16')
        result = loader.load('test.pt')
        self.assertEqual(result.encoding, 'utf-16')

    def test_load_with_auto_reload(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        loader = self._makeOne(search_path=[fixtures], auto_reload=True)
        result = loader.load('test.pt')
        self.assertEqual(result.auto_reload, True)

    def test_load_notexists(self):
        import os
        from deform.template import TemplateError
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        loader = self._makeOne(search_path=[fixtures])
        self.assertRaises(TemplateError, loader.load, 'doesnt')
        self.failUnless(
            os.path.join(fixtures, 'doesnt') in loader.notexists)

    def test_load_negative_cache(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        path = os.path.join(fixtures, 'test.pt')
        loader = self._makeOne(search_path=[fixtures], auto_reload=True)
        loader.notexists[path] = True
        result = loader.load('test.pt')
        self.failUnless(result)

    def test_load_negative_cache2(self):
        import os
        from deform.template import TemplateError
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        path = os.path.join(fixtures, 'test.pt')
        loader = self._makeOne(search_path=[fixtures], auto_reload=False)
        loader.notexists[path] = True
        self.assertRaises(TemplateError, loader.load, 'test.pt')

class TestZPTRendererFactory(unittest.TestCase):
    def _makeOne(self, dirs, **kw):
        from deform.template import ZPTRendererFactory
        return ZPTRendererFactory(dirs, **kw)

    def test_functional(self):
        from pkg_resources import resource_filename
        default_dir = resource_filename('deform', 'tests/fixtures/')
        renderer = self._makeOne((default_dir,))
        result = renderer('test')
        self.assertEqual(result, u'<div>Test</div>')

    def test_it(self):
        renderer = self._makeOne(
            ('dir',),
            auto_reload=True,
            debug=True,
            encoding='utf-16',
            translator=lambda *arg: 'translation',
            )
        self.assertEqual(renderer.loader.auto_reload, True)
        self.assertEqual(renderer.loader.debug, True)
        self.assertEqual(renderer.loader.search_path, ('dir',))
        self.assertEqual(renderer.loader.encoding, 'utf-16')
        self.assertEqual(renderer.loader.translate('a'), 'translation')

class Test_default_renderer(unittest.TestCase):
    def _callFUT(self, template, **kw):
        from deform.template import default_renderer
        return default_renderer(template, **kw)
    
    def test_call_defaultdir(self):
        result = self._callFUT('checkbox',
                               **{'cstruct':None, 'field':DummyField()})
        self.assertEqual(result,
                         u'<input type="checkbox" name="name" value="true" '
                         'id="oid" />')

class DummyWidget(object):
    name = 'name'
    true_val = 'true'
    false_val = 'false'
    
class DummyField(object):
    widget = DummyWidget()
    name = 'name'
    oid = 'oid'
    
