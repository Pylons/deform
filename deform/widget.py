"""Widget."""
# Standard Library
import csv
import json
import random

# Pyramid
from colander import Invalid
from colander import Mapping
from colander import SchemaNode
from colander import SchemaType
from colander import Sequence
from colander import String
from colander import null
from iso8601.iso8601 import ISO8601_REGEX
from translationstring import TranslationString

from .compat import StringIO
from .compat import string
from .compat import string_types
from .compat import text_
from .compat import text_type
from .compat import uppercase
from .compat import url_quote
from .i18n import _


_BLANK = text_("")


def _normalize_choices(values):
    result = []
    for item in values:
        if isinstance(item, OptGroup):
            normalized_options = _normalize_choices(item.options)
            result.append(OptGroup(item.label, *normalized_options))
        else:
            value, description = item
            if not isinstance(value, string_types):
                value = str(value)
            result.append((value, description))
    return result


class _PossiblyEmptyString(String):
    def deserialize(self, node, cstruct):
        if cstruct == "":
            return _BLANK  # String.deserialize returns null
        return super(_PossiblyEmptyString, self).deserialize(node, cstruct)


class _StrippedString(_PossiblyEmptyString):
    def deserialize(self, node, cstruct):
        appstruct = super(_StrippedString, self).deserialize(node, cstruct)
        if isinstance(appstruct, string_types):
            appstruct = appstruct.strip()
        return appstruct


class _FieldStorage(SchemaType):
    def deserialize(self, node, cstruct):
        if cstruct in (null, None, b""):
            return null
        # weak attempt at duck-typing
        if not hasattr(cstruct, "file"):
            raise Invalid(node, "%s is not a FieldStorage instance" % cstruct)
        return cstruct


_sequence_of_strings = SchemaNode(
    Sequence(), SchemaNode(_PossiblyEmptyString())
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

    readonly
        If this attribute is true, the readonly rendering of the widget
        should be output during HTML serialization.

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

    item_css_class
        The name of the CSS class attached to the li which surrounds the field
        when it is rendered inside the mapping_item or sequence_item template.

    style
        A string that will be placed literally in a ``style`` attribute on
        the primary input tag(s) related to the widget.  For example,
        'width:150px;'.  Default: ``None``, meaning no style attribute will
        be added to the input tag.

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
    readonly = False
    category = "default"
    error_class = "error"
    css_class = None
    item_css_class = None
    style = None
    requirements = ()

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def serialize(self, field, cstruct, **kw):
        """
        The ``serialize`` method of a widget must serialize a :term:`cstruct`
        value to an HTML rendering.  A :term:`cstruct` value is the value
        which results from a :term:`Colander` schema serialization for the
        schema node associated with this widget.  ``serialize`` should return
        the HTML rendering: the result of this method should always be a
        string containing HTML.  The ``field`` argument is the :term:`field`
        object to which this widget is attached.  The ``**kw`` argument
        allows a caller to pass named arguments that might be used to
        influence individual widget renderings.
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
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    subfield.widget.handle_error(subfield, e)

    def get_template_values(self, field, cstruct, kw):
        values = {"cstruct": cstruct, "field": field}
        values.update(kw)
        values.pop("template", None)
        return values


class TextInputWidget(Widget):
    """
    Renders an ``<input type="text"/>`` widget.

    **Attributes/Arguments**

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

    template = "textinput"
    readonly_template = "readonly/textinput"
    strip = True
    mask = None
    mask_placeholder = "_"
    requirements = (("jquery.maskedinput", None),)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct


class MoneyInputWidget(Widget):
    """
    Renders an ``<input type="text"/>`` widget with Javascript which enforces
    a valid currency input.  It should be used along with the
    ``colander.Decimal`` schema type (at least if you care about your money).
    This widget depends on the ``jquery-maskMoney`` JQuery plugin.

    **Attributes/Arguments**

    template
       The template name used to render the widget.  Default:
        ``moneyinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.

    options
        A dictionary or sequence of two-tuples containing ``jquery-maskMoney``
        options.  The valid options are:

        symbol
            the symbol to be used before of the user values. default: ``$``

        showSymbol
            set if the symbol must be displayed or not. default: ``False``

        symbolStay
            set if the symbol will stay in the field after the user exists the
            field. default: ``False``

        thousands
            the thousands separator. default: ``,``

        decimal
            the decimal separator. default: ``.``

        precision
            how many decimal places are allowed. default: 2

        defaultZero
            when the user enters the field, it sets a default mask using zero.
            default: ``True``

        allowZero
            use this setting to prevent users from inputing zero. default:
            ``False``

        allowNegative
            use this setting to prevent users from inputing negative values.
            default: ``False``
    """

    template = "moneyinput"
    readonly_template = "readonly/textinput"
    requirements = (("jquery.maskMoney", None),)
    options = None

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        options = kw.get("options", self.options)
        if options is None:
            options = {}
        options = json.dumps(dict(options))
        kw["mask_options"] = options
        values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        pstruct = pstruct.strip()
        thousands = ","
        # Oh jquery-maskMoney, you submit the thousands separator in the
        # control value.  I'm no genius, but IMO that's not very smart.  But
        # then again you also don't inject the thousands separator into the
        # value attached to the control when editing an existing value.
        # Because it's obvious we should have *both* the server and the
        # client doing this bullshit on both serialization and
        # deserialization.  I understand completely, you're just a client
        # library, IT'S NO PROBLEM.  LET ME HELP YOU.
        if self.options:
            thousands = dict(self.options).get("thousands", ",")
        pstruct = pstruct.replace(thousands, "")
        if not pstruct:
            return null
        return pstruct


class AutocompleteInputWidget(Widget):
    """
    Renders an ``<input type="text"/>`` widget which provides
    autocompletion via a list of values using bootstrap's typeahead plugin
    https://github.com/twitter/typeahead.js/

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``typeahead_textinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/typeahead_textinput``.

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).

    values
        A list of strings or string.
        Defaults to ``[]``.

        If ``values`` is a string it will be treated as a
        URL. If values is an iterable which can be serialized to a
        :term:`JSON` array, it will be treated as local data.

        If a string is provided to a URL, an :term:`XHR` request will
        be sent to the URL. The response should be a JSON
        serialization of a list of values.  For example:

          ['foo', 'bar', 'baz']

    min_length
        ``min_length`` is an optional argument to
        :term:`jquery.ui.autocomplete`. The number of characters to
        wait for before activating the autocomplete call.  Defaults to
        ``1``.

    items
        The max number of items to display in the dropdown. Defaults to
        ``8``.

    """

    min_length = 1
    readonly_template = "readonly/textinput"
    strip = True
    items = 8
    template = "autocomplete_input"
    values = None
    requirements = (("typeahead", None), ("deform", None))

    def serialize(self, field, cstruct, **kw):
        if "delay" in kw or getattr(self, "delay", None):
            raise ValueError(
                "AutocompleteWidget does not support *delay* parameter "
                "any longer."
            )
        if cstruct in (null, None):
            cstruct = ""
        self.values = self.values or []
        readonly = kw.get("readonly", self.readonly)

        options = {}
        if isinstance(self.values, string_types):
            options["remote"] = "%s?term=%%QUERY" % self.values
        else:
            options["local"] = self.values

        options["minLength"] = kw.pop("min_length", self.min_length)
        options["limit"] = kw.pop("items", self.items)
        kw["options"] = json.dumps(options)
        tmpl_values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct


class TimeInputWidget(Widget):
    """
    Renders a time picker widget.

    The default rendering is as a native HTML5 time input widget,
    falling back to pickadate (https://github.com/amsul/pickadate.js.)

    Most useful when the schema node is a ``colander.Time`` object.

    **Attributes/Arguments**

    style
        A string that will be placed literally in a ``style`` attribute on
        the text input tag.  For example, 'width:150px;'.  Default: ``None``,
        meaning no style attribute will be added to the input tag.

    options
        Options for configuring the widget (eg: date format)

    template
        The template name used to render the widget.  Default:
        ``timeinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/timeinput``.
    """

    template = "timeinput"
    readonly_template = "readonly/textinput"
    type_name = "time"
    size = None
    style = None
    requirements = (("modernizr", None), ("pickadate", None))
    default_options = (("format", "HH:i"),)

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(_StrippedString(), name="time"),
        SchemaNode(_StrippedString(), name="time_submit", missing=""),
    )

    def __init__(self, *args, **kwargs):
        self.options = dict(self.default_options)
        self.options["formatSubmit"] = "HH:i"
        Widget.__init__(self, *args, **kwargs)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        options = dict(
            kw.get("options") or self.options or self.default_options
        )
        options["formatSubmit"] = "HH:i"
        kw.setdefault("options_json", json.dumps(options))
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct in ("", null):
            return null
        try:
            validated = self._pstruct_schema.deserialize(pstruct)
        except Invalid as exc:
            raise Invalid(field.schema, text_("Invalid pstruct: %s" % exc))
        return validated["time_submit"] or validated["time"]


class DateInputWidget(Widget):
    """
    Renders a date picker widget.

    The default rendering is as a native HTML5 date input widget,
    falling back to pickadate (https://github.com/amsul/pickadate.js.)

    Most useful when the schema node is a ``colander.Date`` object.

    **Attributes/Arguments**

    options
        Dictionary of options for configuring the widget (eg: date format)

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """

    template = "dateinput"
    readonly_template = "readonly/textinput"
    type_name = "date"
    requirements = (("modernizr", None), ("pickadate", None))
    default_options = (
        ("format", "yyyy-mm-dd"),
        ("selectMonths", True),
        ("selectYears", True),
    )
    options = None

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(_StrippedString(), name="date"),
        SchemaNode(_StrippedString(), name="date_submit", missing=""),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        options = dict(
            kw.get("options") or self.options or self.default_options
        )
        options["formatSubmit"] = "yyyy-mm-dd"
        kw.setdefault("options_json", json.dumps(options))
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct in ("", null):
            return null
        try:
            validated = self._pstruct_schema.deserialize(pstruct)
        except Invalid as exc:
            raise Invalid(field.schema, "Invalid pstruct: %s" % exc)
        return validated["date_submit"] or validated["date"]


class DateTimeInputWidget(Widget):
    """
    Renders a datetime picker widget.

    The default rendering is as a pair of inputs (a date and a time) using
    pickadate.js (https://github.com/amsul/pickadate.js).

    Used for ``colander.DateTime`` schema nodes.

    **Attributes/Arguments**

    date_options
        A dictionary of date options passed to pickadate.

    time_options
        A dictionary of time options passed to pickadate.

    template
        The template name used to render the widget.  Default:
        ``dateinput``.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/textinput``.
    """

    template = "datetimeinput"
    readonly_template = "readonly/datetimeinput"
    type_name = "datetime"
    requirements = (("modernizr", None), ("pickadate", None))
    default_date_options = (
        ("format", "yyyy-mm-dd"),
        ("selectMonths", True),
        ("selectYears", True),
    )
    date_options = None
    default_time_options = (("format", "h:i A"), ("interval", 30))
    time_options = None

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(_StrippedString(), name="date"),
        SchemaNode(_StrippedString(), name="time"),
        SchemaNode(_StrippedString(), name="date_submit", missing=""),
        SchemaNode(_StrippedString(), name="time_submit", missing=""),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        if cstruct:
            parsed = ISO8601_REGEX.match(cstruct)
            if parsed:  # strip timezone if it's there
                timezone = parsed.groupdict()["timezone"]
                if timezone and cstruct.endswith(timezone):
                    cstruct = cstruct[: -len(timezone)]

        try:
            date, time = cstruct.split("T", 1)
            try:
                # get rid of milliseconds
                time, _ = time.split(".", 1)
            except ValueError:
                pass
            kw["date"], kw["time"] = date, time
        except ValueError:  # need more than one item to unpack
            kw["date"] = kw["time"] = ""

        date_options = dict(
            kw.get("date_options")
            or self.date_options
            or self.default_date_options
        )
        date_options["formatSubmit"] = "yyyy-mm-dd"
        kw["date_options_json"] = json.dumps(date_options)

        time_options = dict(
            kw.get("time_options")
            or self.time_options
            or self.default_time_options
        )
        time_options["formatSubmit"] = "HH:i"
        kw["time_options_json"] = json.dumps(time_options)

        values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, "Invalid pstruct: %s" % exc)
            # seriously pickadate?  oh.  right.  i forgot.  you're javascript.
            date = validated["date_submit"] or validated["date"]
            time = validated["time_submit"] or validated["time"]

            if not time and not date:
                return null

            result = "T".join([date, time])

            if not date:
                raise Invalid(field.schema, _("Incomplete date"), result)

            if not time:
                raise Invalid(field.schema, _("Incomplete time"), result)

            return result


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
        Default: ``readonly/textinput``.


    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace (default ``True``).
    """

    template = "textarea"
    readonly_template = "readonly/textinput"
    cols = None
    rows = None
    strip = True


class RichTextWidget(TextInputWidget):
    """
    Renders a ``<textarea>`` widget with the
    :term:`TinyMCE Editor`.

    To use this widget the :term:`TinyMCE Editor` library must be
    provided in the page where the widget is rendered. A version of
    :term:`TinyMCE Editor` is included in Deform's ``static`` directory.


    **Attributes/Arguments**

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/richtext``.

    delayed_load
        If you have many richtext fields, you can set this option to
        ``True``, and the richtext editor will only be loaded upon
        the user clicking the field. Default: ``False``.

        **Security Note**: Enabling ``delayed_load`` can create an
        HTML injection vulnerability. When enabled, any existing value
        for the field will be rendered without HTML escaping. Also,
        on form re-display, any user-submitted value which passes
        validation will be rendered unescaped.  (If the field has a
        validation error, ``delayed_load`` will be disabled during
        re-display.) You should not enable ``delayed_load`` unless you
        trust both existing and valid user-submitted values for the field
        to be 'safe HTML'.

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace. Default: ``True``.

    template
        The template name used to render the widget.  Default:
        ``richtext``.

    options
        A dictionary or sequence of two-tuples containing additional
        options to pass to the TinyMCE ``init`` function call. All types
        within such structure should be Python native as the structure
        will be converted to JSON on serialization. This widget provides
        some sensible defaults, as described below in
        :attr:`default_options`.

        You should refer to the `TinyMCE Configuration
        <https://www.tiny.cloud/docs/configure/>`_ documentation
        for details regarding all available configuration options.

        The ``language`` option is passed to TinyMCE within the default
        template, using i18n machinery to determine the language to use.
        This option can be overridden if it is specified here in ``options``.

        *Note*: the ``elements`` option for TinyMCE is set automatically
        according to the given field's ``oid``.

        Default: ``None`` (no additional options)

    Note that the RichTextWidget template does not honor the ``css_class``
    or ``style`` attributes of the widget.

    """

    readonly_template = "readonly/richtext"
    delayed_load = False
    strip = True
    template = "richtext"
    requirements = (("tinymce", None),)

    #: Default options passed to TinyMCE. Customise by using :attr:`options`.
    default_options = (
        ("height", 240),
        ("width", 0),
        ("skin", "lightgray"),
        ("theme", "modern"),
        ("mode", "exact"),
        ("strict_loading_mode", True),
        ("theme_advanced_resizing", True),
        ("theme_advanced_toolbar_align", "left"),
        ("theme_advanced_toolbar_location", "top"),
    )
    #: Options to pass to TinyMCE that will override :attr:`default_options`.
    options = None

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)

        options = dict(self.default_options)
        # Accept overrides from keywords or as an attribute
        options_overrides = dict(kw.get("options", self.options or {}))
        options.update(options_overrides)
        # Dump to JSON and strip curly braces at start and end
        kw["tinymce_options"] = json.dumps(options)[1:-1]

        values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **values)


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

    strip
        If true, during deserialization, strip the value of leading
        and trailing whitespace. Default: ``True``.

    redisplay
        If true, on validation failure, retain and redisplay the password
        input.  If false, on validation failure, this field will be
        rendered empty.  Default: ``False``.

    """

    template = "password"
    readonly_template = "readonly/password"
    redisplay = False


class HiddenWidget(Widget):
    """
    Renders an ``<input type="hidden"/>`` widget.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``hidden``.
    """

    template = "hidden"
    hidden = True

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(self.template, **values)

    def deserialize(self, field, pstruct):
        if not pstruct:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
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

    true_val = "true"
    false_val = "false"

    template = "checkbox"
    readonly_template = "readonly/checkbox"

    def serialize(self, field, cstruct, **kw):
        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return self.false_val
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        return (pstruct == self.true_val) and self.true_val or self.false_val


class OptGroup(object):
    """
    Used in the ``values`` argument passed to an instance of
    ``SelectWidget`` to render an ``<optgroup>`` HTML tag.

    **Attributes/Arguments**

    label
        The label of the ``<optgroup>`` HTML tag.

    options
        A sequence that describes the ``<options>`` HTML tag(s). It
        must have the same structure as the ``values``
        argument/parameter in the ``SelectWidget`` class, but should
        not contain ``OptGroup`` instances since ``<optgroup>`` HTML
        tags cannot be nested.
    """

    def __init__(self, label, *options):
        self.label = label
        self.options = options


class SelectWidget(Widget):
    """
    Renders ``<select>`` field based on a predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of items where each item must be either:

        - a two-tuple (the first value must be of type string, unicode
          or integer, the second value must be string or unicode)
          indicating allowable, displayed values, e.g. ``('jsmith',
          'John Smith')``. The first element in the tuple is the value
          that should be returned when the form is posted. The second
          is the display value;

        - or an instance of ``optgroup_class`` (which is
          ``deform.widget.OptGroup`` by default).

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

    multiple
        Enable multiple on the select widget ( default: ``False`` )

    optgroup_class
        The class used to represent ``<optgroup>`` HTML tags. Default:
        ``deform.widget.OptGroup``.

    long_label_generator
        A function that returns the "long label" used as the
        description for very old browsers that do not support the
        ``<optgroup>`` HTML tag. If a function is provided, the
        ``label`` attribute will receive the (short) description,
        while the content of the ``<option>`` tag will receive the
        "long label". The function is called with two parameters: the
        group label and the option (short) description.

        For example, with the following widget:

        .. code-block:: python

           long_label_gener = lambda group, label: ' - '.join((group, label))
           SelectWidget(
             values=(
               ('', 'Select your favorite musician'),
               OptGroup('Guitarists',
                        ('page', 'Jimmy Page'),
                        ('hendrix', 'Jimi Hendrix')),
               OptGroup('Drummers',
                       ('cobham', 'Billy Cobham'),
                       ('bonham', 'John Bonham'))),
             long_label_generator=long_label_gener)

        ... the rendered options would look like:

        .. code-block:: html

           <option value="">Select your favorite musician</option>
           <optgroup label="Guitarists">
             <option value="page"
                 label="Jimmy Page">Guitarists - Jimmy Page</option>
             <option value="hendrix"
                 label="Jimi Hendrix">Guitarists - Jimi Hendrix</option>
           </optgroup>
           <optgroup label="Drummers">
             <option value="cobham"
                 label="Billy Cobham">Drummers - Billy Cobham</option>
             <option value="bonham"
                 label="John Bonham">Drummers - John Bonham</option>
           </optgroup>

        Default: ``None`` (which means that the ``label`` attribute is
        not rendered).

    size
        The size, in rows, of the select list.  Defaults to
        ``None``, meaning that the ``size`` is not included in the
        widget output (uses browser default size).
    """

    template = "select"
    readonly_template = "readonly/select"
    null_value = ""
    values = ()
    size = None
    multiple = False
    optgroup_class = OptGroup
    long_label_generator = None

    def get_select_value(self, cstruct, value):
        """Choose whether <opt> is selected or not.

        Incoming value is always string, as it has been passed through HTML.
        However, our values might be given as integer, UUID.
        """

        if self.multiple:
            if value in map(text_type, cstruct):
                return "selected"
        else:
            if value == text_type(cstruct):
                return "selected"

        return None

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = self.null_value
        readonly = kw.get("readonly", self.readonly)
        values = kw.get("values", self.values)
        template = readonly and self.readonly_template or self.template
        kw["values"] = _normalize_choices(values)
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct in (null, self.null_value):
            return null
        if self.multiple:
            try:
                return _sequence_of_strings.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, "Invalid pstruct: %s" % exc)
        else:
            if not isinstance(pstruct, string_types):
                raise Invalid(field.schema, "Pstruct is not a string")
            return pstruct


class Select2Widget(SelectWidget):
    """
    Renders ``<select>`` field based on a predefined set of values using
    `select2 <https://select2.org/>`_ library.

    **Attributes/Arguments**

    Same as :func:`~deform.widget.SelectWidget`, with some extra options
    listed here.

    tags: *bool*
        Allow dynamic option creation ( default: ``False`` ).
        See `select2 docs on tagging <https://select2.org/tagging>`_ for
        more details.
    """

    template = "select2"
    requirements = (("deform", None), ("select2", None))


class RadioChoiceWidget(SelectWidget):
    """
    Renders a sequence of ``<input type="radio"/>`` buttons based on a
    predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples (the first value must be of type
        string, unicode or integer, the second value must be string or
        unicode) indicating allowable, displayed values, e.g. ``(
        ('true', 'True'), ('false', 'False') )``.  The first element
        in the tuple is the value that should be returned when the
        form is posted.  The second is the display value.

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

    inline
        If true, choices will be rendered on a single line.
        Otherwise choices will be rendered one per line.
        Default: false.
    """

    template = "radio_choice"
    readonly_template = "readonly/radio_choice"


class CheckboxChoiceWidget(Widget):
    """
    Renders a sequence of ``<input type="check"/>`` buttons based on a
    predefined set of values.

    **Attributes/Arguments**

    values
        A sequence of two-tuples (the first value must be of type
        string, unicode or integer, the second value must be string or
        unicode) indicating allowable, displayed values, e.g. ``(
        ('true', 'True'), ('false', 'False') )``.  The first element
        in the tuple is the value that should be returned when the
        form is posted.  The second is the display value.

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

    inline
        If true, choices will be rendered on a single line.
        Otherwise choices will be rendered one per line.
        Default: false.
    """

    template = "checkbox_choice"
    readonly_template = "readonly/checkbox_choice"
    values = ()

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ()
        readonly = kw.get("readonly", self.readonly)
        values = kw.get("values", self.values)
        kw["values"] = _normalize_choices(values)
        template = readonly and self.readonly_template or self.template
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if isinstance(pstruct, string_types):
            return (pstruct,)
        try:
            validated = _sequence_of_strings.deserialize(pstruct)
        except Invalid as exc:
            raise Invalid(field.schema, "Invalid pstruct: %s" % exc)
        return tuple(validated)


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
        Default: ``readonly/textinput``.

    mismatch_message
        The message to be displayed when the value in the primary
        field does not match the value in the confirm field.

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

    template = "checked_input"
    readonly_template = "readonly/textinput"
    mismatch_message = _("Fields did not match")
    subject = _("Value")
    confirm_subject = _("Confirm Value")
    mask = None
    mask_placeholder = "_"
    requirements = (("jquery.maskedinput", None),)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ""
        readonly = kw.get("readonly", self.readonly)
        kw.setdefault("subject", self.subject)
        kw.setdefault("confirm_subject", self.confirm_subject)
        confirm = getattr(field, "%s-confirm" % (field.name,), cstruct)
        kw["confirm"] = confirm
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        confirm_name = "%s-confirm" % field.name
        schema = SchemaNode(
            Mapping(),
            SchemaNode(_PossiblyEmptyString(), name=field.name),
            SchemaNode(_PossiblyEmptyString(), name=confirm_name),
        )
        try:
            validated = schema.deserialize(pstruct)
        except Invalid as exc:
            raise Invalid(field.schema, "Invalid pstruct: %s" % exc)
        value = validated[field.name]
        confirm = validated[confirm_name]
        setattr(field, confirm_name, confirm)
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

    mismatch_message
        The string shown in the error message when a validation failure is
        caused by the confirm field value does not match the password
        field value.  Default: ``Password did not match confirm``.

    redisplay
        If true, on validation failure involving a field with this widget,
        retain and redisplay the provided values in the password inputs.  If
        false, on validation failure, the fields will be rendered empty.
        Default:: ``False``.
        """

    template = "checked_password"
    readonly_template = "readonly/checked_password"
    mismatch_message = _("Password did not match confirm")
    redisplay = False


class MappingWidget(Widget):
    """
    Renders a mapping into a set of fields.

    **Attributes/Arguments**

    template
        The template name used to render the widget.  Default:
        ``mapping``. See also ``mapping_accordion`` template for hideable
        user experience.

    readonly_template
        The template name used to render the widget in read-only mode.
        Default: ``readonly/mapping``.

    item_template
        The template name used to render each item in the mapping.
        Default: ``mapping_item``.

    readonly_item_template
        The template name used to render each item in the form.
        Default: ``readonly/mapping_item``.

    open: bool
        Used with ``mapping_accordion`` template to define if the
        mapping subform accordion is open or closed by default.

    Note that the MappingWidget template does not honor the ``css_class``
    or ``style`` attributes of the widget.
    """

    template = "mapping"
    readonly_template = "readonly/mapping"
    item_template = "mapping_item"
    readonly_item_template = "readonly/mapping_item"
    error_class = None
    category = "structural"
    requirements = (("deform", None),)

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = {}
        readonly = kw.get("readonly", self.readonly)
        kw.setdefault("null", null)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        error = None

        result = {}

        if pstruct is null:
            pstruct = {}
        elif not isinstance(pstruct, dict):
            raise Invalid(field.schema, "Pstruct is not a dict")

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

    template = "form"
    readonly_template = "readonly/form"


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

    orderable
        Boolean indicating whether the Javascript sequence management will
        allow the user to explicitly re-order the subwidgets.
        Default: ``False``.

    Note that the SequenceWidget template does not honor the ``css_class``
    or ``style`` attributes of the widget.

    """

    template = "sequence"
    readonly_template = "readonly/sequence"
    item_template = "sequence_item"
    readonly_item_template = "readonly/sequence_item"
    error_class = None
    add_subitem_text_template = _("Add ${subitem_title}")
    min_len = None
    max_len = None
    orderable = False
    requirements = (("deform", None), ("sortable", None))

    def prototype(self, field):
        # we clone the item field to bump the oid (for easier
        # automated testing; finding last node)
        item_field = field.children[0].clone()
        if not item_field.name:
            info = "Prototype for %r has no name" % field
            raise ValueError(info)
        # NB: item_field default should already be set up
        proto = item_field.render_template(self.item_template, parent=field)
        if isinstance(proto, string_types):
            proto = proto.encode("utf-8")
        proto = url_quote(proto)
        return proto

    def serialize(self, field, cstruct, **kw):
        # XXX make it possible to override min_len in kw

        if cstruct in (null, None):
            if self.min_len is not None:
                cstruct = [null] * self.min_len
            else:
                cstruct = []

        cstructlen = len(cstruct)

        if self.min_len is not None and (cstructlen < self.min_len):
            cstruct = list(cstruct) + ([null] * (self.min_len - cstructlen))

        item_field = field.children[0]

        if getattr(field, "sequence_fields", None):
            # this serialization is being performed as a result of a
            # validation failure (``deserialize`` was previously run)
            assert len(cstruct) == len(field.sequence_fields)
            subfields = list(zip(cstruct, field.sequence_fields))
        else:
            # this serialization is being performed as a result of a
            # first-time rendering
            subfields = []
            for val in cstruct:
                cloned = item_field.clone()
                if val is not null:
                    # item field has already been set up with a default by
                    # virtue of its constructor and setting cstruct to null
                    # here wil overwrite the real default
                    cloned.cstruct = val
                subfields.append((cloned.cstruct, cloned))

        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        translate = field.translate
        subitem_title = kw.get("subitem_title", item_field.title)
        subitem_description = kw.get(
            "subitem_description", item_field.description
        )
        add_subitem_text_template = kw.get(
            "add_subitem_text_template", self.add_subitem_text_template
        )
        add_template_mapping = dict(
            subitem_title=translate(subitem_title),
            subitem_description=translate(subitem_description),
            subitem_name=item_field.name,
        )
        if isinstance(add_subitem_text_template, TranslationString):
            add_subitem_text = add_subitem_text_template % add_template_mapping
        else:
            add_subitem_text = _(
                add_subitem_text_template, mapping=add_template_mapping
            )

        kw.setdefault("subfields", subfields)
        kw.setdefault("add_subitem_text", add_subitem_text)
        kw.setdefault("item_field", item_field)

        values = self.get_template_values(field, cstruct, kw)

        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        result = []
        error = None

        if pstruct is null:
            pstruct = []
        elif not isinstance(pstruct, list):
            raise Invalid(field.schema, "Pstruct is not a list")

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

            subfield.cstruct = subval
            result.append(subval)
            field.sequence_fields.append(subfield)

        if error is not None:
            raise error

        return result

    def handle_error(self, field, error):
        if field.error is None:
            field.error = error
        # XXX exponential time
        sequence_fields = getattr(field, "sequence_fields", [])
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

    accept
        The ``accept`` attribute of the input field (default ``None``).
    """

    template = "file_upload"
    readonly_template = "readonly/file_upload"
    accept = None

    requirements = (("fileupload", None),)

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(_FieldStorage(), name="upload", missing=None),
        SchemaNode(_PossiblyEmptyString(), name="uid", missing=None),
    )

    def __init__(self, tmpstore, **kw):
        Widget.__init__(self, **kw)
        self.tmpstore = tmpstore

    def random_id(self):
        return "".join(
            [random.choice(uppercase + string.digits) for i in range(10)]
        )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = {}
        if cstruct:
            uid = cstruct["uid"]
            if uid not in self.tmpstore:
                self.tmpstore[uid] = cstruct

        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        try:
            validated = self._pstruct_schema.deserialize(pstruct)
        except Invalid as exc:
            raise Invalid(field.schema, "Invalid pstruct: %s" % exc)

        upload = validated["upload"]
        uid = validated["uid"]

        if hasattr(upload, "file"):
            # the upload control had a file selected
            data = filedict()
            data["fp"] = upload.file
            filename = upload.filename
            # sanitize IE whole-path filenames
            filename = filename[filename.rfind("\\") + 1 :].strip()
            data["filename"] = filename
            data["mimetype"] = upload.type
            data["size"] = upload.length
            if uid is None:
                # no previous file exists
                while 1:
                    uid = self.random_id()
                    if self.tmpstore.get(uid) is None:
                        data["uid"] = uid
                        self.tmpstore[uid] = data
                        preview_url = self.tmpstore.preview_url(uid)
                        self.tmpstore[uid]["preview_url"] = preview_url
                        break
            else:
                # a previous file exists
                data["uid"] = uid
                self.tmpstore[uid] = data
                preview_url = self.tmpstore.preview_url(uid)
                self.tmpstore[uid]["preview_url"] = preview_url
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

    assume_y2k
        If a year is provided in 2-digit form, assume it means
        2000+year.  Default: ``True``.

    """

    template = "dateparts"
    readonly_template = "readonly/dateparts"
    assume_y2k = True

    _pstruct_schema = SchemaNode(
        Mapping(),
        SchemaNode(_StrippedString(), name="year"),
        SchemaNode(_StrippedString(), name="month"),
        SchemaNode(_StrippedString(), name="day"),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct is null:
            year = ""
            month = ""
            day = ""
        else:
            year, month, day = cstruct.split("-", 2)

        kw.setdefault("year", year)
        kw.setdefault("day", day)
        kw.setdefault("month", month)

        readonly = kw.get("readonly", self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        else:
            try:
                validated = self._pstruct_schema.deserialize(pstruct)
            except Invalid as exc:
                raise Invalid(field.schema, text_("Invalid pstruct: %s" % exc))
            year = validated["year"]
            month = validated["month"]
            day = validated["day"]

            if not year and not month and not day:
                return null

            if self.assume_y2k and len(year) == 2:
                year = "20" + year
            result = "-".join([year, month, day])

            if not year or not month or not day:
                raise Invalid(field.schema, _("Incomplete date"), result)

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

    delimiter
        The csv module delimiter character.
        Default: ``,``.

    quotechar
        The csv module quoting character.
        Default: ``"``.

    quoting
        The csv module quoting dialect.
        Default: ``csv.QUOTE_MINIMAL``.
    """

    template = "textarea"
    readonly_template = "readonly/textarea"
    cols = None
    rows = None
    delimiter = ","
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL

    def serialize(self, field, cstruct, **kw):
        # XXX make cols and rows overrideable
        if cstruct is null:
            cstruct = []
        textrows = getattr(field, "unparseable", None)
        if textrows is None:
            outfile = StringIO()
            writer = csv.writer(
                outfile,
                delimiter=self.delimiter,
                quotechar=self.quotechar,
                quoting=self.quoting,
            )
            writer.writerows(cstruct)
            textrows = outfile.getvalue()
        readonly = kw.get("readonly", self.readonly)
        if readonly:
            template = self.readonly_template
        else:
            template = self.template
        values = self.get_template_values(field, textrows, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if not pstruct.strip():
            return null
        try:
            infile = StringIO(pstruct)
            reader = csv.reader(
                infile,
                delimiter=self.delimiter,
                quotechar=self.quotechar,
                quoting=self.quoting,
            )
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
                msgs.append("line %s: %s" % (e.pos + 1, e))
            field.error = Invalid(field.schema, "\n".join(msgs))


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

    """

    template = "textinput"
    readonly_template = "readonly/textinput"
    mask = None
    mask_placeholder = "_"

    def serialize(self, field, cstruct, **kw):
        # XXX make size and mask overrideable
        if cstruct is null:
            cstruct = ""
        textrow = getattr(field, "unparseable", None)
        if textrow is None:
            outfile = StringIO()
            writer = csv.writer(outfile)
            writer.writerow(cstruct)
            textrow = outfile.getvalue().strip()
        readonly = kw.get("readonly", self.readonly)
        if readonly:
            template = self.readonly_template
        else:
            template = self.template
        values = self.get_template_values(field, textrow, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        elif not isinstance(pstruct, string_types):
            raise Invalid(field.schema, "Pstruct is not a string")
        if not pstruct.strip():
            return null
        try:
            infile = StringIO(pstruct)
            reader = csv.reader(infile)
            # row = reader.next()
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
                msgs.append("%s" % e)
            field.error = Invalid(field.schema, "\n".join(msgs))


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
        ver["js"] = resources

    def set_css_resources(self, requirement, version, *resources):
        """ Set the CSS resources for the requirement/version
        pair, using ``resources`` as the set of relative resource paths."""
        reqt = self.registry.setdefault(requirement, {})
        ver = reqt.setdefault(version, {})
        ver["css"] = resources

    def __call__(self, requirements):
        """ Return a dictionary representing the resources required for a
        particular set of requirements (as returned by
        :meth:`deform.Field.get_widget_requirements`).  The dictionary will be
        a mapping from resource type (``js`` and ``css`` are both keys in the
        dictionary) to a list of asset specifications paths.  Each asset
        specification is a full path to a static resource in the form
        ``package:path``.  You can use the paths for each resource type to
        inject CSS and Javascript on-demand into the head of dynamic pages that
        render Deform forms."""
        result = {"js": [], "css": []}
        for requirement, version in requirements:
            tmp = self.registry.get(requirement)
            if tmp is None:
                raise ValueError(
                    "Cannot resolve widget requirement %r" % requirement
                )
            versioned = tmp.get(version)
            if versioned is None:
                raise ValueError(
                    "Cannot resolve widget requirement %r (version %r)"
                    % ((requirement, version))
                )
            for thing in ("js", "css"):
                sources = versioned.get(thing)
                if sources is None:
                    continue
                if isinstance(sources, string_types):
                    sources = (sources,)
                for source in sources:
                    if source not in result[thing]:
                        result[thing].append(source)

        return result


default_resources = {
    "jquery.form": {None: {"js": "deform:static/scripts/jquery.form-3.09.js"}},
    "jquery.maskedinput": {
        None: {"js": "deform:static/scripts/jquery.maskedinput-1.3.1.min.js"}
    },
    "jquery.maskMoney": {
        None: {"js": "deform:static/scripts/jquery.maskMoney-1.4.1.js"}
    },
    "deform": {
        None: {
            "js": (
                "deform:static/scripts/jquery.form-3.09.js",
                "deform:static/scripts/deform.js",
            )
        }
    },
    "tinymce": {None: {"js": "deform:static/tinymce/tinymce.min.js"}},
    "sortable": {None: {"js": "deform:static/scripts/jquery-sortable.js"}},
    "typeahead": {
        None: {
            "js": "deform:static/scripts/typeahead.min.js",
            "css": "deform:static/css/typeahead.css",
        }
    },
    "modernizr": {
        None: {
            "js": "deform:static/scripts/modernizr.custom.input-types-and-atts.js"  # noQA
        }
    },
    "pickadate": {
        None: {
            "js": (
                "deform:static/pickadate/picker.js",
                "deform:static/pickadate/picker.date.js",
                "deform:static/pickadate/picker.time.js",
                "deform:static/pickadate/legacy.js",
            ),
            "css": (
                "deform:static/pickadate/themes/default.css",
                "deform:static/pickadate/themes/default.date.css",
                "deform:static/pickadate/themes/default.time.css",
            ),
        }
    },
    "select2": {
        None: {
            "js": "deform:static/select2/select2.js",
            "css": "deform:static/select2/select2.css",
        }
    },
    "fileupload": {None: {"js": "deform:static/scripts/file_upload.js"}},
}

default_resource_registry = ResourceRegistry()
