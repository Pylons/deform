import unittest

def invalid_exc(func, *arg, **kw):
    from deform.exception import Invalid
    try:
        func(*arg, **kw)
    except Invalid, e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover

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

class DummyRenderer(object):
    def __call__(self, template, **kw):
        self.template = template
        self.kw = kw
        
class DummyWidget(object):
    name = 'name'
    def clone(self):
        return self

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
        
