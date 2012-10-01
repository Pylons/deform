import unittest

class TestForm(unittest.TestCase):
    def _makeOne(self, schema, **kw):
        from deform.form import Form
        return Form(schema, **kw)

    def test_ctor_buttons_strings(self):
        from deform.widget import FormWidget
        schema = DummySchema()
        form = self._makeOne(schema, renderer='abc', action='action',
                             method='method', buttons=('button',),
                             formid='formid')
        self.assertEqual(form.schema, schema)
        self.assertEqual(form.renderer, 'abc')
        self.assertEqual(form.action, 'action')
        self.assertEqual(form.method, 'method')
        self.assertEqual(form.formid, 'formid')
        self.assertEqual(form.widget.__class__, FormWidget)
        self.assertEqual(len(form.buttons), 1)
        button = form.buttons[0]
        self.assertEqual(button.name, 'button')
        self.assertEqual(button.value, 'button')
        self.assertEqual(button.title, 'Button')
        self.assertEqual(button.css_class, None)

    def test_ctor_buttons_notstrings(self):
        from deform.widget import FormWidget
        schema = DummySchema()
        form = self._makeOne(schema, renderer='abc', action='action',
                             method='method', buttons=(None,), formid='formid')
        self.assertEqual(form.schema, schema)
        self.assertEqual(form.renderer, 'abc')
        self.assertEqual(form.action, 'action')
        self.assertEqual(form.method, 'method')
        self.assertEqual(form.formid, 'formid')
        self.assertEqual(form.widget.__class__, FormWidget)
        self.assertEqual(len(form.buttons), 1)
        button = form.buttons[0]
        self.assertEqual(button, None)

    def test_ctor_passes_unknown_kwargs(self):
        schema = DummySchema()
        schema.children = [DummySchema()]
        form = self._makeOne(schema, a='a', b='b')
        self.assertEqual(form.schema, schema)
        self.assertEqual(form.a, 'a')
        self.assertEqual(form.b, 'b')
        child = form.children[0]
        self.assertEqual(child.a, 'a')
        self.assertEqual(child.b, 'b')

    def test_ctor_autocomplete_default(self):
        schema = DummySchema()
        schema.children = [DummySchema()]
        form = self._makeOne(schema)
        self.assertEqual(form.autocomplete, None)

    def test_ctor_autocomplete_None(self):
        schema = DummySchema()
        schema.children = [DummySchema()]
        form = self._makeOne(schema, autocomplete=None)
        self.assertEqual(form.autocomplete, None)

    def test_ctor_autocomplete_True(self):
        schema = DummySchema()
        schema.children = [DummySchema()]
        form = self._makeOne(schema, autocomplete=True)
        self.assertEqual(form.autocomplete, 'on')

    def test_ctor_autocomplete_False(self):
        schema = DummySchema()
        schema.children = [DummySchema()]
        form = self._makeOne(schema, autocomplete=False)
        self.assertEqual(form.autocomplete, 'off')

class TestIssues(unittest.TestCase):

    def test_issue_54(self):
        import deform
        import colander
        class LoginForm(colander.Schema):
            username = colander.SchemaNode(colander.String())
            password = colander.SchemaNode(colander.String(),
                                           widget=deform.widget.PasswordWidget())
        def validate_password(node, d):
            raise colander.Invalid(node,
                                   'Username does not match password')
        loginform = LoginForm(validator=validate_password)
        data = [('__formid__', 'deform'),
                ('username', 'kai'),
                ('password', '123')]
        try:
            deform.Form(loginform).validate(data)
        except deform.ValidationFailure as e:
            rendered = e.render()
            self.assertTrue(
                '<p class="errorMsg">'
                'Username does not match password'
                '</p>' in rendered
            )

    def test_issue_71(self):
        import deform
        import colander
        from bs4 import BeautifulSoup

        schema = colander.MappingSchema(title='SCHEMA_TITLE')
        form = deform.Form(schema)
        html = form.render(colander.null)

        # check that title occurs exactly once in rendered output
        soup = BeautifulSoup(html)
        self.assertEqual(len([ string for string in soup.strings
                               if schema.title in string
                               ]),
                         1)

class TestButton(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.form import Button
        return Button(**kw)

    def test_ctor_title_None(self):
        button = self._makeOne()
        self.assertEqual(button.title, 'Submit')

    def test_ctor_type_None(self):
        button = self._makeOne()
        self.assertEqual(button.type, 'submit')

    def test_ctor_value_None(self):
        button = self._makeOne()
        self.assertEqual(button.value, 'submit')

    def test_name_with_space(self):
        button = self._makeOne(name="log\tin as a user")
        self.assertEqual(button.name, 'log_in_as_a_user')
        self.assertEqual(button.value, 'log_in_as_a_user')

    def test_ctor(self):
        button = self._makeOne(name='name', title='title',
                               type='type', value='value', disabled=True,
                               css_class='css-class')
        self.assertEqual(button.value, 'value')
        self.assertEqual(button.name, 'name')
        self.assertEqual(button.title, 'title')
        self.assertEqual(button.type, 'type')
        self.assertEqual(button.disabled, True)
        self.assertEqual(button.css_class, 'css-class')

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

    def serialize(self, appstruct):
        return appstruct

    def cstruct_children(self, cstruct):
        import colander
        children = []
        for child in self.children:
            children.append(colander.null)
        return children
        
