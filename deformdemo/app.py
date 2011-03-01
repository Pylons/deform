# -*- coding: utf-8 -*-

""" A Pyramid app that demonstrates various Deform widgets and
capabilities """

import inspect
import sys
import csv
import StringIO

from pkg_resources import resource_filename

from pyramid.config import Configurator
from pyramid.renderers import get_renderer
from pyramid.i18n import get_localizer
from pyramid.i18n import get_locale_name
from pyramid.response import Response
from pyramid.threadlocal import get_current_request
from pyramid.url import resource_url
from pyramid.view import view_config

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

import deform
import colander

from translationstring import TranslationStringFactory

_ = TranslationStringFactory('deform')
css = HtmlFormatter().get_style_defs('.highlight')

def translator(term):
    return get_localizer(get_current_request()).translate(term)

deform_template_dir = resource_filename('deform', 'templates/')

deform.Form.set_zpt_renderer(
    deform_template_dir,
    translator=translator,
    )

class demonstrate(object):
    def __init__(self, title):
        self.title = title

    def __call__(self, method):
        method.demo = self.title
        return method

class DeformDemo(object):
    def __init__(self, request):
        self.request = request
        self.macros = get_renderer('templates/main.pt').implementation().macros

    def render_form(self, form, appstruct=colander.null, submitted='submit',
                    success=None, readonly=False):

        captured = None

        if submitted in self.request.POST:
            # the request represents a form submission
            try:
                # try to validate the submitted values
                controls = self.request.POST.items()
                captured = form.validate(controls)
                if success:
                    response = success()
                    if response is not None:
                        return response
                html = form.render(captured)
            except deform.ValidationFailure, e:
                # the submitted values could not be validated
                html = e.render()

        else:
            # the request requires a simple form rendering
            html = form.render(appstruct, readonly=readonly)

        if self.request.is_xhr:
            return Response(html)

        code, start, end = self.get_code(2)

        reqts = form.get_widget_resources()

        # values passed to template for rendering
        return {
            'form':html,
            'captured':repr(captured),
            'code': code,
            'start':start,
            'end':end,
            'demos':self.get_demos(),
            'showmenu':True,
            'title':self.get_title(),
            'css_links':reqts['css'],
            'js_links':reqts['js'],
            }

    def get_code(self, level):
        frame = sys._getframe(level)
        lines, start = inspect.getsourcelines(frame.f_code)
        end = start + len(lines)
        code = ''.join(lines)
        code = unicode(code, 'utf-8')
        formatter = HtmlFormatter()
        return highlight(code, PythonLexer(), formatter), start, end

    @view_config(name='thanks.html')
    def thanks(self):
        return Response(
            '<html><body><p>Thanks!</p><small>'
            '<a href="..">Up</a></small></body></html>')

    @view_config(name='allcode', renderer='templates/code.pt')
    def allcode(self):
        params = self.request.params
        start = params.get('start')
        end = params.get('end')
        hl_lines = None
        if start and end:
            start = int(start)
            end = int(end)
            hl_lines = list(range(start, end))
        code = open(inspect.getsourcefile(self.__class__), 'r').read()
        code = code.decode('utf-8')
        formatter = HtmlFormatter(linenos='table', lineanchors='line',
                                  hl_lines=hl_lines)
        html = highlight(code, PythonLexer(), formatter)
        return {'code':html, 'showmenu':False}

    def get_title(self):
        # gross hack; avert your eyes
        frame = sys._getframe(3)
        attr = frame.f_locals['attr']
        inst = frame.f_locals['inst']
        method = getattr(inst, attr)
        return method.demo

    @view_config(name='pygments.css')
    def cssview(self):
        response =  Response(body=css, content_type='text/css')
        response.cache_expires = 360
        return response

    @view_config(renderer='templates/index.pt')
    def index(self):
        return {
            'demos':self.get_demos(),
            'showmenu':False,
            }

    def get_demos(self):
        context = self.request.context
        base_url = resource_url(context, self.request)
        def predicate(value):
            if getattr(value, 'demo', None) is not None:
                return True
        demos = inspect.getmembers(self, predicate)
        return sorted([(method.demo, base_url + name) for name, method in \
                       demos])

    @view_config(renderer='templates/form.pt', name='textinput')
    @demonstrate('Text Input Widget')
    def textinput(self):
        class Schema(colander.Schema):
            text = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(max=100),
                widget=deform.widget.TextInputWidget(size=60),
                description='Enter some text')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='textinput_with_css_class')
    @demonstrate('Text Input Widget with CSS Class')
    def textinput_with_css_class(self):
        css_widget = deform.widget.TextInputWidget(
            size=60, css_class='deformWidgetWithStyle')
        class Schema(colander.Schema):
            text = colander.SchemaNode(colander.String(),
                                       validator=colander.Length(max=100),
                                       widget = css_widget,
                                       description='Enter some text')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='autocomplete_input')
    @demonstrate('Autocomplete Input Widget')
    def autocomplete_input(self):
        choices = ['bar', 'baz', 'two', 'three']
        widget = deform.widget.AutocompleteInputWidget(
            size=60,
            values = choices,
            min_length=1)
        class Schema(colander.Schema):
            text = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(max=100),
                widget = widget,
                description='Enter some text (Hint: try "b" or "t")')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='autocomplete_remote_input')
    @demonstrate('Autocomplete Input Widget with Remote Data Source')
    def autocomplete_remote_input(self):
        widget = deform.widget.AutocompleteInputWidget(
            size=60,
            min_length=1,
            values = '/autocomplete_input_values')
        class Schema(colander.Schema):
            text = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(max=100),
                widget = widget,
                description='Enter some text (Hint: try "b" or "t")')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='json', name='autocomplete_input_values')
    def autocomplete_input_values(self):
        text = self.request.params.get('term', '')
        return [x for x in ['bar', 'baz', 'two', 'three'] 
                if x.startswith(text)]

    @view_config(renderer='templates/form.pt', name='textarea')
    @demonstrate('Text Area Widget')
    def textarea(self):
        class Schema(colander.Schema):
            text = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(max=100),
                widget=deform.widget.TextAreaWidget(rows=10, cols=60),
                description='Enter some text')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='richtext')
    @demonstrate('Rich Text Widget')
    def richtext(self):
        class Schema(colander.Schema):
            text = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.RichTextWidget(),
                description='Enter some text')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='password')
    @demonstrate('Password Widget')
    def password(self):
        class Schema(colander.Schema):
            password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5, max=100),
                widget=deform.widget.PasswordWidget(size=20),
                description='Enter a password')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='checkbox')
    @demonstrate('Checkbox Widget')
    def checkbox(self):
        class Schema(colander.Schema):
            want = colander.SchemaNode(
                colander.Boolean(),
                description='Check this box!',
                widget=deform.widget.CheckboxWidget(),
                title='I Want It!')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='radiochoice')
    @demonstrate('Radio Choice Widget')
    def radiochoice(self):
        choices = (('habanero', 'Habanero'), ('jalapeno', 'Jalapeno'),
                   ('chipotle', 'Chipotle'))
        class Schema(colander.Schema):
            pepper = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in choices]),
                widget=deform.widget.RadioChoiceWidget(values=choices),
                title='Choose your pepper',
                description='Select a Pepper')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='checkedinput')
    @demonstrate('Checked Input Widget')
    def checkedinput(self):
        widget = deform.widget.CheckedInputWidget(
            subject='Email',
            confirm_subject='Confirm Email',
            size=40)
        class Schema(colander.Schema):
            email = colander.SchemaNode(
                colander.String(),
                title='Email Address',
                description='Type your email address and confirm it',
                validator=colander.Email(),
                widget=widget)
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='checkedpassword')
    @demonstrate('Checked Password Widget')
    def checkedpassword(self):
        class Schema(colander.Schema):
            password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description='Type your password and confirm it')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='checkedinput_withmask')
    @demonstrate('Checked Input Widget (With Input Mask)')
    def checkedinput_withmask(self):
        widget = deform.widget.CheckedInputWidget(
            subject='SSN',
            confirm_subject='Confirm SSN',
            mask = '999-99-9999',
            mask_placeholder = '#',
            size=40)
        class Schema(colander.Schema):
            ssn = colander.SchemaNode(
                colander.String(),
                widget=widget,
                title = 'Social Security Number',
                description='Type your Social Security Number and confirm it',
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='mapping')
    @demonstrate('Mapping Widget')
    def mapping(self):
        class Mapping(colander.Schema):
            name = colander.SchemaNode(
                colander.String(),
                description='Content name')
            date = colander.SchemaNode(
                colander.Date(),
                widget=deform.widget.DatePartsWidget(),
                description='Content date')
        class Schema(colander.Schema):
            number = colander.SchemaNode(
                colander.Integer())
            mapping = Mapping()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='ajaxform')
    @demonstrate('AJAX form submission (inline success)')
    def ajaxform(self):
        class Mapping(colander.Schema):
            name = colander.SchemaNode(
                colander.String(),
                description='Content name')
            date = colander.SchemaNode(
                colander.Date(),
                widget=deform.widget.DatePartsWidget(),
                description='Content date')
        class Schema(colander.Schema):
            number = colander.SchemaNode(
                colander.Integer())
            mapping = Mapping()
        schema = Schema()
        def succeed():
            return Response('<div id="thanks">Thanks!</div>')
        form = deform.Form(schema, buttons=('submit',), use_ajax=True)
        return self.render_form(form, success=succeed)

    @view_config(renderer='templates/form.pt', name='ajaxform_redirect')
    @demonstrate('AJAX form submission (redirect on success)')
    def ajaxform_redirect(self):
        class Mapping(colander.Schema):
            name = colander.SchemaNode(
                colander.String(),
                description='Content name')
            date = colander.SchemaNode(
                colander.Date(),
                widget=deform.widget.DatePartsWidget(),
                description='Content date')
        class Schema(colander.Schema):
            number = colander.SchemaNode(
                colander.Integer())
            mapping = Mapping()
        schema = Schema()
        options = """
        {success:
          function (rText, sText, xhr, form) {
            var loc = xhr.getResponseHeader('X-Relocate');
            if (loc) {
              document.location = loc;
            };
           }
        }
        """
        def succeed():
            location = self.request.application_url + '/thanks.html'
            return Response(headers = [('X-Relocate', location)])
        form = deform.Form(schema, buttons=('submit',), use_ajax=True,
                           ajax_options=options)
        return self.render_form(form, success=succeed)

    @view_config(renderer='templates/form.pt', name='sequence_of_radiochoices')
    @demonstrate('Sequence of Radio Choice Widgets')
    def sequence_of_radiochoices(self):
        choices = (('habanero', 'Habanero'), ('jalapeno', 'Jalapeno'),
                   ('chipotle', 'Chipotle'))
        class Peppers(colander.SequenceSchema):
            pepper = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in choices]),
                widget=deform.widget.RadioChoiceWidget(values=choices),
                title='Pepper Chooser',
                description='Select a Pepper')
        class Schema(colander.Schema):
            peppers = Peppers()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='sequence_of_autocompletes')
    @demonstrate('Sequence of Autocomplete Widgets')
    def sequence_of_autocompletes(self):
        choices = ['bar', 'baz', 'two', 'three']
        widget = deform.widget.AutocompleteInputWidget(
            size=60,
            values = choices
            )
        class Sequence(colander.SequenceSchema):
            text = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(max=100),
                widget=widget,
                description='Enter some text (Hint: try "b" or "t")')
        class Schema(colander.Schema):
            texts = Sequence()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='sequence_of_dateinputs')
    @demonstrate('Sequence of Date Inputs')
    def sequence_of_dateinputs(self):
        import datetime
        from colander import Range
        class Sequence(colander.SequenceSchema):
            date = colander.SchemaNode(
                colander.Date(),
                validator=Range(
                    min=datetime.date(2010, 5, 5),
                    min_err=_('${val} is earlier than earliest date ${min}')
                    )
                )
        class Schema(colander.Schema):
            dates = Sequence()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='sequence_of_richtext')
    @demonstrate('Sequence of Rich Text Widgets')
    def sequence_of_richtext(self):
        class Sequence(colander.SequenceSchema):
            text = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.RichTextWidget(),
                description='Enter some text')
        class Schema(colander.Schema):
            texts = Sequence()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt',
              name='sequence_of_masked_textinputs')
    @demonstrate('Sequence of Masked Text Inputs')
    def sequence_of_masked_textinputs(self):
        class Sequence(colander.SequenceSchema):
            text = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextInputWidget(mask='999-99-9999'))
        class Schema(colander.Schema):
            texts = Sequence()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='sequence_of_fileuploads')
    @demonstrate('Sequence of File Upload Widgets')
    def sequence_of_fileuploads(self):
        class Sequence(colander.SequenceSchema):
            upload = colander.SchemaNode(
                deform.FileData(),
                widget=deform.widget.FileUploadWidget(tmpstore)
                )
        class Schema(colander.Schema):
            uploads = Sequence()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form, success=tmpstore.clear)


    @view_config(renderer='templates/form.pt',
              name='sequence_of_fileuploads_with_initial_item')
    @demonstrate('Sequence of File Upload Widgets (With Initial Item)')
    def sequence_of_fileuploads_with_initial_item(self):
        class Sequence(colander.SequenceSchema):
            upload = colander.SchemaNode(
                deform.FileData(),
                widget=deform.widget.FileUploadWidget(tmpstore)
                )
        class Schema(colander.Schema):
            uploads = Sequence()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        form['uploads'].widget = deform.widget.SequenceWidget(min_len=1)
        return self.render_form(form, success=tmpstore.clear)

    @view_config(renderer='templates/form.pt', name='sequence_of_mappings')
    @demonstrate('Sequence of Mapping Widgets')
    def sequence_of_mappings(self):
        class Person(colander.Schema):
            name = colander.SchemaNode(colander.String())
            age = colander.SchemaNode(colander.Integer(),
                                      validator=colander.Range(0,200))
        class People(colander.SequenceSchema):
            person = Person()
        class Schema(colander.Schema):
            people = People()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt',
              name='sequence_of_mappings_with_initial_item')
    @demonstrate('Sequence of Mapping Widgets (With Initial Item)')
    def sequence_of_mappings_with_initial_item(self):
        class Person(colander.Schema):
            name = colander.SchemaNode(colander.String())
            age = colander.SchemaNode(colander.Integer(),
                                      validator=colander.Range(0,200))
        class People(colander.SequenceSchema):
            person = Person()
        class Schema(colander.Schema):
            people = People()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        form['people'].widget = deform.widget.SequenceWidget(min_len=1)
        return self.render_form(form)

    @view_config(renderer='templates/form.pt',
              name='readonly_sequence_of_mappings')
    @demonstrate('Read-Only Sequence of Mappings')
    def readonly_sequence_of_mappings(self):
        class Person(colander.Schema):
            name = colander.SchemaNode(colander.String())
            age = colander.SchemaNode(colander.Integer(),
                                      validator=colander.Range(0,200))
        class People(colander.SequenceSchema):
            person = Person()
        class Schema(colander.Schema):
            people = People()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(
            form,
            appstruct={'people':
                       [{'name':'name1', 'age':23},
                        {'name':'name2', 'age':25},]
                       },
            readonly=True)

    @view_config(renderer='templates/form.pt', name='sequence_of_sequences')
    @demonstrate('Sequence of Sequence Widgets')
    def sequence_of_sequences(self):
        class NameAndTitle(colander.Schema):
            name = colander.SchemaNode(colander.String())
            title = colander.SchemaNode(colander.String())
        class NamesAndTitles(colander.SequenceSchema):
            name_and_title = NameAndTitle(title='Name and Title')
        class NamesAndTitlesSequences(colander.SequenceSchema):
            names_and_titles = NamesAndTitles(title='Names and Titles')
        class Schema(colander.Schema):
            names_and_titles_sequence = NamesAndTitlesSequences(
                title='Sequence of Sequences of Names and Titles')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        outer = form['names_and_titles_sequence']
        outer.widget = deform.widget.SequenceWidget(min_len=1)
        outer['names_and_titles'].widget = deform.widget.SequenceWidget(
            min_len=1)
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='sequence_of_constrained_len')
    @demonstrate('Sequence of Constrained Min and Max Lengths')
    def sequence_of_constrained_len(self):
        class Names(colander.SequenceSchema):
            name = colander.SchemaNode(colander.String())
        class Schema(colander.Schema):
            names = Names(
                validator = colander.Length(2, 4),
                title = 'At Least 2 At Most 4 Names',
                widget=deform.widget.SequenceWidget(
                    min_len=2,
                    max_len=4)
            )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)
        
    @view_config(renderer='templates/form.pt', name='file')
    @demonstrate('File Upload Widget')
    def file(self):
        class Schema(colander.Schema):
            upload = colander.SchemaNode(
                deform.FileData(),
                widget=deform.widget.FileUploadWidget(tmpstore)
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form, success=tmpstore.clear)

    @view_config(renderer='templates/form.pt', name='dateparts')
    @demonstrate('Date Parts Widget')
    def dateparts(self):
        import datetime
        from colander import Range
        class Schema(colander.Schema):
            date = colander.SchemaNode(
                colander.Date(),
                widget = deform.widget.DatePartsWidget(),
                validator=Range(
                    min=datetime.date(2010, 1, 1),
                    min_err=_('${val} is earlier than earliest date ${min}')
                    )
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='dateinput')
    @demonstrate('Date Input Widget')
    def dateinput(self):
        import datetime
        from colander import Range
        class Schema(colander.Schema):
            date = colander.SchemaNode(
                colander.Date(),
                validator=Range(
                    min=datetime.date(2010, 5, 5),
                    min_err=_('${val} is earlier than earliest date ${min}')
                    )
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        when = datetime.date(2010, 5, 5)
        return self.render_form(form, appstruct={'date':when})

    @view_config(renderer='templates/form.pt', name='edit')
    @demonstrate('Edit Form')
    def edit(self):
        class Mapping(colander.Schema):
            name = colander.SchemaNode(
                colander.String(),
                description='Content name')
            date = colander.SchemaNode(
                colander.Date(),
                widget = deform.widget.DatePartsWidget(),
                description='Content date')
        class Schema(colander.Schema):
            number = colander.SchemaNode(
                colander.Integer())
            mapping = Mapping()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        import datetime
        # We don't need to suppy all the values required by the schema
        # for an initial rendering, only the ones the app actually has
        # values for.  Notice below that we don't pass the ``name``
        # value specified by the ``Mapping`` schema.
        appstruct = {
            'number':42,
            'mapping': {
                'date':datetime.date(2010, 4, 9),
                }
            }
        return self.render_form(form, appstruct=appstruct)

    @view_config(renderer='templates/form.pt', name='interfield')
    @demonstrate('Inter-Field Validation')
    def interfield(self):
        class Schema(colander.Schema):
            name = colander.SchemaNode(
                colander.String(),
                description='Content name')
            title = colander.SchemaNode(
                colander.String(),
                description='Content title (must start with content name)')
        def validator(form, value):
            if not value['title'].startswith(value['name']):
                exc = colander.Invalid(form, 'Title must start with name')
                exc['title'] = 'Must start with name %s' % value['name']
                raise exc
        schema = Schema(validator=validator)
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='fielddefaults')
    @demonstrate('Field Defaults')
    def fielddefaults(self):
        class Schema(colander.Schema):
            artist = colander.SchemaNode(
                colander.String(),
                default = 'Grandaddy',
                description='Song name')
            album = colander.SchemaNode(
                colander.String(),
                default='Just Like the Fambly Cat')
            song = colander.SchemaNode(
                colander.String(),
                description='Song name')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='nonrequiredfields')
    @demonstrate('Non-Required Fields')
    def nonrequiredfields(self):
        class Schema(colander.Schema):
            required = colander.SchemaNode(
                colander.String(),
                description='Required Field'
                )
            notrequired = colander.SchemaNode(
                colander.String(),
                missing=u'',
                description='Unrequired Field')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='nonrequired_number_fields')
    @demonstrate('Non-Required Number Fields')
    def nonrequired_number_fields(self):
        class Schema(colander.Schema):
            required = colander.SchemaNode(
                colander.Int(),
                description='Required Field'
                )
            notrequired = colander.SchemaNode(
                colander.Float(),
                missing=0,
                description='Unrequired Field')
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='unicodeeverywhere')
    @demonstrate('Unicode Everywhere')
    def unicodeeverywhere(self):
        class Schema(colander.Schema):
            field = colander.SchemaNode(
                colander.String(),
                title = u'По оживлённым берегам',
                description=(u"子曰：「學而時習之，不亦說乎？有朋自遠方來，不亦樂乎？ "
                             u"人不知而不慍，不亦君子乎？」"),
                default=u'☃',
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='select')
    @demonstrate('Select Widget')
    def select(self):
        choices = (
            ('', '- Select -'),
            ('habanero', 'Habanero'),
            ('jalapeno', 'Jalapeno'),
            ('chipotle', 'Chipotle')
            )
        class Schema(colander.Schema):
            pepper = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.SelectWidget(values=choices)
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='checkboxchoice')
    @demonstrate('Checkbox Choice Widget')
    def checkboxchoice(self):
        choices = (('habanero', 'Habanero'), ('jalapeno', 'Jalapeno'),
                   ('chipotle', 'Chipotle'))
        class Schema(colander.Schema):
            pepper = colander.SchemaNode(
                deform.Set(),
                widget=deform.widget.CheckboxChoiceWidget(values=choices),
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='checkboxchoice2')
    @demonstrate('Checkbox Choice Widget 2')
    def checkboxchoice2(self):
        choices = (('habanero', 'Habanero'), ('jalapeno', 'Jalapeno'),
                   ('chipotle', 'Chipotle'))

        @colander.deferred
        def deferred_checkbox_widget(node, kw):
            return deform.widget.CheckboxChoiceWidget(values=choices)

        class Schema(colander.Schema):
            pepper = colander.SchemaNode(
                deform.Set(),
                widget=deferred_checkbox_widget,
                )
            required = colander.SchemaNode(
                colander.String()
                )

        schema = Schema()
        schema = schema.bind()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/translated_form.pt', name='i18n')
    @demonstrate('Internationalization')
    def i18n(self):
        minmax = {'min':1, 'max':10}
        locale_name = get_locale_name(self.request)
        class Schema(colander.Schema):
            
            number = colander.SchemaNode(
                colander.Integer(),
                title=_('A number between ${min} and ${max}',
                        mapping=minmax),
                description=_('A number between ${min} and ${max}',
                              mapping=minmax),
                validator = colander.Range(1, 10),
                )
            _LOCALE_ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default=locale_name)

        schema = Schema()
        form = deform.Form(
            schema,
            buttons=[deform.Button('submit', _('Submit'))],
            )

        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='hidden_field')
    @demonstrate('Hidden Field Widget')
    def hidden_field(self):
        class Schema(colander.Schema):
            sneaky = colander.SchemaNode(
                colander.Boolean(),
                widget = deform.widget.HiddenWidget(),
                default=True,
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='hiddenmissing')
    @demonstrate('Hidden, Missing Widget Representing an Integer')
    def hiddenmissing(self):
        class Schema(colander.Schema):
            title = colander.SchemaNode(
                colander.String())
            number = colander.SchemaNode(
                colander.Integer(),
                widget = deform.widget.HiddenWidget(),
                missing=colander.null,
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='text_input_masks')
    @demonstrate('Text Input Masks')
    def text_input_masks(self):
        class Schema(colander.Schema):
            ssn = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.TextInputWidget(mask='999-99-9999'),
                )
            date = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.TextInputWidget(mask='99/99/9999'),
                )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='textareacsv')
    @demonstrate('Text Area CSV Widget')
    def textareacsv(self):
        class Row(colander.TupleSchema):
            first = colander.SchemaNode(colander.Integer())
            second = colander.SchemaNode(colander.String())
            third = colander.SchemaNode(colander.Decimal())
        class Rows(colander.SequenceSchema):
            row = Row()
        class Schema(colander.Schema):
            csv = Rows()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        form['csv'].widget = deform.widget.TextAreaCSVWidget(rows=10, cols=60)
        appstruct = {'csv':[ (1, 'hello', 4.5), (2, 'goodbye', 5.5) ]}
        return self.render_form(form, appstruct=appstruct)

    @view_config(renderer='templates/form.pt', name='textinputcsv')
    @demonstrate('Text Input CSV Widget')
    def textinputcsv(self):
        class Row(colander.TupleSchema):
            first = colander.SchemaNode(colander.Integer())
            second = colander.SchemaNode(colander.String())
            third = colander.SchemaNode(colander.Decimal())
        class Schema(colander.Schema):
            csv = Row()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        # we don't need to assign a widget; the text input csv widget is the
        # default widget for tuples
        appstruct = {'csv':(1, 'hello', 4.5)}
        return self.render_form(form, appstruct=appstruct)

    @view_config(renderer='templates/form.pt', name='require_one_or_another')
    @demonstrate('Require One Field or Another')
    def require_one_or_another(self):
        class Schema(colander.Schema):
            one = colander.SchemaNode(
                colander.String(),
                missing=u'',
                title='One (required if Two is not supplied)')
            two = colander.SchemaNode(
                colander.String(),
                missing=u'',
                title='Two (required if One is not supplied)')
        def validator(form, value):
            if not value['one'] and not value['two']:
                exc = colander.Invalid(
                    form, 'A value for either "one" or "two" is required')
                exc['one'] = 'Required if two is not supplied'
                exc['two'] = 'Required if one is not supplied'
                raise exc
        schema = Schema(validator=validator)
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='multiple_error_messages_mapping')
    @demonstrate('Multiple Error Messages For a Single Widget (Mapping)')
    def multiple_error_messages_mapping(self):
        def v1(node, value):
            msg = _('Error ${num}', mapping=dict(num=1))
            raise colander.Invalid(node, msg)
        def v2(node, value):
            msg = _('Error ${num}', mapping=dict(num=2))
            raise colander.Invalid(node, msg)
        def v3(node, value):
            msg = _('Error ${num}', mapping=dict(num=3))
            raise colander.Invalid(node, msg)
        class Schema(colander.Schema):
            field = colander.SchemaNode(
                colander.String(),
                title="Fill in a value and submit to see multiple errors",
                validator = colander.All(v1, v2, v3))
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name='multiple_error_messages_seq')
    @demonstrate('Multiple Error Messages For a Single Widget (Sequence)')
    def multiple_error_messages_seq(self):
        def v1(node, value):
            msg = _('Error ${num}', mapping=dict(num=1))
            raise colander.Invalid(node, msg)
        def v2(node, value):
            msg = _('Error ${num}', mapping=dict(num=2))
            raise colander.Invalid(node, msg)
        def v3(node, value):
            msg = _('Error ${num}', mapping=dict(num=3))
            raise colander.Invalid(node, msg)
        class Sequence(colander.SequenceSchema):
            field = colander.SchemaNode(
                colander.String(),
                title="Fill in a value and submit to see multiple errors",
                validator = colander.All(v1, v2, v3))
        class Schema(colander.Schema):
            fields = Sequence()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

    @view_config(renderer='templates/form.pt', name="multiple_forms")
    @demonstrate('Multiple Forms on the Same Page')
    def multiple_forms(self):
        import itertools

        # We need to make sure the form field identifiers for the two
        # forms do not overlap so accessibility features continue work
        # such as focusing the field related to a legend when the
        # legend is clicked on.

        # We do so by creating an ``itertools.count`` object and
        # passing that object as the ``counter`` keyword argument to
        # the constructor of both forms.  As a result, the second
        # form's element identifiers will not overlap the first
        # form's.

        counter = itertools.count() 
        
        class Schema1(colander.Schema):
            name1 = colander.SchemaNode(colander.String())
        schema1 = Schema1()
        form1 = deform.Form(schema1, buttons=('submit',), formid='form1',
                            counter=counter)

        class Schema2(colander.Schema):
            name2 = colander.SchemaNode(colander.String())
        schema2 = Schema2()
        form2 = deform.Form(schema2, buttons=('submit',), formid='form2',
                            counter=counter)

        html = []
        captured = None

        if 'submit' in self.request.POST:
            posted_formid = self.request.POST['__formid__']
            for (formid, form) in [('form1', form1), ('form2', form2)]:
                if formid == posted_formid:
                    try:
                        controls = self.request.POST.items()
                        captured = form.validate(controls)
                        html.append(form.render(captured))
                    except deform.ValidationFailure, e:
                        # the submitted values could not be validated
                        html.append(e.render())
                else:
                    html.append(form.render())
        else:
            for form in form1, form2:
                html.append(form.render())

        html = ''.join(html)

        code, start, end = self.get_code(1)

        # values passed to template for rendering
        return {
            'form':html,
            'captured':repr(captured),
            'code': code,
            'start':start,
            'demos':self.get_demos(),
            'showmenu':True,
            'end':end,
            'title':'Multiple Forms on the Same Page',
            }
        
    @view_config(renderer='templates/form.pt', name='widget_adapter')
    @demonstrate('Widget Adapter')
    def widget_adapter(self):
        # Formish allows you to pair a widget against a type that
        # doesn't "natively" lend itself to being representible by the
        # widget; for example, it allows you to use a text area widget
        # against a sequence type.  To provide this feature, Formish
        # uses an adapter to convert the sequence data to text during
        # serialization and from text back to a sequence during
        # deserialization.
        #
        # Deform doesn't have such a feature out of the box.  This is
        # on purpose: the feature is really too complicated and
        # magical for civilians.  However, if you really want or need
        # it, you can add yourself as necessary using an adapter
        # pattern.
        #
        # In the demo method below, we adapt a "normal" text area
        # widget for use against a sequence.  The resulting browser UI
        # is the same as if we had used a TextAreaCSVWidget against
        # the sequence as in the "textareacsv" test method.
        #
        # N.B.: we haven't automated the lookup of the widget adapter
        # based on the type of the field and the type of the widget.
        # Instead, we just construct an adapter manually.  Adding an
        # abstraction to the lookup based on the widget and schema
        # types being adapted is easy enough, but trying to follow the
        # codepath of the abstraction becomes brainbending.
        # Therefore, we don't bother to show it.
        class Row(colander.TupleSchema):
            first = colander.SchemaNode(colander.Integer())
            second = colander.SchemaNode(colander.String())
            third = colander.SchemaNode(colander.Decimal())
        class Rows(colander.SequenceSchema):
            row = Row()
        class Schema(colander.Schema):
            csv = Rows()
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        inner_widget = deform.widget.TextAreaWidget(rows=10, cols=60)
        widget = SequenceToTextWidgetAdapter(inner_widget)
        form['csv'].widget = widget
        appstruct = {'csv':[ (1, 'hello', 4.5), (2, 'goodbye', 5.5) ]}
        return self.render_form(form, appstruct=appstruct)

    @view_config(renderer='templates/form.pt', name='deferred_schema_bindings')
    @demonstrate('Deferred Schema Bindings')
    def deferred_schema_bindings(self):
        import datetime
        import colander
        @colander.deferred
        def deferred_date_validator(node, kw):
            max_date = kw.get('max_date')
            if max_date is None:
                max_date = datetime.date.today()
            return colander.Range(min=datetime.date.min, max=max_date)

        @colander.deferred
        def deferred_date_description(node, kw):
            max_date = kw.get('max_date')
            if max_date is None:
                max_date = datetime.date.today()
            return 'Blog post date (no earlier than %s)' % max_date.ctime()

        @colander.deferred
        def deferred_date_missing(node, kw):
            default_date = kw.get('default_date')
            if default_date is None:
                default_date = datetime.date.today()
            return default_date

        @colander.deferred
        def deferred_body_validator(node, kw):
            max_bodylen = kw.get('max_bodylen')
            if max_bodylen is None:
                max_bodylen = 1 << 18
            return colander.Length(max=max_bodylen)

        @colander.deferred
        def deferred_body_description(node, kw):
            max_bodylen = kw.get('max_bodylen')
            if max_bodylen is None:
                max_bodylen = 1 << 18
            return 'Blog post body (no longer than %s bytes)' % max_bodylen

        @colander.deferred
        def deferred_body_widget(node, kw):
            body_type = kw.get('body_type')
            if body_type == 'richtext':
                widget = deform.widget.RichTextWidget()
            else:
                widget = deform.widget.TextAreaWidget()
            return widget

        @colander.deferred
        def deferred_category_validator(node, kw):
            categories = kw.get('categories', [])
            return colander.OneOf([ x[0] for x in categories ])

        @colander.deferred
        def deferred_category_widget(node, kw):
            categories = kw.get('categories', [])
            return deform.widget.RadioChoiceWidget(values=categories)

        class BlogPostSchema(colander.Schema):
            title = colander.SchemaNode(
                colander.String(),
                title = 'Title',
                description = 'Blog post title',
                validator = colander.Length(min=5, max=100),
                widget = deform.widget.TextInputWidget(),
                )
            date = colander.SchemaNode(
                colander.Date(),
                title = 'Date',
                missing = deferred_date_missing,
                description = deferred_date_description,
                validator = deferred_date_validator,
                widget = deform.widget.DateInputWidget(),
                )
            body = colander.SchemaNode(
                colander.String(),
                title = 'Body',
                description = deferred_body_description,
                validator = deferred_body_validator,
                widget = deferred_body_widget,
                )
            category = colander.SchemaNode(
                colander.String(),
                title = 'Category',
                description = 'Blog post category',
                validator = deferred_category_validator,
                widget = deferred_category_widget,
                )
        
        schema = BlogPostSchema().bind(
            max_date = datetime.date.max,
            max_bodylen = 5000,
            body_type = 'richtext',
            default_date = datetime.date.today(),
            categories = [('one', 'One'), ('two', 'Two')]
            )
        
        form = deform.Form(schema, buttons=('submit',))
        return self.render_form(form)

class MemoryTmpStore(dict):
    """ Instances of this class implement the
    :class:`deform.interfaces.FileUploadTempStore` interface"""
    def preview_url(self, uid):
        return None

tmpstore = MemoryTmpStore()

class SequenceToTextWidgetAdapter(object):
    def __init__(self, widget):
        self.widget = widget

    def __getattr__(self, name):
        return getattr(self.widget, name)

    def serialize(self, field, cstruct, readonly=False):
        if cstruct is colander.null:
            cstruct = []
        textrows = getattr(field, 'unparseable', None)
        if textrows is None:
            outfile = StringIO.StringIO()
            writer = csv.writer(outfile)
            writer.writerows(cstruct)
            textrows = outfile.getvalue()
        return self.widget.serialize(field, cstruct=textrows,
                                     readonly=readonly)

    def deserialize(self, field, pstruct):
        text = self.widget.deserialize(field, pstruct)
        if text is colander.null:
            return text
        if not text.strip():
            return colander.null
        try:
            infile = StringIO.StringIO(text)
            reader = csv.reader(infile)
            rows = list(reader)
        except Exception, e:
            field.unparseable = pstruct
            raise colander.Invalid(field.schema, str(e))
        return rows

    def handle_error(self, field, error):
        msgs = []
        if error.msg:
            field.error = error
        else:
            for e in error.children:
                msgs.append('line %s: %s' % (e.pos+1, e))
            field.error = colander.Invalid(field.schema, '\n'.join(msgs))
        

def run(global_config, **settings):
    settings['debug_templates'] = 'true'
    config = Configurator(settings=settings)
    config.begin()
    config.add_static_view('static', 'deform:static')
    config.add_static_view('static_demo', 'deformdemo:static')
    config.add_translation_dirs(
        'colander:locale',
        'deform:locale',
        'deformdemo:locale'
        )
    config.scan()
    config.end()
    return config.make_wsgi_app()
