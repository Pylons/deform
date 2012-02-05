import unittest

def validation_failure_exc(func, *arg, **kw):
    from deform.exception import ValidationFailure
    try:
        func(*arg, **kw)
    except ValidationFailure as e:
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

    def test_ctor_with_resource_registry(self):
        from deform.field import Field
        schema = DummySchema()
        node = DummySchema()
        schema.children = [node]
        field = self._makeOne(schema, resource_registry='abc')
        self.assertEqual(len(field.children), 1)
        child_field = field.children[0]
        self.assertEqual(child_field.__class__, Field)
        self.assertEqual(child_field.schema, node)
        self.assertEqual(child_field.resource_registry, 'abc')

    def test_ctor_with_unknown_kwargs(self):
        from deform.field import Field
        schema = DummySchema()
        node = DummySchema()
        schema.children = [node]
        field = self._makeOne(schema, foo='foo', bar='bar')
        self.assertEqual(len(field.children), 1)
        child_field = field.children[0]
        self.assertEqual(field.foo, 'foo')
        self.assertEqual(field.bar, 'bar')
        self.assertEqual(child_field.__class__, Field)
        self.assertEqual(child_field.schema, node)
        self.assertEqual(child_field.foo, 'foo')
        self.assertEqual(child_field.bar, 'bar')

    def test_translate_renderer_has_no_translator(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        self.assertEqual(field.translate('term'), 'term')

    def test_translate_renderer_has_translator(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        field.renderer.translate = lambda foo: 'translated'
        self.assertEqual(field.translate('term'), 'translated')

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

    def test_set_default_resource_registry(self):
        cls = self._getTargetClass()
        old = cls.default_resource_registry
        try:
            cls.set_default_resource_registry('OK')
            self.assertEqual(cls.default_resource_registry, 'OK')
        finally:
            cls.set_default_resource_registry(old)

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
            self.assertTrue(cls.default_renderer('hidden', field=field,
                                                 cstruct=None))
        finally:
            cls.set_default_renderer(old)

    def test_widget_uses_schema_widget(self):
        widget = DummyWidget()
        schema = DummySchema()
        schema.widget = widget
        schema.typ = DummyType()
        field = self._makeOne(schema)
        widget = field.widget
        self.assertEqual(widget, widget)

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

    def test_widget_no_maker_with_derived_from_default_field(self):
        from deform.widget import SequenceWidget
        from colander import Sequence

        class CustomSequence(Sequence):
            pass

        schema = DummySchema() 
        schema.typ = CustomSequence()
        field = self._makeOne(schema)
        widget = field.widget
        self.assertEqual(widget.__class__, SequenceWidget)

    def test_widget_no_maker_no_default_widget_maker(self):
        from deform.widget import TextInputWidget
        schema = DummySchema()
        schema.typ = None
        field = self._makeOne(schema)
        widget = field.widget
        self.assertEqual(widget.__class__, TextInputWidget)

    def test_set_widgets_emptystring(self):
        schema = DummySchema()
        field = self._makeOne(schema, renderer='abc')
        widget = DummyWidget()
        field.set_widgets({'':widget})
        self.assertEqual(field.widget, widget)

    def test_set_widgets_emptystring_and_children(self):
        schema = DummySchema()
        field = self._makeOne(schema, renderer='abc')
        child1 = DummyField(name='child1')
        child2 = DummyField(name='child2')
        field.children = [child1, child2]
        widget = DummyWidget()
        widget1 = DummyWidget()
        widget2 = DummyWidget()
        field.set_widgets({'':widget,
                           'child1':widget1,
                           'child2':widget2})
        self.assertEqual(field.widget, widget)
        self.assertEqual(child1.widget, widget1)
        self.assertEqual(child2.widget, widget2)

    def test_set_widgets_childrenonly(self):
        schema = DummySchema()
        field = self._makeOne(schema, renderer='abc')
        child1 = DummyField(name='child1')
        child2 = DummyField(name='child2')
        field.children = [child1, child2]
        widget1 = DummyWidget()
        widget2 = DummyWidget()
        field.set_widgets({'child1':widget1,
                           'child2':widget2})
        self.assertEqual(child1.widget, widget1)
        self.assertEqual(child2.widget, widget2)

    def test_set_widgets_splat(self):
        schema = DummySchema()
        field = self._makeOne(schema, renderer='abc')
        child1 = DummyField(name='child1')
        field.children = [child1]
        widget1 = DummyWidget()
        field.set_widgets({'*':widget1})
        self.assertEqual(child1.widget, widget1)

    def test_set_widgets_nested(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        schema1 = DummySchema()
        schema1.name = 'child1'
        child1 = self._makeOne(schema1)
        schema2 = DummySchema()
        schema2.name = 'child2'
        child2 = self._makeOne(schema2)
        schema3 = DummySchema()
        schema3.name = 'child3'
        child3 = self._makeOne(schema3)
        schema4 = DummySchema()
        schema4.name = 'child4'
        child4 = self._makeOne(schema4)
        field.children = [child1, child2]
        child1.children = [child3]
        child2.children = [child4]
        widget1 = DummyWidget()
        widget2 = DummyWidget()
        widget3 = DummyWidget()
        widget4 = DummyWidget()
        field.set_widgets({'child1':widget1,
                           'child1.child3':widget3,
                           'child2':widget2,
                           'child2.child4':widget4})
        self.assertEqual(child1.widget, widget1)
        self.assertEqual(child2.widget, widget2)
        self.assertEqual(child3.widget, widget3)
        self.assertEqual(child4.widget, widget4)

    def test_set_widgets_complex_nonempty_key_no_children(self):
        schema = DummySchema()
        field = self._makeOne(schema, renderer='abc')
        child1 = DummyField(name='child1')
        child2 = DummyField(name='child2')
        field.children = [child1, child2]
        widget1 = DummyWidget()
        widget2 = DummyWidget()
        field.set_widgets({'child1':widget1,
                           'child2':widget2})
        self.assertEqual(child1.widget, widget1)
        self.assertEqual(child2.widget, widget2)

    def test_get_widget_requirements(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        field.widget.requirements = (('abc', '123'), ('ghi', '789'))
        child1 = DummyField(name='child1')
        field.children = [child1]
        result = field.get_widget_requirements()
        self.assertEqual(result,
                         [('abc', '123'), ('ghi', '789'), ('def', '456')])

    def test_get_widget_resources(self):
        def resource_registry(requirements):
            self.assertEqual(requirements, [ ('abc', '123') ])
            return 'OK'
        schema = DummySchema()
        field = self._makeOne(schema)
        field.widget.requirements = ( ('abc', '123') ,)
        field.resource_registry = resource_registry
        result = field.get_widget_resources()
        self.assertEqual(result, 'OK')

    def test_clone(self):
        schema = DummySchema()
        field = self._makeOne(schema, renderer='abc')
        child = DummyField()
        field.children = [child]
        field.foo = 1
        result = field.clone()
        self.assertFalse(result is field)
        self.assertEqual(result.order, 1)
        self.assertEqual(result.oid, 'deformField1')
        self.assertEqual(result.renderer, 'abc')
        self.assertEqual(result.schema, schema)
        self.assertEqual(result.foo, 1)
        self.assertEqual(result.children, [child])
        self.assertEqual(result.children[0].cloned, True)

    def test___iter__(self):
        schema = DummySchema()
        field = self._makeOne(schema)
        child = DummyField()
        child2 = DummyField()
        field.children = [child, child2]
        result = list(field.__iter__())
        self.assertEqual(result, [child, child2])

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
        self.assertTrue(r.startswith('<deform.field.Field object at '))
        self.assertTrue(r.endswith("(schemanode 'name')>"))

class DummyField(object):
    oid = 'oid'
    requirements = ( ('abc', '123'), ('def', '456'))
    def __init__(self, schema=None, renderer=None, name='name'):
        self.schema = schema
        self.renderer = renderer
        self.name = name

    def clone(self):
        self.cloned = True
        return self

    def get_widget_requirements(self, L=None):
        return self.requirements

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
