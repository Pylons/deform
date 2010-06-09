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
    def _getTargetClass(self):
        from deform.field import Field
        return Field
        
    def _makeOne(self, schema, **kw):
        cls = self._getTargetClass()
        return cls(schema, **kw)

    def test_ctor_defaults(self):
        from deform.template import default_renderer
        schema = DummySchema()
        field = self._makeOne(schema)
        self.assertEqual(field.schema, schema)
        self.assertEqual(field.renderer, default_renderer)
        self.assertEqual(field.name, 'name')
        self.assertEqual(field.title, 'title')
        self.assertEqual(field.required, True)
        self.assertEqual(field.order, 0)
        self.assertEqual(field.oid, 'deformField0')
        self.assertEqual(field.children, [])
        self.assertEqual(field.typ, schema.typ)

    def test_ctor_with_children_in_schema(self):
        from deform.field import Field
        schema = DummySchema()
        node = DummySchema()
        schema.children = [node]
        field = self._makeOne(schema, renderer='abc')
        self.assertEqual(len(field.children), 1)
        child_field = field.children[0]
        self.assertEqual(child_field.__class__, Field)
        self.assertEqual(child_field.schema, node)
        self.assertEqual(child_field.renderer, 'abc')

    def test_set_default_renderer(self):
        cls = self._getTargetClass()
        old = cls.default_renderer
        def new():
            return 'OK'
        try:
            cls.set_default_renderer(new)
            self.assertEqual(cls.default_renderer(), 'OK')
        finally:
            cls.set_default_renderer(old)

    def test_set_zpt_renderer(self):
        cls = self._getTargetClass()
        old = cls.default_renderer
        from pkg_resources import resource_filename
        template_dir = resource_filename('deform', 'templates/')
        class Field:
            oid = None
            name = None
        field = Field()
        try:
            cls.set_zpt_renderer(template_dir)
            self.failUnless(cls.default_renderer('hidden', field=field,
                                                 cstruct=None))
        finally:
            cls.set_default_renderer(old)

    def test_widget_has_maker(self):
        schema = DummySchema()
        def maker():
            return 'a widget'
        schema.typ = DummyType(maker=maker)
        field = self._makeOne(schema)
        widget = field.widget
        self.assertEqual(widget, 'a widget')

    def test_widget_no_maker_with_default_widget_maker(self):
        from deform.widget import MappingWidget
        from colander import Mapping
        schema = DummySchema() 
        schema.typ = Mapping()
        field = self._makeOne(schema)
        widget = field.widget
        self.assertEqual(widget.__class__, MappingWidget)

    def test_widget_no_maker_no_default_widget_maker(self):
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
        self.assertEqual(result.order, 1)
        self.assertEqual(result.oid, 'deformField1')
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

    def test_errormsg_error_None(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        self.assertEqual(field.errormsg, None)
            
    def test_errormsg_error_not_None(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        field.error = DummyInvalid('abc')
        self.assertEqual(field.errormsg, 'abc')

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

    def test_validate_fails_widgeterror(self):
        from colander import Invalid
        fields = [
            ('name', 'Name'),
            ('title', 'Title'),
            ]
        invalid = Invalid(None, None, dict(fields))
        schema = DummySchema()
        field = self._makeOne(schema)
        field.widget = DummyWidget(exc=invalid)
        e = validation_failure_exc(field.validate, fields)
        self.assertEqual(field.widget.error, invalid)
        self.assertEqual(e.cstruct, dict(fields))
        self.assertEqual(e.field, field)
        self.assertEqual(e.error, invalid)

    def test_validate_fails_schemaerror(self):
        from colander import Invalid
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

    def test_validate_fails_widgeterror_and_schemaerror(self):
        from colander import Invalid
        fields = [
            ('name', 'Name'),
            ('title', 'Title'),
            ]
        widget_invalid = Invalid(None, None, dict(fields))
        schema_invalid = Invalid(None, None)
        schema = DummySchema(schema_invalid)
        field = self._makeOne(schema)
        field.widget = DummyWidget(exc=widget_invalid)
        e = validation_failure_exc(field.validate, fields)
        self.assertEqual(field.widget.error, schema_invalid)
        self.assertEqual(e.cstruct, dict(fields))
        self.assertEqual(e.field, field)
        self.assertEqual(e.error, schema_invalid)

    def test_render(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        widget = field.widget = DummyWidget()
        self.assertEqual(field.render('abc'), 'abc')
        self.assertEqual(widget.rendered, 'writable')

    def test_render_readonly(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        widget = field.widget = DummyWidget()
        self.assertEqual(field.render('abc', readonly=True), 'abc')
        self.assertEqual(widget.rendered, 'readonly')

    def test_serialize(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        widget = field.widget = DummyWidget()
        self.assertEqual(field.serialize('abc'), 'abc')
        self.assertEqual(widget.rendered, 'writable')

    def test_serialize_null(self):
        from colander import null
        schema = DummySchema()
        field = self._makeOne(schema)
        widget = field.widget = DummyWidget()
        self.assertEqual(field.serialize(null), null)
        self.assertEqual(widget.rendered, 'writable')

    def test_deserialize(self):
        cstruct = {'name':'Name', 'title':'Title'}
        schema = DummySchema()
        field = self._makeOne(schema)
        field.widget = DummyWidget()
        result = field.deserialize(cstruct)
        self.assertEqual(result, {'name':'Name', 'title':'Title'})

    def test___repr__(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        r = repr(field)
        self.failUnless(r.startswith('<deform.field.Field object at '))
        self.failUnless(r.endswith("(schemanode 'name')>"))

class DummyField(object):
    name = 'name'
    oid = 'oid'
    def __init__(self, schema=None, renderer=None):
        self.schema = schema
        self.renderer = renderer

    def clone(self):
        self.cloned = True
        return self

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
    def deserialize(self, value):
        if self.exc:
            raise self.exc
        return value

    def serialize(self, value):
        return value

class DummyType(object):
    def __init__(self, maker=None):
        self.widget_maker = maker
        
class DummyWidget(object):
    rendered = None
    def __init__(self, exc=None):
        self.exc = exc

    def deserialize(self, field, pstruct):
        if self.exc is not None:
            raise self.exc
        return pstruct

    def serialize(self, field, cstruct=None, readonly=True):
        self.rendered = readonly and 'readonly' or 'writable'
        return cstruct

    def handle_error(self, field, e):
        self.error = e

class DummyInvalid(object):
    def __init__(self, msg=None):
        self.msg = msg
