import csv
import random
import string
import StringIO
import urllib

from colander import Invalid
from deform.i18n import _

class Widget(object):
    """
    A widget is the building block for rendering logic.  The
    :class:`deform.widget.Widget` class is never instantiated
    directly: it is the abstract class from which all other widget
    types within :mod:`deform.widget` derive.  It should likely also
    be subclassed by application-developer-defined widgets.

    A widget instance is attached to a field during normal operation.
    A widget is not meant to carry any state.  Instead, widget
    implementations should use the ``field`` object passed to them
    during :meth:`deform.widget.Widget.serialize` and
    :meth:`deform.widget.Widget.deserialize` as a scratchpad for state
    information.

    All widgets have the following attributes:

    hidden
        An attribute indicating the hidden state of this widget.  The
        default is ``False``.  If this attribute is not ``False``, the
        field associated with this widget will not be rendered in the
        form (although, if the widget is a structural widget, its
        children will be; ``hidden`` is not a recursive flag).  No
        label, no error message, nor any furniture such as a close
        button when the widget is one of a sequence will exist for the
        field in the rendered form.

    category
        A string value indicating the *category* of this widget.  This
        attribute exists to inform structural widget rendering
        behavior.  For example, when a text widget or another simple
        'leaf-level' widget is rendered as a child of a mapping widget
        using the default template mapping template, the field title
        associated with the child widget will be rendered above the
        field as a label by default.  This is because simple child
        widgets are in the ``default`` category and no special action
        is taken when a structural widget renders child widgets that
        are in the ``default`` category.  However, if the default
        mapping widget encounters a child widget with the category of
        ``structural`` during rendering (the default mapping and
        sequence widgets are in this category), it omits the title.
        Default: ``default``

    error_class
        The name of the CSS class attached to various tags in the form
        renderering indicating an error condition for the field
        associated with this widget.  Default: ``error``.

    These attributes are also accepted as keyword arguments to all
    widget constructors; if they are passed, they will override the
    defaults.

    Particular widget types also accept other keyword arguments that
    get attached to the widget as attributes.  These are documented as
    'Attributes/Arguments' within the documentation of each concrete
    widget implementation subclass.
    """

    hidden = False
    category = 'default'
    error_class = 'error'

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def serialize(self, field, cstruct=None, readonly=False):
        """
        The ``serialize`` method of a widget must serialize a
        :term:`cstruct` value to an HTML rendering.  A :term:`cstruct`
        value is the value which results from a :term:`Colander`
        schema serialization for the schema node associated with this
        widget.  ``serialize`` should return the HTML rendering: the
        result of this method should always be a string containing
        HTML.  The ``field`` argument is the :term:`field` object to
        which this widget is attached.  If the ``readonly`` argument
        is ``True``, it indicates that the result of this
        serialization should be a read-only rendering (no form
        controls) of the ``cstruct`` data to HTML.
        """
        raise NotImplementedError

    def deserialize(self, field, pstruct=None):
        """
        The ``deserialize`` method of a widget must deserialize a
        :term:`pstruct` value to a :term:`cstruct` value and return the
        :term:`cstruct` value.  The ``pstruct`` argument is a value resulting
        from the ``parse`` method of the :term:`Peppercorn` package. The
        ``field`` argument is the field object to which this widget is
        attached.
        """
        raise NotImplementedError

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        # XXX exponential time
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)


class TextInputWidget(Widget):
    """
    Renders an ``<input type="text"/>`` widget.

    **Attributes/Arguments**

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).

    template
        The template name used to render the widget.  Default:
        ``textinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """
    template = 'textinput'
    readonly_template = 'readonly/textinput'
    size = None
    strip = True

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = ''
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ''
        if self.strip:
            pstruct = pstruct.strip()
        return pstruct

class HiddenWidget(Widget):
    """
    Renders an ``<input type="hidden"/>`` widget.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``hidden``.
    """
    template = 'hidden'
    hidden = True

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = ''
        return field.renderer(self.template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ''
        return pstruct

class TextAreaWidget(TextInputWidget):
    """
    Renders a ``<textarea>`` widget.

    **Attributes/Arguments**

    cols
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``cols`` is not included in the
        widget output (uses browser default cols).

    rows
        The size, in rows, of the text input field.  Defaults to
        ``None``, meaning that the ``rows`` is not included in the
        widget output (uses browser default cols).

    template
        The template name used to render the widget.  Default:
        ``textarea``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textarea``.


    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """
    template = 'textarea'
    readonly_template = 'readonly/textarea'
    cols = None
    rows = None
    strip = True


class PasswordWidget(TextInputWidget):
    """
    Renders a single <input type="password"/> input field.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``password``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/password``.

    size
        The ``size`` attribute of the password input field (default:
        ``None``).

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """
    template = 'password'
    readonly_template = 'readonly/password'

class CheckboxWidget(Widget):
    """
    Renders an ``<input type="checkbox"/>`` widget.

    **Attributes/Arguments**

    true_val
        The value which should be returned during deserialization if
        the box is checked.  Default: ``true``.

    false_val
        The value which should be returned during deserialization if
        the box was left unchecked.  Default: ``false``.

    template
        The template name used to render the widget.  Default:
        ``checkbox``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/checkbox``.

    """
    true_val = 'true'
    false_val = 'false'

    template = 'checkbox'
    readonly_template = 'readonly/checkbox'

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = self.false_val
        return (pstruct == self.true_val) and self.true_val or self.false_val

class RadioChoiceWidget(Widget):
    """
    Renders a sequence of ``<input type="radio"/>`` buttons based on a
    predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples indicating allowable, displayed
        values, e.g. ``( ('true', 'True'), ('false', 'False') )``.
        The first element in the tuple is the value that should be
        returned when the form is posted.  The second is the display
        value.

    template
        The template name used to render the widget.  Default:
        ``radio_choice``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/radio_choice``.
    """
    template = 'radio_choice'
    readonly_template = 'readonly/radio_choice'
    values = ()

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ''
        return pstruct

class SelectWidget(Widget):
    """
    Renders ``<select>`` field based on a predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples indicating allowable, displayed
        values, e.g. ``( ('true', 'True'), ('false', 'False') )``.
        The first element in the tuple is the value that should be
        returned when the form is posted.  The second is the display
        value.

    template
        The template name used to render the widget.  Default:
        ``select``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/select``.
    """
    template = 'select'
    readonly_template = 'readonly/select'
    values = ()

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ''
        return pstruct

class CheckboxChoiceWidget(Widget):
    """
    Renders a sequence of ``<input type="check"/>`` buttons based on a
    predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples indicating allowable, displayed
        values, e.g. ``( ('true', 'True'), ('false', 'False') )``.
        The first element in the tuple is the value that should be
        returned when the form is posted.  The second is the display
        value.

    template
        The template name used to render the widget.  Default:
        ``checkbox_choice``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/checkbox_choice``.
    """
    template = 'checkbox_choice'
    readonly_template = 'readonly/checkbox_choice'
    values = ()

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = ()
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ()
        if isinstance(pstruct, basestring):
            return (pstruct,)
        return tuple(pstruct)

class CheckedInputWidget(Widget):
    """
    Renders two text input fields: 'value' and 'confirm'.
    Validates that the 'value' value matches the 'confirm' value.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``checked_input``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/checked_input``.

    size
        The ``size`` attribute of the input fields (default:
        ``None``, default browser size).

    mismatch_message
        The message to be displayed when the value in the primary
        field doesn't match the value in the confirm field.
    """
    template = 'checked_input'
    readonly_template = 'readonly/checked_input'
    size = None
    mismatch_message = _('Fields did not match')
    subject = _('Value')
    confirm_subject = _('Confirm Value')

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = ''
        confirm = getattr(field, 'confirm', '')
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct,
                              confirm=confirm, subject=self.subject,
                              confirm_subject=self.confirm_subject,
                              )

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = {}
        value = pstruct.get('value') or ''
        confirm = pstruct.get('confirm') or ''
        field.confirm = confirm
        if value != confirm:
            raise Invalid(field.schema, self.mismatch_message, value)
        return value

class CheckedPasswordWidget(CheckedInputWidget):
    """
    Renders two password input fields: 'password' and 'confirm'.
    Validates that the 'password' value matches the 'confirm' value.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``checked_password``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/checked_password``.

    size
        The ``size`` attribute of the password input field (default:
        ``None``).
    """
    template = 'checked_password'
    readonly_template = 'readonly/checked_password'
    mismatch_message = _('Password did not match confirm')
    size = None

class MappingWidget(Widget):
    """
    Renders a mapping into a set of fields.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``mapping``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/mapping``.

    item_template
        The template name used to render each item in the mapping.
        Default: ``mapping_item``.

    readonly_item_template
        The template name used to render each item in the form.
        Default: ``readonly/mapping_item``.

    """
    template = 'mapping'
    readonly_template = 'readonly/mapping'
    item_template = 'mapping_item'
    readonly_item_template = 'readonly/mapping_item'
    error_class = None
    category = 'structural'

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = {}
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        error = None
        result = {}

        if pstruct is None:
            pstruct = {}

        for num, subfield in enumerate(field.children):
            name = subfield.name
            subval = pstruct.get(name)
            try:
                result[name] = subfield.widget.deserialize(subfield, subval)
            except Invalid, e:
                result[name] = e.value
                if error is None:
                    error = Invalid(field.schema, value=result)
                error.add(e, num)

        if error is not None:
            raise error

        return result

class FormWidget(MappingWidget):
    """
    The top-level widget; represents an entire form.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``form``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/form``.

    item_template
        The template name used to render each item in the form.
        Default: ``mapping_item``.

    readonly_item_template
        The template name used to render each item in the form.
        Default: ``readonly/mapping_item``.

    """
    template = 'form'
    readonly_template = 'readonly/form'

class SequenceWidget(Widget):
    """
    Renders a sequence (0 .. N widgets, each the same as the other)
    into a set of fields.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``sequence``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/sequence``.

    item_template
        The template name used to render each value in the sequence.
        Default: ``sequence_item``.

    add_subitem_text_template
        The string used as the add link text for the widget.
        Interpolation markers in the template will be replaced in this
        string during serialization with a value as follows:

        ``${subitem_title}``
          The title of the subitem field

        ``${subitem_description}``
          The description of the subitem field

        ``${subitem_name}``
          The name of the subitem field

        Default: ``Add ${subitem_title}``.

    render_initial_item
        Boolean attribute indicating whether, on the first rendering
        of a form including a sequence widget, a child widget
        rendering should be performed.  Default: ``False``.

    closebutton_url
        The URL to the image representing the sequence item close
        button.  Default: ``/static/images/close.png``
    """
    template = 'sequence'
    readonly_template = 'readonly/sequence'
    item_template = 'sequence_item'
    readonly_item_template = 'readonly/sequence_item'
    error_class = None
    add_subitem_text_template = _('Add ${subitem_title}')
    render_initial_item = False
    category = 'structural'
    closebutton_url = '/static/images/close.png'

    def prototype(self, field):
        # we clone the item field to bump the oid (for easier
        # automated testing; finding last node)
        item_field = field.children[0].clone()
        proto = field.renderer(self.item_template, field=item_field,
                               cstruct=None, parent=field)
        if isinstance(proto, unicode):
            proto = proto.encode('utf-8')
        proto = urllib.quote(proto)
        return proto

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            if self.render_initial_item:
                cstruct = [None]
            else:
                cstruct = []

        item_field = field.children[0]

        if getattr(field, 'sequence_fields', None):
            # this serialization is assumed to be performed as a
            # result of a validation failure (``deserialize`` was
            # previously run)
            assert(len(cstruct) == len(field.sequence_fields))
            subfields = zip(cstruct, field.sequence_fields)
        else:
            # this serialization is being performed as a result of a
            # first-time rendering
            subfields = [ (val, item_field.clone()) for val in cstruct ]

        template = readonly and self.readonly_template or self.template
        add_template_mapping = dict(
            subitem_title=item_field.title,
            subitem_description=item_field.description,
            subitem_name=item_field.name)
        add_subitem_text = _(self.add_subitem_text_template,
                             mapping=add_template_mapping)
        return field.renderer(template, field=field, cstruct=cstruct,
                              subfields=subfields, item_field=item_field,
                              add_subitem_text=add_subitem_text)

    def deserialize(self, field, pstruct):
        result = []
        error = None

        if pstruct is None:
            pstruct = []

        field.sequence_fields = []
        item_field = field.children[0]

        for num, substruct in enumerate(pstruct):
            subfield = item_field.clone()
            try:
                subval = subfield.widget.deserialize(subfield, substruct)
            except Invalid, e:
                subval = e.value
                if error is None:
                    error = Invalid(field.schema, value=result)
                error.add(e, num)

            result.append(subval)
            field.sequence_fields.append(subfield)

        if error is not None:
            raise error

        return result

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        # XXX exponential time
        sequence_fields = getattr(field, 'sequence_fields', [])
        for e in error.children:
            for num, subfield in enumerate(sequence_fields):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)

class FileUploadWidget(Widget):
    """
    Represent a file upload.  Meant to work with a
    :class:`deform.FileData` schema node.

    This widget accepts a single required positional argument in its
    constructor: ``tmpstore``.  This argument should be passed an
    instance of an object that implements the
    :class:`deform.interfaces.FileUploadTempStore` interface.  Such an
    instance will hold on to file upload data during the validation
    process, so the user doesn't need to reupload files if other parts
    of the form rendering fail validation.  See also
    :class:`deform.interfaces.FileUploadTempStore`.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``file_upload``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/file_upload``.

    size
        The ``size`` attribute of the input field (default ``None``).
    """
    template = 'file_upload'
    readonly_template = 'readonly/file_upload'
    size = None

    def __init__(self, tmpstore, **kw):
        Widget.__init__(self, **kw)
        self.tmpstore = tmpstore

    def random_id(self):
        return ''.join(
            [random.choice(string.uppercase+string.digits) for i in range(10)])

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = {}
        if cstruct:
            uid = cstruct['uid']
            if not uid in self.tmpstore:
                self.tmpstore[uid] = cstruct

        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        upload = pstruct.get('upload')
        uid = pstruct.get('uid')

        if hasattr(upload, 'file'):
            # the upload control had a file selected
            data = {}
            data['fp'] = upload.file
            data['filename'] = upload.filename
            data['mimetype'] = upload.type
            data['size']  = upload.length
            if uid is None:
                # no previous file exists
                while 1:
                    uid = self.random_id()
                    if self.tmpstore.get(uid) is None:
                        data['uid'] = uid
                        data['preview_url'] = self.tmpstore.preview_url(uid)
                        self.tmpstore[uid] = data
                        break
            else:
                # a previous file exists
                data['uid'] = uid
                data['preview_url'] = self.tmpstore.preview_url(uid)
                self.tmpstore[uid] = data
        else:
            # the upload control had no file selected
            if uid is None:
                # no previous file exists
                return None
            else:
                # a previous file should exist
                data = self.tmpstore.get(uid)
                # but if it doesn't, don't blow up
                if data is None:
                    return None

        return data


class DatePartsWidget(Widget):
    """
    Renders a set of ``<input type='text'/>`` controls based on the
    year, month, and day parts of the serialization of a
    :class:`colander.Date` object or a string in the format
    ``YYYY-MM-DD``.  This widget is usually meant to be used as widget
    which renders a :class:`colander.Date` type; validation
    likely won't work as you expect if you use it against a
    :class:`colander.String` object, but it is possible to use it
    with one if you use a proper validator.

    **Attributes/Arguments**

    template
        The template name used to render the input widget.  Default:
        ``dateparts``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/dateparts``.

    size
        The size (in columns) of each date part input control.
        Default: ``None`` (let browser decide).

    assume_y2k
        If a year is provided in 2-digit form, assume it means
        2000+year.  Default: ``True``.

    """
    template = 'dateparts'
    readonly_template = 'readonly/dateparts'
    size = None
    assume_y2k = True

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            year = ''
            month = ''
            day = ''
        else:
            year, month, day = cstruct.split('-', 2)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct,
                              year=year, month=month, day=day)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            return ''
        else:
            if self.assume_y2k:
                year = pstruct['year']
                if len(year) == 2:
                    pstruct['year'] = '20' + year
            result = '%(year)s-%(month)s-%(day)s' % pstruct
            if (not pstruct['year'] or not pstruct['month']
                or not pstruct['day']):
                raise Invalid(field.schema, _('Incomplete'), result)
            return result

class TextAreaCSVWidget(Widget):
    """
    Widget used for a sequence of scalars; allows for editing CSV
    within a text area.  Used with a schema node which is a sequence
    of tuples.
    
    **Attributes/Arguments**

    cols
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``cols`` is not included in the
        widget output (uses browser default cols).

    rows
        The size, in rows, of the text input field.  Defaults to
        ``None``, meaning that the ``rows`` is not included in the
        widget output (uses browser default cols).

    template
        The template name used to render the widget.  Default:
        ``textarea``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textarea``.
    """
    template = 'textarea'
    readonly_template = 'readonly/textarea'
    cols = None
    rows = None

    def serialize(self, field, cstruct=None, readonly=False):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = []
        textrows = getattr(field, 'unparseable', None)
        if textrows is None:
            outfile = StringIO.StringIO()
            writer = csv.writer(outfile)
            writer.writerows(cstruct)
            textrows = outfile.getvalue()
        if readonly:
            template = self.readonly_template
        else:
            template = self.template
        return field.renderer(template, field=field, cstruct=textrows)
        
    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ''
        if not pstruct.strip() and field.schema.required:
            # prevent
            raise Invalid(field.schema, 'Required', [])
        try:
            infile = StringIO.StringIO(pstruct)
            reader = csv.reader(infile)
            rows = list(reader)
        except Exception, e:
            field.unparseable = pstruct
            raise Invalid(field.schema, str(e))
        return rows

    def handle_error(self, field, error):
        msgs = []
        if error.msg:
            field.error = error
        else:
            for e in error.children:
                msgs.append('line %s: %s' % (e.pos+1, e))
            field.error = Invalid(field.schema, '\n'.join(msgs))
        

    
            
    
