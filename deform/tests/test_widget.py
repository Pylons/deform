import unittest

class TestWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import Widget
        return Widget(**kw)

    def test_ctor(self):
        widget = self._makeOne(a=1, b=2)
        self.assertEqual(widget.a, 1)
        self.assertEqual(widget.b, 2)
    
    def test_serialize(self):
        widget = self._makeOne()
        self.assertRaises(NotImplementedError, widget.serialize, None, None)

    def test_deserialize(self):
        widget = self._makeOne()
        self.assertRaises(NotImplementedError, widget.deserialize, None, None)

    def test_handle_error(self):
        inner_widget = self._makeOne()
        outer_widget = self._makeOne()
        inner_field = DummyField()
        inner_field.widget = inner_widget
        outer_field = DummyField()
        outer_field.widget = outer_widget
        outer_field.children = [ inner_field ]
        inner_error = DummyInvalid()
        outer_error = DummyInvalid(inner_error)
        outer_widget.handle_error(outer_field, outer_error)
        self.assertEqual(inner_field.error, inner_error)
        self.assertEqual(outer_field.error, outer_error)

class TestTextInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import TextInputWidget
        return TextInputWidget(**kw)
    
    def test_serialize_None_no_default(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_None_with_default(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        field.default = 'default'
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'default')

    def test_serialize_not_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)
        
    def test_deserialize_strip(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = ' abc '
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, 'abc')

    def test_deserialize_no_strip(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = ' abc '
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, ' abc ')

    def test_deserialize_None(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, None)
        self.assertEqual(result, '')

class TestCheckboxWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckboxWidget
        return CheckboxWidget(**kw)
    
    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        field.default = 'default'
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'default')

    def test_serialize_not_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)
        
    def test_deserialize_None(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, None)
        self.assertEqual(result, 'false')

    def test_deserialize_true_val(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'true')
        self.assertEqual(result, 'true')

    def test_deserialize_false_val(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'false')
        self.assertEqual(result, 'false')

class TestRadioChoiceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import RadioChoiceWidget
        return RadioChoiceWidget(**kw)
    
    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        field.default = 'default'
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'default')

    def test_serialize_not_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)
        
    def test_deserialize_None(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, None)
        self.assertEqual(result, '')

    def test_deserialize_other(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'true')
        self.assertEqual(result, 'true')

class TestCheckedPasswordWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckedPasswordWidget
        return CheckedPasswordWidget(**kw)
    
    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        field.default = 'default'
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'default')

    def test_serialize_None_no_default(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        field.default = None
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_deserialize_None(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, None)
        self.assertEqual(result, '')

    def test_deserialize_nonmatching(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field,
                                    {'password':'password', 'confirm':'not'})
        self.assertEqual(result, 'password')
        self.assertEqual(field.error.msg,
                         'Password did not match confirmation')

    def test_deserialize_matching(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, {'password':'password',
                                            'confirm':'password'})
        self.assertEqual(result, 'password')
        self.assertEqual(field.error, None)

class TestMappingWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import MappingWidget
        return MappingWidget(**kw)
    
    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], {})

    def test_serialize_not_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = {'a':1}
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_None(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, None)
        self.assertEqual(result, {})

    def test_deserialize_non_None(self):
        widget = self._makeOne()
        field = DummyField()
        inner_field = DummyField()
        inner_field.name = 'a'
        inner_widget = DummyWidget()
        inner_widget.name = 'a'
        inner_field.widget = inner_widget
        field.children = [inner_field]
        pstruct = {'a':1}
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, {'a':1})

class TestSequenceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import SequenceWidget
        return SequenceWidget(**kw)

    def test_prototype_unicode(self):
        import urllib
        renderer = DummyRenderer(u'abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        field.children=[None]
        result = widget.prototype(field)
        self.assertEqual(type(result), str)
        self.assertEqual(urllib.unquote(result), 'abc')

    def test_prototype_str(self):
        import urllib
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        field.children=[None]
        result = widget.prototype(field)
        self.assertEqual(type(result), str)
        self.assertEqual(urllib.unquote(result), 'abc')

    def test_serialize_None(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children=[inner]
        widget = self._makeOne()
        result = widget.serialize(field)
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 0)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], [])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_not_None(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer) 
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        result = widget.serialize(field, ['123'])
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 1)
        self.assertEqual(renderer.kw['subfields'][0], ('123', inner))
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], ['123'])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_with_sequence_widgets(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        inner = DummyField()
        field.children = [inner]
        sequence_field = DummyField()
        field.sequence_fields = [sequence_field]
        result = widget.serialize(field, ['123'])
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 1)
        self.assertEqual(renderer.kw['subfields'][0], ('123', sequence_field))
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], ['123'])
        self.assertEqual(renderer.template, widget.template)

    def test_deserialize_None(self):
        field = DummyField()
        inner_field = DummyField()
        field.children = [inner_field]
        widget = self._makeOne()
        result = widget.deserialize(field, None)
        self.assertEqual(result, [])
        self.assertEqual(field.sequence_fields, [])
        
    def test_deserialize_not_None(self):
        field = DummyField()
        inner_field = DummyField()
        inner_field.widget = DummyWidget()
        field.children = [inner_field]
        widget = self._makeOne()
        result = widget.deserialize(field, ['123'])
        self.assertEqual(result, ['123'])
        self.assertEqual(len(field.sequence_fields), 1)
        self.assertEqual(field.sequence_fields[0], inner_field)

    def test_handle_error(self):
        field = DummyField()
        widget = self._makeOne()
        inner_widget = DummyWidget()
        inner_invalid = DummyInvalid()
        inner_invalid.pos = 0
        error = DummyInvalid(inner_invalid)
        inner_field = DummyField()
        inner_field.widget = inner_widget
        field.sequence_fields = [inner_field]
        widget.handle_error(field, error)
        self.assertEqual(field.error, error)
        self.assertEqual(inner_widget.error, inner_invalid)

class TestFormWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import FormWidget
        return FormWidget(**kw)

    def test_template(self):
        form = self._makeOne()
        self.assertEqual(form.template, 'form')

class DummyRenderer(object):
    def __init__(self, result=''):
        self.result = result
    
    def __call__(self, template, **kw):
        self.template = template
        self.kw = kw
        return self.result
        
class DummyWidget(object):
    name = 'name'
    def deserialize(self, field, pstruct):
        return pstruct

    def handle_error(self, field, error):
        self.error = error

class DummySchema(object):
    pass

class DummyInvalid(object):
    pos = 0
    def __init__(self, *children):
        self.children = children
        
class DummyField(object):
    default = None
    error = None
    children = ()
    def __init__(self, schema=None, renderer=None):
        self.schema = schema
        self.renderer = renderer

    def clone(self):
        return self
    
        
