import colander

from paste.httpserver import serve
from repoze.bfg.configuration import Configurator

from deform.exception import ValidationFailure

from deform.schema import MappingSchema
from deform.schema import SequenceSchema
from deform.schema import SchemaNode
from deform.schema import String
from deform.schema import Boolean
from deform.schema import Integer

from deform import widget


LONG_DESC = """
The name of the thing.  This is a pretty long line, and hopefully I won't
need to type too much more of it because it's pretty boring to type this kind
of thing """

class DateSchema(MappingSchema):
    month = SchemaNode(Integer())
    year = SchemaNode(Integer())
    day = SchemaNode(Integer())

class DatesSchema(SequenceSchema):
    date = DateSchema()
    #date = SchemaNode(String())

class SeriesSchema(MappingSchema):
    name = SchemaNode(String())
    dates = DatesSchema()

class MySchema(MappingSchema):
    name = SchemaNode(String(), description=LONG_DESC)
    title = SchemaNode(String(), validator=colander.OneOf(('a', 'b')),
                       description=LONG_DESC)
    password = SchemaNode(String(), validator=colander.Length(5))
    cool = SchemaNode(Boolean(), default=True)
    series = SeriesSchema()
    color = SchemaNode(String(), validator=colander.OneOf(('red', 'blue')))

def form_view(request):
    schema = MySchema()
    schema['color'].widget_type = widget.RadioChoiceWidget
    schema['password'].widget_type = widget.CheckedPasswordWidget

    form = widget.Form(schema, buttons=('submit',))
    form['title'].size = 40
    form['color'].values = (('red', 'Red'),('green', 'Green'),('blue', 'Blue'))

    if 'submit' in request.POST:
        fields = request.POST.items()
        import pprint
        pprint.pprint(fields)
        try:
            form.validate(fields)
        except ValidationFailure, e:
            return {'form':e.serialize()}
        return {'form':'OK'}
            
    return {'form':form.serialize()}

if __name__ == '__main__':
    settings = dict(reload_templates=True)
    config = Configurator(settings=settings)
    config.begin()
    config.add_view(form_view, renderer='form.pt')
    config.add_view(form_view, name='bfg', renderer='bfg.pt')
    config.add_static_view('static', 'deform:static')
    config.end()
    app = config.make_wsgi_app()
    serve(app)
    
