import colander

from deform import widget
from deform.i18n import _

default_widget_makers = {
    colander.Mapping: widget.MappingWidget,
    colander.Sequence: widget.SequenceWidget,
    colander.String: widget.TextInputWidget,
    colander.Integer: widget.TextInputWidget,
    colander.Float: widget.TextInputWidget,
    colander.Decimal: widget.TextInputWidget,
    colander.Boolean: widget.CheckboxWidget,
    colander.Date: widget.DateInputWidget,
    colander.DateTime: widget.DateTimeInputWidget,
    colander.Tuple: widget.TextInputCSVWidget,
}

class FileData(object):
    """
    A type representing file data; used to shuttle data back and forth
    between an application and the
    :class:`deform.widget.FileUploadWidget` widget.

    This type passes the value obtained during deserialization back to
    the caller unchanged (it will be an instance of
    ``deform.widget.filedict``, which is a plain dictionary subclass;
    it is only a dict subclass so ``isinstance`` may be used against
    it in highly generalized persistence circumstances to detect that
    it is file data).  It serializes from a dictionary containing
    partial file data info into a dictionary containing full file data
    info, serializing the full file data (the widget receives the full
    file data).
    """

    # We cant use FileUploadWidget as the default_widget_maker for
    # this schema node because it requires a tmpstore argument, and
    # a tmpstore cannot be generally defaulted.

    def serialize(self, node, value):
        """
        Serialize a dictionary representing partial file information
        to a dictionary containing information expected by a file
        upload widget.
        
        The file data dictionary passed as ``value`` to this
        ``serialize`` method *must* include:

        filename
            Filename of this file (not a full filesystem path, just the
            filename itself).

        uid
            Unique string id for this file.  Needs to be unique enough to
            disambiguate it from other files that may use the same
            temporary storage mechanism before a successful validation,
            and must be adequate for the calling code to reidentify it
            after deserialization.

        A fully populated dictionary *may* also include the following
        values:

        fp
            File-like object representing this file's content or
            ``None``.  ``None`` indicates this file has already been
            committed to permanent storage.  When serializing a
            'committed' file, the ``fp`` value should ideally not be
            passed or it should be passed as ``None``; ``None`` as an
            ``fp`` value is a signifier to the file upload widget that
            the file data has already been committed.  Using ``None``
            as an ``fp`` value helps prevent unnecessary data copies
            to temporary storage when a form is rendered, however its
            use requires cooperation from the calling code; in
            particular, the calling code must be willing to translate
            a ``None`` ``fp`` value returned from a deserialization
            into the file data via the ``uid`` in the deserialization.

        mimetype
            File content type (e.g. ``application/octet-stream``).

        size
            File content length (integer).

        preview_url
            URL which provides an image preview of this file's data.

        If a ``size`` is not provided, the widget will have no access
        to size display data.  If ``preview_url`` is not provided, the
        widget will not be able to show a file preview.  If
        ``mimetype`` is not provided, the widget will not be able to
        display mimetype information.
        """
        if value is colander.null:
            return colander.null
        
        if not hasattr(value, 'get'):
            mapping = {'value':repr(value)}
            raise colander.Invalid(
                node,
                _('${value} is not a dictionary', mapping=mapping)
                )
        for n in ('filename', 'uid'):
            if not n in value:
                mapping = {'value':repr(value), 'key':n}
                raise colander.Invalid(
                    node,
                    _('${value} has no ${key} key', mapping=mapping)
                    )
        result = widget.filedict()
        result['filename'] = value['filename']
        result['uid'] = value['uid']
        result['mimetype'] = value.get('mimetype')
        result['size'] = value.get('size')
        result['fp'] = value.get('fp')
        result['preview_url'] = value.get('preview_url')
        return result

    def deserialize(self, node, value):
        return value

class Set(object):
    """ A type representing a non-overlapping set of items.
    Deserializes an iterable to a ``set`` object.

    This type constructor accepts one argument:

    ``allow_empty``
       Boolean representing whether an empty set input to
       deserialize will be considered valid.  Default: ``False``.
    """

    widget_maker = widget.CheckboxChoiceWidget

    def __init__(self, allow_empty=False):
        self.allow_empty = allow_empty
        
    def serialize(self, node, value):
        return value

    def deserialize(self, node, value):
        if value is colander.null:
            return colander.null
        if not hasattr(value, '__iter__'):
            raise colander.Invalid(
                node,
                _('${value} is not iterable', mapping={'value':value})
                )
        value =  set(value)
        if not value and not self.allow_empty:
            raise colander.Invalid(node, _('Required'))
        return value
    
        

