from colander import OneOf
from paste.httpserver import serve
from repoze.bfg.configuration import Configurator
from deform.schema import MappingSchema
from deform.schema import SequenceSchema
from deform.schema import SchemaNode
from deform.schema import String
from deform.schema import Boolean
from deform.schema import Integer
from deform.widget import Form
from deform.widget import ValidationError

def form_view(request):
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
        name = SchemaNode(String(), description='Name')
        title = SchemaNode(String(), validator=OneOf(('a', 'b')))
        cool = SchemaNode(Boolean(), default=True)
        series = SeriesSchema()

    schema = MySchema()
    form = Form(schema, buttons=('submit',))

    if 'submit' in request.POST:
        fields = request.POST.items()
        try:
            form.validate(fields)
        except ValidationError, e:
            cstruct = e.cstruct
            return {'form':form.serialize(cstruct)}
        return {'form':'OK'}
            
    return {'form':form.serialize()}

if __name__ == '__main__':
    config = Configurator()
    config.begin()
    config.add_view(form_view, renderer='form.pt')
    config.add_static_view('static', 'deform:static')
    config.end()
    app = config.make_wsgi_app()
    serve(app)
    
