"""Deform exceptions."""


class ValidationFailure(Exception):
    """
    The exception raised by :meth:`deform.widget.Widget.validate`
    (most often called as ``form.validate(fields)``) when the supplied
    field data does not pass the overall constraints of the schema
    associated with the widget.

    **Attributes**

    ``field``
       The field :meth:`deform.form.Field.validate` was
       called on (usually a :class:`deform.form.Form` object).

    ``cstruct``
       The unvalidatable :term:`cstruct` that was returned from
       :meth:`deform.widget.Widget.deserialize`.

    ``error``
       The original :class:`colander.Invalid` exception raised by
       :meth:`deform.schema.SchemaNode.deserialize` which caused
       this exception to need to be raised.
    """

    def __init__(self, field, cstruct, error):
        Exception.__init__(self)
        self.field = field
        self.cstruct = cstruct
        self.error = error

    def render(self, **kw):
        """
        Used to reserialize the form in such a way that the user will
        see error markers in the form HTML.

        The ``**kw`` argument allows a caller to pass named arguments
        that are passed on to the template.
        """
        return self.field.widget.serialize(self.field, self.cstruct, **kw)


class TemplateError(Exception):
    pass
