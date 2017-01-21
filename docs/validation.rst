==========
Validation
==========

.. contents:: local

Introduction
============

Deform uses Colander form validation.

`More information in Colander documentation <http://docs.pylonsproject.org/projects/colander/en/latest/basics.html#schema-node-objects>`_

Colandar stock validators
=========================

You can use default Colandar validators in Deform forms:

* :py:class:`colandar.Email`

* :py:class:`colandar.Length`

* :py:class:`colandar.Range`

* :py:class:`colandar.Any`

* :py:class:`colandar.Function`

* :py:class:`colandar.OneOf`

* :py:class:`colandar.NoneOf`

Example:

.. code-block:: python

    class NewsletterSender(CSRFSchema):
        """Send a news letter."""

        preview = colander.SchemaNode(colander.Boolean())

        # Validate emaik
        email = colander.SchemaNode(colander.String(), validator=colander.Email(), missing=colander.Drop)


Custom validator functions
==========================

Here is an example for data-driven validator, that validates the form submission against SQLAlchemy query.

.. code-block:: python

    import colander


    def validate_unique_user_email(node, value, **kwargs):
    """Make sure we cannot enter the same username twice."""

        request = node.bindings["request"]
        dbsession = request.dbsession
        User = get_user_class(request.registry)
        if dbsession.query(User).filter_by(email=value).first():
            raise colander.Invalid(node, "Email address already taken")


    class MySchema(CSRFSchema):
        email = colander.SchemaNode(colander.String(), validator=validate_unique_user_email)

Form level validation
=====================

Sometimes you might need to do complex validation where :py:func:`colander.deferred` pattern complicates thing too much. You might just want to do the validation within your view. Here is an example how to do it:

.. code-block:: python

    class NewsletterSend(CSRFSchema):

        preview = colander.SchemaNode(colander.Boolean(), description="Is this a preview send.", default=True)

        email = colander.SchemaNode(colander.String(), title="Preview email", description="Send preview email to this email address", validator=colander.Email)

        def deserialize(self, cstruct: dict):
            """Override form deserialization to add custom validation steps.

            :param cstruct: Colander unvalidated structure of incoming data
            """

            if cstruct["preview"] and cstruct["email"] == colander.null:
                # The messag will appear at the top of the form
                raise colander.Invalid(self, "Please fill in email field if you want to send a preview email.")

            return super(NewsletterSend, self).deserialize()
