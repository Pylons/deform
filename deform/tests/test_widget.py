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
    def _makeOne(self, schema, renderer=None):
        from deform.widget import RadioChoiceWidget
        return RadioChoiceWidget(schema, renderer=renderer)
    
    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        widget.default = 'default'
        widget.serialize(None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], 'default')

    def test_serialize_not_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        cstruct = 'abc'
        widget.serialize(cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], cstruct)
        
    def test_deserialize_None(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize(None)
        self.assertEqual(result, '')

    def test_deserialize_other(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize('true')
        self.assertEqual(result, 'true')

class TestCheckedPasswordWidget(unittest.TestCase):
    def _makeOne(self, schema, renderer=None):
        from deform.widget import CheckedPasswordWidget
        return CheckedPasswordWidget(schema, renderer=renderer)
    
    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        widget.default = 'default'
        widget.serialize(None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], 'default')

    def test_serialize_None_no_default(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        widget.serialize(None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_deserialize_None(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize(None)
        self.assertEqual(result, '')

    def test_deserialize_nonmatching(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize({'password':'password', 'confirm':'not'})
        self.assertEqual(result, 'password')
        self.assertEqual(widget.error.msg,
                         'Password did not match confirmation')

    def test_deserialize_matching(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize({'password':'password',
                                     'confirm':'password'})
        self.assertEqual(result, 'password')
        self.assertEqual(widget.error, None)

class TestMappingWidget(unittest.TestCase):
    def _makeOne(self, schema, renderer=None):
        from deform.widget import MappingWidget
        return MappingWidget(schema, renderer=renderer)
    
    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        widget.serialize(None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], {})

    def test_serialize_not_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        cstruct = {'a':1}
        widget.serialize(cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_None(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize(None)
        self.assertEqual(result, {})

    def test_deserialize_non_None(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        inner_schema = DummySchema()
        inner_schema.name = 'a'
        inner = DummyWidget()
        inner.name = 'a'
        widget.widgets = [inner]
        pstruct = {'a':1}
        result = widget.deserialize(pstruct)
        self.assertEqual(result, {'a':1})

class TestSequenceWidget(unittest.TestCase):
    def _makeOne(self, schema, **kw):
        from deform.widget import SequenceWidget
        return SequenceWidget(schema, **kw)

    def test_prototype_unicode(self):
        import urllib
        renderer = DummyRenderer(u'abc')
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        widget.widgets=[None]
        result = widget.prototype()
        self.assertEqual(type(result), str)
        self.assertEqual(urllib.unquote(result), 'abc')

    def test_prototype_str(self):
        import urllib
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        widget.widgets=[None]
        result = widget.prototype()
        self.assertEqual(type(result), str)
        self.assertEqual(urllib.unquote(result), 'abc')

    def test_serialize_None(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        inner = DummyWidget()
        widget.widgets=[inner]
        result = widget.serialize()
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subwidgets']), 0)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], [])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_not_None(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        inner = DummyWidget()
        widget.widgets=[inner]
        result = widget.serialize(['123'])
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subwidgets']), 1)
        self.assertEqual(renderer.kw['subwidgets'][0], ('123', inner))
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], ['123'])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_with_sequence_widgets(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        inner = DummyWidget()
        widget.widgets=[inner]
        sequence_widget = DummyWidget()
        widget.sequence_widgets = [sequence_widget]
        result = widget.serialize(['123'])
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subwidgets']), 1)
        self.assertEqual(renderer.kw['subwidgets'][0], ('123', sequence_widget))
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], ['123'])
        self.assertEqual(renderer.template, widget.template)

    def test_deserialize_None(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        inner = DummyWidget()
        widget.widgets = [inner]
        result = widget.deserialize(None)
        self.assertEqual(result, [])
        self.assertEqual(widget.sequence_widgets, [])
        
    def test_deserialize_not_None(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        inner = DummyWidget()
        widget.widgets = [inner]
        result = widget.deserialize(['123'])
        self.assertEqual(result, ['123'])
        self.assertEqual(len(widget.sequence_widgets), 1)
        self.assertEqual(widget.sequence_widgets[0], inner)

    def test_handle_error(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        inner = DummyWidget()
        inner_invalid = DummyInvalid()
        inner_invalid.pos = 0
        error = DummyInvalid(inner_invalid)
        widget.sequence_widgets = [inner]
        widget.handle_error(error)
        self.assertEqual(widget.error, error)
        self.assertEqual(inner.error, inner_invalid)

class TestForm(unittest.TestCase):
    def _makeOne(self, schema, **kw):
        from deform.widget import Form
        return Form(schema, **kw)

    def test_ctor_string_buttons(self):
        schema = DummySchema()
        form = self._makeOne(schema, buttons=('a', 'b'))
        self.assertEqual(form.buttons[0].name, 'a')
        self.assertEqual(form.buttons[1].name, 'b')

    def test_ctor_nonstring_buttons(self):
        schema = DummySchema()
        form = self._makeOne(schema, buttons=(None, None))
        self.assertEqual(form.buttons[0], None)
        self.assertEqual(form.buttons[1], None)
    
    def test_ctor_defaults(self):
        schema = DummySchema()
        form = self._makeOne(schema)
        self.assertEqual(form.action, '.')
        self.assertEqual(form.method, 'POST')

    def test_ctor_nondefaults(self):
        schema = DummySchema()
        form = self._makeOne(schema, action='action', method='method')
        self.assertEqual(form.action, 'action')
        self.assertEqual(form.method, 'method')

class DummyRenderer(object):
    def __init__(self, result=''):
        self.result = result
    
    def __call__(self, template, **kw):
        self.template = template
        self.kw = kw
        return self.result
        
class DummyWidget(object):
    name = 'name'
    def clone(self):
        return self

    def deserialize(self, pstruct):
        return pstruct

    def handle_error(self, error):
        self.error = error

class DummySchema(object):
    typ = None
    name = 'name'
    title = 'title'
    description = 'description'
    required = True
    nodes = ()
    default = 'default'
    def __init__(self, exc=None):
        self.exc = exc
    def serialize(self, value):
        return value
    def deserialize(self, value):
        if self.exc:
            raise self.exc
        return value

class DummyWidgetType(object):
    def __init__(self, node, renderer=None):
        self.node = node
        self.renderer = renderer
        
class DummyInvalid(object):
    pos = 0
    def __init__(self, *children):
        self.children = children
        
class DummyField(object):
    default = None
    def __init__(self, schema=None, renderer=None):
        self.schema = schema
        self.renderer = renderer
        
