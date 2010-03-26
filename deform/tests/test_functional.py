import unittest

class TestFunctional(unittest.TestCase):
    def _makeSchema(self):
        from deform.schema import MappingSchema
        from deform.schema import SequenceSchema
        from deform.schema import SchemaNode
        from deform.schema import String
        from deform.schema import Boolean
        from deform.schema import Integer
    
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
        from deform.widget import Form
        return Form(schema)

    def _soupify(self, html):
        from BeautifulSoup import BeautifulSoup
        return BeautifulSoup(html)

    def test_serialize_empty(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        html = form.serialize()
        soup = self._soupify(html)
        form = soup.form
        self.assertEqual(form['action'], '.')
        labels = form.findAll('label')
        self.assertEqual(labels[0]['for'], 'name')
        self.assertEqual(labels[1]['for'], 'title')
        self.assertEqual(labels[2]['for'], 'cool')
        inputs = form.findAll('input')
        self.assertEqual(inputs[0]['name'], '_charset_')
        self.assertEqual(inputs[1]['name'], '__deform__')
        self.assertEqual(inputs[1]['value'], '')
        self.assertEqual(inputs[2]['name'], 'name')
        self.assertEqual(inputs[2]['value'], '')
        self.assertEqual(inputs[3]['name'], 'title')
        self.assertEqual(inputs[3]['value'], '')
        self.assertEqual(inputs[4]['name'], 'cool')
        self.assertEqual(inputs[4].get('checked'), 'True')
        self.assertEqual(inputs[5]['name'], '__start__')
        self.assertEqual(inputs[5]['value'], 'series:mapping')
        self.assertEqual(inputs[6]['name'], 'name')
        self.assertEqual(inputs[6]['value'], '')
        self.assertEqual(inputs[7]['name'], '__start__')
        self.assertEqual(inputs[7]['value'], 'dates:sequence')
        self.assertEqual(inputs[8]['name'], '__end__')
        self.assertEqual(inputs[8]['value'], 'dates:sequence')
        self.assertEqual(inputs[9]['name'], '__end__')
        self.assertEqual(inputs[9]['value'], 'series:mapping')

    def test_serialize_not_empty(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        html = form.serialize(
            {'cool':'false',
             'series':{'dates':[{'day':'21', 'month':'3', 'year':'2010'}]}})
        soup = self._soupify(html)
        form = soup.form
        self.assertEqual(form['action'], '.')
        labels = form.findAll('label')
        self.assertEqual(labels[0]['for'], 'name')
        self.assertEqual(labels[1]['for'], 'title')
        self.assertEqual(labels[2]['for'], 'cool')
        inputs = form.findAll('input')
        self.assertEqual(inputs[0]['name'], '_charset_')
        self.assertEqual(inputs[1]['name'], '__deform__')
        self.assertEqual(inputs[1]['value'], '')
        self.assertEqual(inputs[2]['name'], 'name')
        self.assertEqual(inputs[2]['value'], '')
        self.assertEqual(inputs[3]['name'], 'title')
        self.assertEqual(inputs[3]['value'], '')
        self.assertEqual(inputs[4]['name'], 'cool')
        self.assertEqual(inputs[4].get('checked'), None)
        self.assertEqual(inputs[5]['name'], '__start__')
        self.assertEqual(inputs[5]['value'], 'series:mapping')
        self.assertEqual(inputs[6]['name'], 'name')
        self.assertEqual(inputs[6]['value'], '')
        self.assertEqual(inputs[7]['name'], '__start__')
        self.assertEqual(inputs[7]['value'], 'dates:sequence')
        self.assertEqual(inputs[8]['name'], '__start__')
        self.assertEqual(inputs[8]['value'], 'date:mapping')
        self.assertEqual(inputs[9]['name'], 'month')
        self.assertEqual(inputs[9]['value'], '3')
        self.assertEqual(inputs[10]['name'], 'year')
        self.assertEqual(inputs[10]['value'], '2010')
        self.assertEqual(inputs[11]['name'], 'day')
        self.assertEqual(inputs[11]['value'], '21')
        self.assertEqual(inputs[12]['name'], '__end__')
        self.assertEqual(inputs[12]['value'], 'date:mapping')
        self.assertEqual(inputs[13]['name'], '__end__')
        self.assertEqual(inputs[13]['value'], 'dates:sequence')
        self.assertEqual(inputs[14]['name'], '__end__')
        self.assertEqual(inputs[14]['value'], 'series:mapping')

    def test_deserialize(self):
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
                    'cool': 'false',
                    'name': 'project1',
                    'title': 'Cool project'}
        self.assertEqual(result, expected)

    def test_validate(self):
        from deform.exception import FormValidationError
        schema = self._makeSchema()
        form = self._makeForm(schema)
        try:
            form.validate([])
        except FormValidationError, ve:
            e = ve.invalid_exc
        self.assertEqual(form.error, e)
        self.assertEqual(form.widgets[0].error, e.children[0])
        self.assertEqual(form.widgets[1].error, e.children[1])
        self.assertEqual(form.widgets[3].error, e.children[2])
        self.assertEqual(form.widgets[3].widgets[0].error,
                         e.children[2].children[0])
        self.assertEqual(
            ve.cstruct,
            {'series': {'dates': [], 'name': ''}, 'cool': 'false', 'name': '',
             'title': ''})
        
        
        
        
