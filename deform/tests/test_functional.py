import unittest

class TestFunctional(unittest.TestCase):
    def _makeSchema(self):
        from colander import MappingSchema
        from colander import SequenceSchema
        from colander import SchemaNode
        from colander import String
        from colander import Boolean
        from colander import Date
    
        class DatesSchema(SequenceSchema):
            date = SchemaNode(Date())

        class SeriesSchema(MappingSchema):
            name = SchemaNode(String())
            dates = DatesSchema()

        class MySchema(MappingSchema):
            name = SchemaNode(String())
            title = SchemaNode(String())
            cool = SchemaNode(Boolean(), default=True, missing=True)
            series = SeriesSchema()

        schema = MySchema()
        return schema

    def _makeForm(self, schema):
        from deform.form import Form
        return Form(schema, formid='myform')

    def _soupify(self, html):
        from BeautifulSoup import BeautifulSoup
        return BeautifulSoup(html)

    def test_render_empty(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        html = form.render()
        soup = self._soupify(html)
        form = soup.form
        self.assertEqual(form['action'], '')
        inputs = form.findAll('input')
        self.assertEqual(inputs[0]['name'], '_charset_')
        self.assertEqual(inputs[1]['name'], '__formid__')
        self.assertEqual(inputs[1]['value'], 'myform')
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

    def test_render_not_empty(self):
        import datetime
        schema = self._makeSchema()
        form = self._makeForm(schema)
        appstruct =  {
            'cool':False,
            'series':{
                'dates':[datetime.date(2010, 3, 21)],
                }
            }
        html = form.render(appstruct)
        soup = self._soupify(html)
        form = soup.form
        self.assertEqual(form['action'], '')
        inputs = form.findAll('input')
        self.assertEqual(inputs[0]['name'], '_charset_')
        self.assertEqual(inputs[1]['name'], '__formid__')
        self.assertEqual(inputs[1]['value'], 'myform')
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
        self.assertEqual(inputs[8]['name'], 'date')
        self.assertEqual(inputs[8]['value'], '2010-03-21')
        self.assertEqual(inputs[9]['name'], '__end__')
        self.assertEqual(inputs[9]['value'], 'dates:sequence')
        self.assertEqual(inputs[10]['name'], '__end__')
        self.assertEqual(inputs[10]['value'], 'series:mapping')

    def test_widget_deserialize(self):
        filled = {
            'name': 'project1',
            'title': 'Cool project',
            'series': {
                'name':'date series 1',
                'dates': ['2008-10-12', '2009-10-12'],
                }
            }
        schema = self._makeSchema()
        form = self._makeForm(schema)
        result = form.widget.deserialize(form, filled)
        expected = {'series':
                    {'dates': ['2008-10-12', '2009-10-12'],
                     'name': 'date series 1'},
                    'cool': 'false',
                    'name': 'project1',
                    'title': 'Cool project'}
        self.assertEqual(result, expected)

    def test_validate(self):
        from colander import null
        from deform.exception import ValidationFailure
        schema = self._makeSchema()
        form = self._makeForm(schema)
        try:
            form.validate([])
        except ValidationFailure, ve:
            e = ve.error
        self.assertEqual(form.error, e)
        self.assertEqual(form.children[0].error, e.children[0])
        self.assertEqual(form.children[1].error, e.children[1])
        self.assertEqual(form.children[3].error, e.children[2])
        self.assertEqual(form.children[3].children[0].error,
                         e.children[2].children[0])
        self.assertEqual(
            ve.cstruct,
            {
                'series': {'dates': [], 'name': null},
                'cool': 'false',
                'name': null,
                'title': null,
             }
            )
        
        
        
        
