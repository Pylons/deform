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

class TestRaw(unittest.TestCase):
    def _makeOne(self, val):
        from deform.form import Raw
        return Raw(val)

    def test___html__(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.__html__(), 'abc')

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
