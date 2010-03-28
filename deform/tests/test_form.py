import unittest

def validation_failure_exc(func, *arg, **kw):
    from deform.exception import ValidationFailure
    try:
        func(*arg, **kw)
    except ValidationFailure, e:
        return e
    else:
        raise AssertionError('Form error not raised') # pragma: no cover

class TestField(unittest.TestCase):
    def _makeOne(self, schema, renderer=None):
        from deform.form import Field
        return Field(schema, renderer=renderer)

    def test_ctor_defaults(self):
        from deform.template import default_renderer
        schema = DummySchema()
        field = self._makeOne(schema)
        self.assertEqual(field.schema, schema)
        self.assertEqual(field.renderer, default_renderer)
        self.assertEqual(field.name, 'name')
        self.assertEqual(field.title, 'title')
        self.assertEqual(field.default, 'sdefault')
        self.assertEqual(field.required, True)
        self.assertEqual(field.children, [])

    def test_ctor_with_children_in_schema(self):
        from deform.form import Field
        schema = DummySchema()
        node = DummySchema()
        schema.children = [node]
        field = self._makeOne(schema, renderer='abc')
        self.assertEqual(len(field.children), 1)
        child_field = field.children[0]
        self.assertEqual(child_field.__class__, Field)
        self.assertEqual(child_field.schema, node)
        self.assertEqual(child_field.renderer, 'abc')

    def test_ctor_schema_required(self):
        schema = DummySchema()
        schema.required = False
        field = self._makeOne(schema)
        self.assertEqual(field.default, 'sdefault')

    def test_widget_has_maker(self):
        schema = DummySchema()
        def maker():
            return 'a widget'
        schema.typ = DummyType(maker=maker)
        field = self._makeOne(schema)
        widget = field.widget
        self.assertEqual(widget, 'a widget')

    def test_widget_no_maker(self):
        from deform.widget import TextInputWidget
        schema = DummySchema()
        schema.typ = None
        field = self._makeOne(schema)
        widget = field.widget
        self.assertEqual(widget.__class__, TextInputWidget)

    def test_clone(self):
        schema = DummySchema()
        field = self._makeOne(schema, renderer='abc')
        child = DummyField()
        field.children = [child]
        field.foo = 1
        result = field.clone()
        self.failIf(result is field)
        self.assertEqual(result.renderer, 'abc')
        self.assertEqual(result.schema, schema)
        self.assertEqual(result.foo, 1)
        self.assertEqual(result.children, [child])
        self.assertEqual(result.children[0].cloned, True)

    def test___getitem__success(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        child = DummyField()
        field.children = [child]
        self.assertEqual(field['name'], child)
        
    def test___getitem__fail(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        child = DummyField()
        field.children = [child]
        self.assertRaises(KeyError, field.__getitem__, 'nope')

    def test_validate_succeeds(self):
        fields = [
            ('name', 'Name'),
            ('title', 'Title'),
            ]
        schema = DummySchema()
        field = self._makeOne(schema)
        field.widget = DummyWidget()
        result = field.validate(fields)
        self.assertEqual(result, {'name':'Name', 'title':'Title'})

    def test_validate_fails(self):
        from deform.exception import Invalid
        fields = [
            ('name', 'Name'),
            ('title', 'Title'),
            ]
        invalid = Invalid(None, None)
        schema = DummySchema(invalid)
        field = self._makeOne(schema)
        field.widget = DummyWidget()
        e = validation_failure_exc(field.validate, fields)
        self.assertEqual(field.widget.error, invalid)
        self.assertEqual(e.cstruct, {'name':'Name', 'title':'Title'})
        self.assertEqual(e.field, field)
        self.assertEqual(e.error, invalid)

class TestButton(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.form import Button
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


class DummyField(object):
    name = 'name'
    def __init__(self, schema=None, renderer=None):
        self.schema = schema
        self.renderer = renderer

    def clone(self):
        self.cloned = True
        return self

    def deserialize(self, pstruct):
        return pstruct

class DummySchema(object):
    typ = None
    name = 'name'
    title = 'title'
    description = 'description'
    required = True
    children = ()
    default = 'default'
    sdefault = 'sdefault'
    def __init__(self, exc=None):
        self.exc = exc
    def serialize(self, value):
        return value
    def deserialize(self, value):
        if self.exc:
            raise self.exc
        return value

class DummyType(object):
    def __init__(self, maker=None):
        self.default_widget_maker = maker
        
class DummyInvalid(object):
    def __init__(self, *children):
        self.children = children
        
class DummyWidget(object):
    def deserialize(self, field, pstruct):
        return pstruct

    def handle_error(self, field, e):
        self.error = e

