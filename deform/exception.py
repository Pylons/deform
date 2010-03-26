import colander

class Invalid(colander.Invalid):
    """ An exception indicating an individual schema node or widget
    deserialization did not succeed.
    """

class ValidationFailure(Exception):
    """
    The exception raised by :meth:`deform.widget.Widget.validate`
    (most often called as ``form.validate(fields)``) when the supplied
    field data does not pass the overall constraints of the schema
    associated with the widget.

    **Attributes**

    ``widget``
       The widget that :meth:`deform.widget.Widget.validate` was
       called on (usually a :class:`deform.widget.Form` object).

    ``cstruct``
       The unvalidatable :term:`cstruct` that was returned from
       :meth:`deform.widget.Widget.deserialize`.

    ``error``
       The :class:`deform.exception.Invalid` exception raised by
       :meth:`deform.schema.SchemaNode.deserialize` which caused this
       exception to need to be raised.

    """
    def __init__(self, widget, cstruct, error):
        Exception.__init__(self)
        self.widget = widget
        self.cstruct = cstruct
        self.error = error

    def serialize(self):
        """
        Used to reserialize the form in such a way that the user will
        see error markers in the form HTML.  This method accepts no
        arguments and returns text representing the HTML of a form
        rendering.
        """
        return self.widget.serialize(self.cstruct)

