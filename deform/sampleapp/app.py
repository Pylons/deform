import datetime
import pprint

from repoze.bfg.configuration import Configurator
import colander

from paste.httpserver import serve

from deform import schema
from deform import widget
from deform import form
from deform import exception

LONG_DESC = """
The name of the thing.  This is a pretty long line, and hopefully I won't
need to type too much more of it because it's pretty boring to type this kind
of thing """

class MemoryTmpStore(dict):
    def preview_url(self, uid):
        return None

memory = MemoryTmpStore()

class DatesSchema(schema.SequenceSchema):
    date = schema.SchemaNode(schema.Date())

class SeriesSchema(schema.MappingSchema):
    name = schema.SchemaNode(schema.String())
    dates = DatesSchema()

class FileUploads(schema.SequenceSchema):
    file = schema.SchemaNode(schema.FileData())

class MySchema(schema.MappingSchema):
    name = schema.SchemaNode(schema.String(), description=LONG_DESC)
    title = schema.SchemaNode(schema.String(),
                              validator=colander.Length(max=10),
                              description=LONG_DESC)
    password = schema.SchemaNode(schema.String(),
                                 validator=colander.Length(min=5))
    cool = schema.SchemaNode(schema.Boolean(), default=True)
    series = SeriesSchema()
    color = schema.SchemaNode(schema.String(),
                              validator=colander.OneOf(('red', 'blue')))
    uploads = FileUploads()

def validate_form(form, value):
    if value['name'] != value['title']:
        exc = exception.Invalid(form, 'Name does not match title')
        exc['title'] = 'Does not match title'
        exc['name'] = 'Does not match name'
        raise exc

def form_view(request):
    # Create a schema; when the form is submitted, we want to assert
    # that the name must match the title; we use a validator for the
    # entire form by assigning it a validator
    schema = MySchema(validator=validate_form)

    # Create a form; it will have a single button named submit.
    myform = form.Form(schema, buttons=('submit',))

    # Associate widgets with fields in the form
    myform['password'].widget = widget.CheckedPasswordWidget()
    myform['title'].widget = widget.TextInputWidget(size=40)
    myform['color'].widget = widget.RadioChoiceWidget(
        values=(('red', 'Red'),('green', 'Green'),('blue', 'Blue')))
    myform['uploads']['file'].widget = widget.FileUploadWidget(memory)

    # Handle the request
    if 'submit' in request.POST:
        # This was a form submission
        fields = request.POST.items()
        try:
            converted = myform.validate(fields)
        except exception.ValidationFailure, e:
            # Validation failed
            return {'form':e.render()}
        # Validation succeeded
        return {'form':pprint.pformat(converted)}

    # This was not a form submission; render the form "normally".
    appstruct = {'name':'Fred',
                'series':{'name':'series 1',
                          'dates':[datetime.datetime.now()]},
                'uploads':[{'uid':'/communities/myfile', 'filename':'myfile'}]}
    # We turn this into an "edit" form by passing an "appstruct"
    # (default application values related to the schema) to the
    # "render" method.  If this were an "add" form, we'd wouldn't
    # supply an appstruct, allowing the form to render without
    # prefilled fields.
    return {'form':myform.render(appstruct)}

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
    
