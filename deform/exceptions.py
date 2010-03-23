
class FormValidationError(Exception):
    def __init__(self, form, cstruct, e):
        Exception.__init__(self)
        self.form = form
        self.cstruct = cstruct
        self.invalid_exc = e

    def serialize(self):
        return self.form.serialize(self.cstruct)

