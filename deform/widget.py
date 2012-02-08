import csv
import random
import json 

from colander import Invalid
from colander import null

from deform.i18n import _

from deform.compat import (
    string_types,
    next,
    StringIO,
    string,
    url_quote,
    uppercase,
    )

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
    
    css_class
        The name of the CSS class attached to various tags in
        the form renderering specifying a new class for the field
        associated with this widget.  Default: ``None`` (no class).

    requirements
        A sequence of two-tuples in the form ``( (requirement_name,
        version_id), ...)`` indicating the logical external
        requirements needed to make this widget render properly within
        a form.  The ``requirement_name`` is a string that *logically*
        (not concretely, it is not a filename) identifies *one or
        more* Javascript or CSS resources that must be included in the
        page by the application performing the form rendering.  The
        requirement name string value should be interpreted as a
        logical requirement name (e.g. ``jquery`` for JQuery,
        'tinymce' for Tiny MCE).  The ``version_id`` is a string
        indicating the version number (or ``None`` if no particular
        version is required).  For example, a rich text widget might
        declare ``requirements = (('tinymce', '3.3.8'),)``.  See also:
        :ref:`specifying_widget_requirements` and
        :ref:`widget_requirements`.

        Default: ``()`` (the empty tuple, meaning no special
        requirements).

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
    css_class = None
    requirements = ()

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def serialize(self, field, cstruct, readonly=False):
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

    def deserialize(self, field, pstruct):
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
        """
        The ``handle_error`` method of a widget must:

        - Set the ``error`` attribute of the ``field`` object it is
          passed, if the ``error`` attribute has not already been set.

        - Call the ``handle_error`` method of each subfield which also
          has an error (as per the ``error`` argument's ``children``
          attribute).
        """
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

    mask
        A :term:`jquery.maskedinput` input mask, as a string.

        a - Represents an alpha character (A-Z,a-z)
        9 - Represents a numeric character (0-9)
        * - Represents an alphanumeric character (A-Z,a-z,0-9)

        All other characters in the mask will be considered mask
        literals.

        Example masks:

          Date: 99/99/9999

          US Phone: (999) 999-9999

          US SSN: 999-99-9999

        When this option is used, the :term:`jquery.maskedinput`
        library must be loaded into the page serving the form for the
        mask argument to have any effect.  See :ref:`masked_input`.

    mask_placeholder
        The placeholder for required nonliteral elements when a mask
        is used.  Default: ``_`` (underscore).
    """
    template = 'textinput'
    readonly_template = 'readonly/textinput'
    size = None
    strip = True
    mask = None
    mask_placeholder = "_"
    requirements = ( ('jquery.maskedinput', None), )

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ''
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct

class AutocompleteInputWidget(Widget):
    """
    Renders an ``<input type="text"/>`` widget which provides
    autocompletion via a list of values.

    When this option is used, the :term:`jquery.ui.autocomplete`
    library must be loaded into the page serving the form for
    autocompletion to have any effect.  See also
    :ref:`autocomplete_input`.  A version of :term:`JQuery UI` which
    includes the autoinclude sublibrary is included in the deform
    static directory. The default styles for JQuery UI are also
    available in the deform static/css directory.

    **Attributes/Arguments**

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).

    template
        The template name used to render the widget.  Default:
        ``autocomplete_textinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/autocomplete_textinput``.

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).

    values
        ``values`` from which :term:`jquery.ui.autocomplete` provides
        autocompletion. It MUST be an iterable that can be converted
        to a json array by [simple]json.dumps. It is also possible
        to pass a [base]string representing a remote URL.

        If ``values`` is a string it will be treated as a
        URL. If values is an iterable which can be serialized to a
        :term:`json` array, it will be treated as local data.

        If a string is provided to a URL, an :term:`xhr` request will
        be sent to the URL. The response should be a JSON
        serialization of a list of values.  For example:

          ['foo', 'bar', 'baz']

        Defaults to ``None``.

    min_length
        ``min_length`` is an optional argument to
        :term:`jquery.ui.autocomplete`. The number of characters to
        wait for before activating the autocomplete call.  Defaults to
        ``2``.

    delay
        ``delay`` is an optional argument to
        :term:`jquery.ui.autocomplete`. It sets the time to wait after a
        keypress to activate the autocomplete call.
        Defaults to ``10`` ms or ``400`` ms if a url is passed.
    """
    delay = None
    min_length = 2
    readonly_template = 'readonly/textinput'
    size = None
    strip = True
    template = 'autocomplete_input'
    values = None
    requirements = ( ('jqueryui', None), )

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ''
        options = {}
        if not self.delay:
            # set default delay if None
            options['delay'] = (isinstance(self.values,
                                          string_types) and 400) or 10
        options['minLength'] = self.min_length
        options = json.dumps(options)
        values = json.dumps(self.values)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template,
                              cstruct=cstruct,
                              field=field,
                              options=options,
                              values=values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct


class DateInputWidget(Widget):
    """
    
    Renders a JQuery UI date picker widget
    (http://jqueryui.com/demos/datepicker/).  Most useful when the
    schema node is a ``colander.Date`` object.

    **Attributes/Arguments**

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """
    template = 'dateinput'
    readonly_template = 'readonly/textinput'
    size = None
    requirements = ( ('jqueryui', None), )

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ''
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct in ('', null):
            return null
        return pstruct

class DateTimeInputWidget(DateInputWidget):
    """
    Renders a a jQuery UI date picker with a JQuery Timepicker add-on
    (http://trentrichardson.com/examples/timepicker/).  Used for
    ``colander.DateTime`` schema nodes.

    **Attributes/Arguments**

    options
        A dictionary of options that's passed to the datetimepicker.

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """
    template = 'datetimeinput'
    readonly_template = 'readonly/textinput'
    size = None
    requirements = ( ('jqueryui', None), ('datetimepicker', None), )
    option_defaults = {'dateFormat': 'yy-mm-dd',
                       'timeFormat': 'hh:mm:ss',
                       'separator': ' '}
    options = {}

    def _options(self):
        options = self.option_defaults.copy()
        options.update(self.options)
        return options

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ''
        template = readonly and self.readonly_template or self.template
        options = self._options()
        if len(cstruct) == 25: # strip timezone if it's there
            cstruct = cstruct[:-6]
        cstruct = options['separator'].join(cstruct.split('T'))
        return field.renderer(
            template,
            field=field,
            cstruct=cstruct,
            options=json.dumps(self._options()),
            )

    def deserialize(self, field, pstruct):
        if pstruct in ('', null):
            return null
        options = self._options()
        return pstruct.replace(options['separator'], 'T')

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

class RichTextWidget(TextInputWidget):
    """
    Renders a ``<textarea>`` widget with the
    :term:`TinyMCE Editor`.

    To use this widget the :term:`TinyMCE Editor` library must be
    provided in the page where the widget is rendered. A version of
    :term:`TinyMCE Editor` is included in deform's static directory.
    

    **Attributes/Arguments**

    height
        The height, in pixels, of the text editor.  Defaults to 240.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/richtext``.

    delayed_load
        If you have many richtext fields, you can set this option to
        ``true``, and the richtext editor will only be loaded when
        clicking on the field (default ``false``)

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).

    template
        The template name used to render the widget.  Default:
        ``richtext``.

    skin 
        The skin for the WYSIWYG editor. Normally only needed if you
        plan to reuse a TinyMCE js from another framework that
        defined a skin.

    theme
        The theme for the WYSIWYG editor, ``simple`` or ``advanced``.
        Defaults to ``simple``.

    width
        The width, in pixels, of the editor.  Defaults to 500.
        The width can also be given as a percentage (e.g. '100%')
        relative to the width of the enclosing element.
    """
    height = 240
    width = 500
    readonly_template = 'readonly/richtext'
    delayed_load = False
    strip = True
    template = 'richtext'
    skin = 'default'
    theme = 'simple'
    requirements = ( ('tinymce', None), )

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

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ''
        return field.renderer(self.template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if not pstruct:
            return null
        return pstruct

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

    def serialize(self, field, cstruct, readonly=False):
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return self.false_val
        return (pstruct == self.true_val) and self.true_val or self.false_val

class SelectWidget(Widget):
    """
    Renders ``<select>`` field based on a predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples (both values must be **string** or
        **unicode** values) indicating allowable, displayed values,
        e.g. ``( ('true', 'True'), ('false', 'False') )``.  The first
        element in the tuple is the value that should be returned when
        the form is posted.  The second is the display value.

    size
        The ``size`` attribute of the select input field (default:
        ``None``).

    null_value
        The value which represents the null value.  When the null
        value is encountered during serialization, the
        :attr:`colander.null` sentinel is returned to the caller.
        Default: ``''`` (the empty string).

    template
        The template name used to render the widget.  Default:
        ``select``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/select``.

    """
    template = 'select'
    readonly_template = 'readonly/select'
    null_value = ''
    values = ()
    size = None

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = self.null_value
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct in (null, self.null_value):
            return null
        return pstruct

class RadioChoiceWidget(SelectWidget):
    """
    Renders a sequence of ``<input type="radio"/>`` buttons based on a
    predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples (both values must be **string** or
        **unicode** values) indicating allowable, displayed values,
        e.g. ``( ('true', 'True'), ('false', 'False') )``.  The first
        element in the tuple is the value that should be returned when
        the form is posted.  The second is the display value.

    template
        The template name used to render the widget.  Default:
        ``radio_choice``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/radio_choice``.

    null_value
        The value used to replace the ``colander.null`` value when it
        is passed to the ``serialize`` or ``deserialize`` method.
        Default: the empty string.
    """
    template = 'radio_choice'
    readonly_template = 'readonly/radio_choice'

class CheckboxChoiceWidget(Widget):
    """
    Renders a sequence of ``<input type="check"/>`` buttons based on a
    predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples (both values must be **string** or
        **unicode** values) indicating allowable, displayed values,
        e.g. ``( ('true', 'True'), ('false', 'False') )``.  The first
        element in the tuple is the value that should be returned when
        the form is posted.  The second is the display value.

    template
        The template name used to render the widget.  Default:
        ``checkbox_choice``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/checkbox_choice``.

    null_value
        The value used to replace the ``colander.null`` value when it
        is passed to the ``serialize`` or ``deserialize`` method.
        Default: the empty string.
    """
    template = 'checkbox_choice'
    readonly_template = 'readonly/checkbox_choice'
    values = ()

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ()
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if isinstance(pstruct, string_types):
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

    mask
        A :term:`jquery.maskedinput` input mask, as a string.  Both
        input fields will use this mask.

        a - Represents an alpha character (A-Z,a-z)
        9 - Represents a numeric character (0-9)
        * - Represents an alphanumeric character (A-Z,a-z,0-9)

        All other characters in the mask will be considered mask
        literals.

        Example masks:

          Date: 99/99/9999

          US Phone: (999) 999-9999

          US SSN: 999-99-9999

        When this option is used, the :term:`jquery.maskedinput`
        library must be loaded into the page serving the form for the
        mask argument to have any effect.  See :ref:`masked_input`.

    mask_placeholder
        The placeholder for required nonliteral elements when a mask
        is used.  Default: ``_`` (underscore).
    """
    template = 'checked_input'
    readonly_template = 'readonly/checked_input'
    size = None
    mismatch_message = _('Fields did not match')
    subject = _('Value')
    confirm_subject = _('Confirm Value')
    mask = None
    mask_placeholder = "_"
    requirements = ( ('jquery.maskedinput', None), )

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = ''
        confirm = getattr(field, '%s-confirm' % (field.name,), '')
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct,
                              confirm=confirm, subject=self.subject,
                              confirm_subject=self.confirm_subject,
                              )

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        value = pstruct.get(field.name) or ''
        confirm = pstruct.get('%s-confirm' % (field.name,)) or ''
        setattr(field, '%s-confirm' % (field.name,), confirm)
        if (value or confirm) and (value != confirm):
            raise Invalid(field.schema, self.mismatch_message, value)
        if not value:
            return null
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
    requirements = ( ('deform', None), )

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = {}
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct,
                              null=null)

    def deserialize(self, field, pstruct):
        error = None
        
        result = {}

        if pstruct is null:
            pstruct = {}

        for num, subfield in enumerate(field.children):
            name = subfield.name
            subval = pstruct.get(name, null)
                            
            try:
                result[name] = subfield.deserialize(subval)
            except Invalid as e:
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
    """Renders a sequence (0 .. N widgets, each the same as the other)
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
        Deprecated boolean attribute indicating whether, on the first
        rendering of a form including this sequence widget, a single child
        widget rendering should be performed.  Default: ``False``.  This
        attribute is honored for backwards compatibility only: in new
        applications, please use ``min_len=1`` instead.

    min_len
        Integer indicating minimum number of acceptable subitems.  Default:
        ``None`` (meaning no minimum).  On the first rendering of a form
        including this sequence widget, at least this many subwidgets will be
        rendered.  The JavaScript sequence management will not allow fewer
        than this many subwidgets to be present in the sequence.

    max_len
        Integer indicating maximum number of acceptable subwidgets.  Default:
        ``None`` (meaning no maximum).  The JavaScript sequence management
        will not allow more than this many subwidgets to be added to the
        sequence.
    """
    template = 'sequence'
    readonly_template = 'readonly/sequence'
    item_template = 'sequence_item'
    readonly_item_template = 'readonly/sequence_item'
    error_class = None
    add_subitem_text_template = _('Add ${subitem_title}')
    render_initial_item = False
    min_len = None
    max_len = None
    requirements = ( ('deform', None), )

    def prototype(self, field):
        # we clone the item field to bump the oid (for easier
        # automated testing; finding last node)
        item_field = field.children[0].clone()
        proto = field.renderer(self.item_template, field=item_field,
                               cstruct=null, parent=field)
        if isinstance(proto, string_types):
            proto = proto.encode('utf-8')
        proto = url_quote(proto)
        return proto

    def serialize(self, field, cstruct, readonly=False):
        if (self.render_initial_item and self.min_len is None):
            # This is for compat only: ``render_initial_item=True`` should
            # now be spelled as ``min_len = 1``
            self.min_len = 1

        if cstruct in (null, None):
            if self.min_len is not None:
                cstruct = [null] * self.min_len
            else:
                cstruct = []

        cstructlen = len(cstruct)

        if self.min_len is not None and (cstructlen < self.min_len):
            cstruct = list(cstruct) + ([null] * (self.min_len-cstructlen))

        item_field = field.children[0]

        if getattr(field, 'sequence_fields', None):
            # this serialization is being performed as a result of a
            # validation failure (``deserialize`` was previously run)
            assert(len(cstruct) == len(field.sequence_fields))
            subfields = list(zip(cstruct, field.sequence_fields))
        else:
            # this serialization is being performed as a result of a
            # first-time rendering
            subfields = [ (val, item_field.clone()) for val in cstruct ]

        template = readonly and self.readonly_template or self.template
        translate = field.translate
        add_template_mapping = dict(
            subitem_title=translate(item_field.title),
            subitem_description=translate(item_field.description),
            subitem_name=item_field.name)
        add_subitem_text = _(self.add_subitem_text_template,
                             mapping=add_template_mapping)
        return field.renderer(template,
                              field=field,
                              cstruct=cstruct,
                              subfields=subfields,
                              item_field=item_field,
                              add_subitem_text=add_subitem_text)

    def deserialize(self, field, pstruct):
        result = []
        error = None

        if pstruct is null:
            pstruct = []

        field.sequence_fields = []
        item_field = field.children[0]

        for num, substruct in enumerate(pstruct):
            subfield = item_field.clone()
            try:
                subval = subfield.deserialize(substruct)
            except Invalid as e:
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

class filedict(dict):
    """ Use a dict subclass to make it easy to detect file upload
    dictionaries in application code before trying to write them to
    persistent objects."""

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
            [random.choice(uppercase+string.digits) for i in range(10)])

    def serialize(self, field, cstruct, readonly=False):
        if cstruct in (null, None):
            cstruct = {}
        if cstruct:
            uid = cstruct['uid']
            if not uid in self.tmpstore:
                self.tmpstore[uid] = cstruct

        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null

        upload = pstruct.get('upload')
        uid = pstruct.get('uid')

        if hasattr(upload, 'file'):
            # the upload control had a file selected
            data = filedict()
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
                return null
            else:
                # a previous file should exist
                data = self.tmpstore.get(uid)
                # but if it doesn't, don't blow up
                if data is None:
                    return null

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

    def serialize(self, field, cstruct, readonly=False):
        if cstruct is null:
            year = ''
            month = ''
            day = ''
        else:
            year, month, day = cstruct.split('-', 2)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, field=field, cstruct=cstruct,
                              year=year, month=month, day=day)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            year = pstruct['year'].strip()
            month = pstruct['month'].strip()
            day = pstruct['day'].strip()
            
            if (not year and not month and not day):
                return null

            if self.assume_y2k and len(year) == 2:
                year = '20' + year
            result = '-'.join([year, month, day])

            if (not year or not month or not day):
                raise Invalid(field.schema, _('Incomplete date'), result)

            return result

class TextAreaCSVWidget(Widget):
    """
    Widget used for a sequence of tuples of scalars; allows for
    editing CSV within a text area.  Used with a schema node which is
    a sequence of tuples.
    
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

    def serialize(self, field, cstruct, readonly=False):
        if cstruct is null:
            cstruct = []
        textrows = getattr(field, 'unparseable', None)
        if textrows is None:
            outfile = StringIO()
            writer = csv.writer(outfile)
            writer.writerows(cstruct)
            textrows = outfile.getvalue()
        if readonly:
            template = self.readonly_template
        else:
            template = self.template
        return field.renderer(template, field=field, cstruct=textrows)
        
    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if not pstruct.strip():
            return null
        try:
            infile = StringIO(pstruct)
            reader = csv.reader(infile)
            rows = list(reader)
        except Exception as e:
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


class TextInputCSVWidget(Widget):
    """
    Widget used for a tuple of scalars; allows for editing a single
    CSV line within a text input.  Used with a schema node which is a
    tuple composed entirely of scalar values (integers, strings, etc).
    
    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``textinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.

    size
        The size, in columns, of the text input field.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).
    """
    template = 'textinput'
    readonly_template = 'readonly/textinput'
    size = None
    mask = None

    def serialize(self, field, cstruct, readonly=False):
        if cstruct is null:
            cstruct = ''
        textrow = getattr(field, 'unparseable', None)
        if textrow is None:
            outfile = StringIO()
            writer = csv.writer(outfile)
            writer.writerow(cstruct)
            textrow = outfile.getvalue().strip()
        if readonly:
            template = self.readonly_template
        else:
            template = self.template
        return field.renderer(template, field=field, cstruct=textrow)
        
    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if not pstruct.strip():
            return null
        try:
            infile = StringIO(pstruct)
            reader = csv.reader(infile)
            #row = reader.next()
            row = next(reader)
        except Exception as e:
            field.unparseable = pstruct
            raise Invalid(field.schema, str(e))
        return row

    def handle_error(self, field, error):
        msgs = []
        if error.msg:
            field.error = error
        else:
            for e in error.children:
                msgs.append('%s' % e)
            field.error = Invalid(field.schema, '\n'.join(msgs))

class ResourceRegistry(object):
    """ A resource registry maps :term:`widget requirement` name/version
    pairs to one or more relative resources.  A resource registry can
    be passed to a :class:`deform.Form` constructor; if a resource
    registry is *not* passed to the form constructor, a default
    resource registry is used by that form.  The default resource
    registry contains only mappings from requirement names to
    resources required by the built-in Deform widgets (not by any
    add-on widgets).

    If the ``use_defaults`` flag is True, the default set of Deform
    requirement-to-resource mappings is loaded into the registry.
    Otherwise, the registry is initialized without any mappings.
    """
    def __init__(self, use_defaults=True):
        if use_defaults is True:
            self.registry = default_resources.copy()
        else:
            self.registry = {}

    def set_js_resources(self, requirement, version, *resources):
        """ Set the Javascript resources for the requirement/version
        pair, using ``resources`` as the set of relative resource paths."""
        reqt = self.registry.setdefault(requirement, {})
        ver = reqt.setdefault(version, {})
        ver['js'] = resources

    def set_css_resources(self, requirement, version, *resources):
        """ Set the CSS resources for the requirement/version
        pair, using ``resources`` as the set of relative resource paths."""
        reqt = self.registry.setdefault(requirement, {})
        ver = reqt.setdefault(version, {})
        ver['css'] = resources

    def __call__(self, requirements):
        """ Return a dictionary representing the resources required
        for a particular set of requirements (as returned by
        :meth:`deform.Field.get_widget_requirements`).  The dictionary
        will be a mapping from resource type (``js`` and ``css`` are
        both keys in the dictionary) to a list of relative resource
        paths.  Each path is relative to wherever you've mounted
        Deform's ``static`` directory in your web server.  You can use
        the paths for each resource type to inject CSS and Javascript
        on-demand into the head of dynamic pages that render Deform
        forms.  """
        result = {'js':[], 'css':[]}
        for requirement, version in requirements:
            tmp = self.registry.get(requirement)
            if tmp is None:
                raise ValueError(
                    'Cannot resolve widget requirement %r' % requirement)
            versioned = tmp.get(version)
            if versioned is None:
                raise ValueError(
                    'Cannot resolve widget requirement %r (version %r)' % (
                        (requirement, version)))
            for thing in ('js', 'css'):
                sources = versioned.get(thing)
                if sources is None:
                    continue
                if isinstance(sources, string_types):
                    sources = (sources,)
                for source in sources:
                    if not source in result[thing]:
                        result[thing].append(source)
        return result

            
default_resources = {
    'jquery': {
        None:{
            'js':'scripts/jquery-1.4.2.min.js',
            },
        },
    'jqueryui': {
        None:{
            'js':('scripts/jquery-1.4.2.min.js',
                  'scripts/jquery-ui-1.8.11.custom.min.js'),
            'css':'css/ui-lightness/jquery-ui-1.8.11.custom.css',
            },
        },
    'jquery.form': {
        None:{
            'js':('scripts/jquery-1.4.2.min.js',
                  'scripts/jquery.form.js'),
            },
        },
    'jquery.maskedinput': {
        None:{
            'js':('scripts/jquery-1.4.2.min.js',
                  'scripts/jquery.maskedinput-1.2.2.min.js'),
            },
        },
    'datetimepicker': {
        None:{
            'js':('scripts/jquery-1.4.2.min.js',
                  'scripts/jquery-ui-timepicker-addon.js'),
            'css':'css/jquery-ui-timepicker-addon.css',
            },
        },
    'deform': {
        None:{
            'js':('scripts/jquery-1.4.2.min.js',
                  'scripts/jquery.form.js',
                  'scripts/deform.js'),
            'css':('css/form.css')

            },
        },
    'tinymce': {
        None:{
            'js':'tinymce/jscripts/tiny_mce/tiny_mce.js',
            },
        },
    }

default_resource_registry = ResourceRegistry()
