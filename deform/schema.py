import colander

from deform import widget

# data types

class Mapping(colander.Mapping):
    default_widget_maker = widget.MappingWidget

class Sequence(colander.Sequence):
    default_widget_maker = widget.SequenceWidget

class String(colander.String):
    default_widget_maker = widget.TextInputWidget

class Integer(colander.Integer):
    default_widget_maker = widget.TextInputWidget

class Float(colander.Integer):
    default_widget_maker = widget.TextInputWidget

class Boolean(colander.Boolean):
    default_widget_maker = widget.CheckboxWidget

class FileData(object):
    """
    A type representing file data; used to shuttle data back and forth
    between an application and a file upload widget
    (e.g. the :class:`deform.widget.FileUploadWidget` widget).

    This type passes the value obtained during deserialization back to
    the caller unchanged.  It serializes from a dictionary containing
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
        if not hasattr(value, 'get'):
            raise colander.Invalid(node, '%s is not a dictionary' % repr(value))
        for n in ('filename', 'uid'):
            if not n in value:
                raise colander.Invalid(node,
                                       '%s has no %s key' % (repr(value), n))
        result = {}
        result['filename'] = value['filename']
        result['uid'] = value['uid']
        result['mimetype'] = value.get('mimetype')
        result['size'] = value.get('size')
        result['fp'] = value.get('fp')
        result['preview_url'] = value.get('preview_url')
        return result

    def deserialize(self, node, value):
        if not value and node.required:
            raise colander.Invalid(node, 'Required')
        return value

# schema nodes

class SchemaNode(colander.SchemaNode):
    pass

class MappingSchema(colander.MappingSchema):
    schema_type = Mapping
    node_type = SchemaNode

Schema = MappingSchema

class SequenceSchema(colander.SequenceSchema):
    schema_type = Sequence
    node_type = SchemaNode
    

    
