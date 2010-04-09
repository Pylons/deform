import random
import string
import urllib

from deform.exception import Invalid

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
        form (although, if te field is a container field, its
        children will be; it is not a recursive flag).

    error_class
        The name of the CSS class attached to various tags in the form
        renderering indicating an error condition for the field
        associated with this widget.  By default, this is ``error``.

    static_url
        The URL to static resources required by the widget.
        Default: ``/static``

    These attributes are accepted as keyword arguments to all widget
    constructors.  Particular widget types also accept other keyword
    arguments that get attached to the widget as attributes.  These
    are documented as 'Attributes/Arguments' within the documentation
    of each concrete widget implementation subclass.
    """

    hidden = False
    error_class = 'error'
    static_url = '/static'

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def serialize(self, field, cstruct=None):
        """
        Serialize a :term:`cstruct` value (a value resulting from a
        :term:`Colander` schema serialization) to a form rendering and
        return the rendering.  The result of this method should always
        be a string (containing HTML).  The ``field`` argument is the
        field object to which this widget is attached.
        """
        raise NotImplementedError

    def deserialize(self, field, pstruct=None):
        """
        Deserialize a :term:`pstruct` value (a value resulting from
        the ``parse`` method of the :term:`Peppercorn` package) to a
        :term:`cstruct` value and return the :term:`cstruct` value.
        The ``field`` argument is the field object to which this
        widget is attached.
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

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """
    template = 'textinput'
    size = None
    strip = True

    def serialize(self, field, cstruct=None):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = ''
        return field.renderer(self.template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ''
        if self.strip:
            pstruct = pstruct.strip()
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

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """
    template = 'textarea'
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

    size
        The ``size`` attribute of the password input field (default:
        ``None``).

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """
    template = 'password'

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

    """
    true_val = 'true'
    false_val = 'false'

    template = 'checkbox'

    def serialize(self, field, cstruct=None):
        if cstruct is None:
            cstruct = field.default
        return field.renderer(self.template, field=field, cstruct=cstruct)

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
        values, e.g. ( ('true', 'True'), ('false', 'False') ).  The
        first element in the tuple is the value that should be
        returned when the form is posted.  The second is the display
        value.

    template
        The template name used to render the widget.  Default:
        ``radio_choice``.
    """
    template = 'radio_choice'
    values = ()

    def serialize(self, field, cstruct=None):
        if cstruct is None:
            cstruct = field.default
        return field.renderer(self.template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is None:
            pstruct = ''
        return pstruct

class CheckedInputWidget(Widget):
    """
    Renders two text input fields: 'value' and 'confirm'.
    Validates that the 'value' value matches the 'confirm' value.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``checked_input``.

    size
        The ``size`` attribute of the input fields (default:
        ``None``, default browser size).
    """
    template = 'checked_input'
    size = None
    mismatch_message = 'Fields did not match'
    subject = 'Value'

    def serialize(self, field, cstruct=None):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = ''
        confirm = getattr(field, 'confirm', '')
        return field.renderer(self.template, field=field, cstruct=cstruct,
                              confirm=confirm, subject=self.subject)
        
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

    size
        The ``size`` attribute of the password input field (default:
        ``None``).
    """
    template = 'checked_password'
    mismatch_message = 'Password did not match confirm'
    size = None

class MappingWidget(Widget):
    """
    Renders a mapping into a set of fields.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``mapping``.

    item_template
        The template name used to render each item in the mapping.
        Default: ``mapping_item``.

    """
    template = 'mapping'
    item_template = 'mapping_item'
    hidden = True
    error_class = None

    def serialize(self, field, cstruct=None):
        if cstruct is None:
            cstruct = {}
        return field.renderer(self.template, field=field, cstruct=cstruct)

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

    item_template
        The template name used to render each item in the form.
        Default: ``mapping_item``.
        
    """
    template = 'form'

class SequenceWidget(Widget):
    """
    Renders a sequence (0 .. N widgets, each the same as the other)
    into a set of fields.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``sequence``.

    item_template
        The template name used to render each value in the sequence.
        Default: ``sequence_item``.

    """
    hidden = True
    template = 'sequence'
    item_template = 'sequence_item'
    error_class = None

    def prototype(self, field):
        item_field = field.children[0]
        proto = field.renderer(self.item_template, field=item_field,
                               cstruct=None)
        if isinstance(proto, unicode):
            proto = proto.encode('utf-8')
        proto = urllib.quote(proto)
        return proto

    def serialize(self, field, cstruct=None):
        if cstruct is None:
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

        return field.renderer(self.template, field=field, cstruct=cstruct,
                              subfields=subfields)

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
    :class:`deform.schema.FileData` schema node.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``file_upload``.

    size
        The ``size`` attribute of the input field (default ``None``).
    """
    template = 'file_upload'
    size = None

    def __init__(self, tmpstore, **kw):
        Widget.__init__(self, **kw)
        self.tmpstore = tmpstore

    def random_id(self):
        return ''.join(
            [random.choice(string.uppercase+string.digits) for i in range(10)])

    def serialize(self, field, cstruct=None):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            cstruct = {}
        if cstruct:
            uid = cstruct['uid']
            if not uid in self.tmpstore:
                self.tmpstore[uid] = cstruct

        return field.renderer(self.template, field=field, cstruct=cstruct)

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
                # a previous file exists
                data = self.tmpstore[uid]

        return data


class DatePartsWidget(Widget):
    """
    Renders a set of ``<input type='text'/>`` controls based on the
    year, month, and day parts of the serialization of a
    :class:`deform.schema.Date` object or a string in the format
    ``YYYY-MM-DD``.  This widget is usually meant to be used as widget
    which renders a :class:`deform.schema.Date` type; validation
    likely won't work as you expect if you use it against a
    :class:`deform.schema.String` object, but it is possible to use it
    with one if you use a proper validator.

    **Attributes/Arguments**

    template
        The template name used to render the input widget.  Default:
        ``dateparts``.

    size
        The size (in columns) of each date part input control.
        Default: ``None`` (let browser decide).

    assume_y2k
        If a year is provided in 2-digit form, assume it means
        2000+year.  Default: ``True``.
        
    """
    template = 'dateparts'
    size = None
    assume_y2k = True

    def serialize(self, field, cstruct=None):
        if cstruct is None:
            cstruct = field.default
        if cstruct is None:
            year = ''
            month = ''
            day = ''
        else:
            year, month, day = cstruct.split('-', 2)
        return field.renderer(self.template, field=field, cstruct=cstruct,
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
                raise Invalid(field.schema, 'Incomplete', result)
            return result
