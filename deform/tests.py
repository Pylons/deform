import unittest

def invalid_exc(func, *arg, **kw):
    from deform import Invalid
    try:
        func(*arg, **kw)
    except Invalid, e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover

class TestFunctional(unittest.TestCase):
    def _makeSchema(self):
        from deform import MappingSchema
        from deform import SequenceSchema
        from deform import SchemaNode
        from deform import String
        from deform import Boolean
        from deform import Integer
    
        class DateSchema(MappingSchema):
            month = SchemaNode(Integer())
            year = SchemaNode(Integer())
            day = SchemaNode(Integer())

        class DatesSchema(SequenceSchema):
            date = DateSchema()

        class SeriesSchema(MappingSchema):
            name = SchemaNode(String())
            dates = DatesSchema()

        class MySchema(MappingSchema):
            name = SchemaNode(String())
            title = SchemaNode(String())
            cool = SchemaNode(Boolean(), default=True)
            series = SeriesSchema()

        schema = MySchema()
        return schema

    def _makeForm(self, schema):
        from deform import Form
        return Form(schema)

    def test_serialize_empty(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        html = form.serialize()
        lines = html.split('\n')
        self.assertEqual(
            lines[0],
            '<form name="" method="POST" action="." '
            'encoding="multipart/form-data">')
        self.assertEqual(
            lines[1],
            '<input type="text" name="name" value=""/>')
        self.assertEqual(
            lines[3],
            '<input type="checkbox" name="cool"/>')
        self.assertEqual(
            lines[4],
            '<input type="hidden" name="__start__" value="series:mapping">')
        self.assertEqual(
            lines[5],
            '<input type="text" name="name" value=""/>')

    def test_deserialize_empty(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        e = invalid_exc(form.deserialize, {})
        self.failUnless(e)

    def test_deserialize_ok(self):
        filled = {
            'name': 'project1',
            'title': 'Cool project',
            'series': {
                'name':'date series 1',
                'dates': [{'month':'10', 'day':'12', 'year':'2008'},
                          {'month':'10', 'day':'12', 'year':'2009'}],
                }
            }
        schema = self._makeSchema()
        form = self._makeForm(schema)
        result = form.deserialize(filled)
        expected = {'series':
                    {'dates': [{'year': '2008', 'day': '12', 'month': '10'},
                               {'year': '2009', 'day': '12', 'month': '10'}],
                     'name': 'date series 1'},
                    'cool': 'true',
                    'name': 'project1',
                    'title': 'Cool project'}
        self.assertEqual(result, expected)

