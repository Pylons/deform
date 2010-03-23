
class FormValidationError(Exception):
    """
    The exception raised by :meth:`deform.widget.Widget.validate` when
    the supplied field data does not pass the constraints of the
    schema.
    """
    def __init__(self, form, cstruct, e):
        Exception.__init__(self)
        self.form = form
        self.cstruct = cstruct
        self.invalid_exc = e

    def serialize(self):
        """
        The ``serialize`` method of a
        :exc:`deform.exception.FormValidationError` exception can be
        used to reserialize the form in such a way that the user will
        see error markers in the form HTML.  It accepts no arguments
        and returns text representing the HTML of a form rendering.
        """
        return self.form.serialize(self.cstruct)

