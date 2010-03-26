import unittest

def validation_failure_exc(func, *arg, **kw):
    from deform.exception import ValidationFailure
    try:
        func(*arg, **kw)
    except ValidationFailure, e:
        return e
    else:
        raise AssertionError('Form error not raised') # pragma: no cover

class TestWidget(unittest.TestCase):
    def _makeOne(self, schema, renderer=None):
        from deform.widget import Widget
        return Widget(schema, renderer=renderer)

    def test_ctor_defaults(self):
        from deform.template import default_renderer
        schema = DummySchema()
        widget = self._makeOne(schema)
        self.assertEqual(widget.schema, schema)
        self.assertEqual(widget.renderer, default_renderer)
        self.assertEqual(widget.name, 'name')
        self.assertEqual(widget.title, 'title')
        self.assertEqual(widget.widgets, [])
        self.assertEqual(widget.default, None)
        self.assertEqual(widget.required, True)

    def test_ctor_schema_required(self):
        schema = DummySchema()
        schema.required = False
        widget = self._makeOne(schema)
        self.assertEqual(widget.default, 'default')

    def test_ctor_node_has_widget_type(self):
        schema = DummySchema()
        node = DummySchema()
        node.widget_type = DummyWidgetType
        schema.nodes = [node]
        widget = self._makeOne(schema, renderer='abc')
        self.assertEqual(len(widget.widgets), 1)
        child_widget = widget.widgets[0]
        self.assertEqual(child_widget.__class__, DummyWidgetType)
        self.assertEqual(child_widget.node, node)
        self.assertEqual(child_widget.renderer, 'abc')
        
    def test_ctor_type_has_widget_type(self):
        schema = DummySchema()
        node = DummySchema()
        node.widget_type = DummyWidgetType
        schema.nodes = [node]
        widget = self._makeOne(schema, renderer='abc')
        self.assertEqual(len(widget.widgets), 1)
        child_widget = widget.widgets[0]
        self.assertEqual(child_widget.__class__, DummyWidgetType)
        self.assertEqual(child_widget.node, node)
        self.assertEqual(child_widget.renderer, 'abc')

    def test_clone(self):
        schema = DummySchema()
        widget = self._makeOne(schema, renderer='abc')
        child = DummyWidget()
        widget.widgets = [child]
        widget.foo = 1
        result = widget.clone()
        self.failIf(result is widget)
        self.assertEqual(result.renderer, 'abc')
        self.assertEqual(result.schema, schema)
        self.assertEqual(result.foo, 1)
        self.assertEqual(result.widgets, [child])

    def test___getitem__success(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        child = DummyWidget()
        widget.widgets = [child]
        self.assertEqual(widget['name'], child)
        
    def test___getitem__fail(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        child = DummyWidget()
        widget.widgets = [child]
        self.assertRaises(KeyError, widget.__getitem__, 'nope')

    def test_serialize(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        self.assertRaises(NotImplementedError, widget.serialize)
        
    def test_deserialize(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        self.assertRaises(NotImplementedError, widget.deserialize)

    def test_validate_succeeds(self):
        fields = [
            ('name', 'Name'),
            ('title', 'Title'),
            ]
        schema = DummySchema()
        widget = self._makeOne(schema)
        widget.deserialize = lambda x: x
        result = widget.validate(fields)
        self.assertEqual(result, {'name':'Name', 'title':'Title'})

    def test_validate_fails(self):
        from deform.exception import Invalid
        fields = [
            ('name', 'Name'),
            ('title', 'Title'),
            ]
        invalid = Invalid(None, None)
        schema = DummySchema(invalid)
        widget = self._makeOne(schema)
        widget.deserialize = lambda x: x
        e = validation_failure_exc(widget.validate, fields)
        self.assertEqual(widget.error, invalid)
        self.assertEqual(e.cstruct, {'name':'Name', 'title':'Title'})
        self.assertEqual(e.widget, widget)
        self.assertEqual(e.error, invalid)

    def test_handle_error(self):
        inner_schema = DummySchema()
        outer_schema = DummySchema()
        inner_widget = self._makeOne(inner_schema)
        outer_widget = self._makeOne(outer_schema)
        outer_widget.widgets = [inner_widget]
        inner_error = DummyInvalid()
        inner_error.node = inner_schema
        outer_error = DummyInvalid(inner_error)
        outer_widget.handle_error(outer_error)
        self.assertEqual(inner_widget.error, inner_error)

class TestTextInputWidget(unittest.TestCase):
    def _makeOne(self, schema, renderer=None):
        from deform.widget import TextInputWidget
        return TextInputWidget(schema, renderer=renderer)
    
    def test_serialize_None_no_default(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        widget = self._makeOne(schema, renderer=renderer)
        widget.serialize(None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['widget'], widget)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_None_with_default(self):
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
        
    def test_deserialize_strip(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        pstruct = ' abc '
        result = widget.deserialize(pstruct)
        self.assertEqual(result, 'abc')

    def test_deserialize_no_strip(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        widget.strip = False
        pstruct = ' abc '
        result = widget.deserialize(pstruct)
        self.assertEqual(result, ' abc ')

    def test_deserialize_None(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize(None)
        self.assertEqual(result, '')

class TestCheckboxWidget(unittest.TestCase):
    def _makeOne(self, schema, renderer=None):
        from deform.widget import CheckboxWidget
        return CheckboxWidget(schema, renderer=renderer)
    
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
        self.assertEqual(result, 'false')

    def test_deserialize_true_val(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize('true')
        self.assertEqual(result, 'true')

    def test_deserialize_false_val(self):
        schema = DummySchema()
        widget = self._makeOne(schema)
        result = widget.deserialize('false')
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

class TestButton(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import Button
        return Button(**kw)

    def test_ctor_title_None(self):
        button = self._makeOne()
        self.assertEqual(button.title, 'Submit')

    def test_ctor_value_None(self):
        button = self._makeOne()
        self.assertEqual(button.value, 'submit')

    def test_ctor(self):
        button = self._makeOne(name='name', title='title', value='value')
        self.assertEqual(button.value, 'value')
        self.assertEqual(button.name, 'name')
        self.assertEqual(button.title, 'title')

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
    def __init__(self, *children):
        self.children = children
        
