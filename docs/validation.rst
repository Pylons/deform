==========
Validation
==========

.. contents:: :local:

Introduction
============

Deform uses Colander for form validation.

See `Schema Node Objects <https://docs.pylonsproject.org/projects/colander/en/latest/basics.html#schema-node-objects>`_ in Colander's documentation for more information.

Colander stock validators
=========================

You can use default Colander validators in Deform forms:

* :py:class:`colander.Email`

* :py:class:`colander.Length`

* :py:class:`colander.Range`

* :py:class:`colander.Any`

* :py:class:`colander.Function`

* :py:class:`colander.OneOf`

* :py:class:`colander.NoneOf`

Example:

.. code-block:: python

    class NewsletterSender(CSRFSchema):
        """Send a news letter."""

        preview = colander.SchemaNode(colander.Boolean())

        # Validate email
        email = colander.SchemaNode(colander.String(), validator=colander.Email(), missing=colander.Drop)


Custom validator functions
==========================

Here is an example of a data-driven validator that validates the form submission against an SQLAlchemy query.

.. code-block:: python

    import colander


    def validate_unique_user_email(node, value, **kwargs):
    """Prevent duplicate usernames."""

        request = node.bindings["request"]
        dbsession = request.dbsession
        User = get_user_class(request.registry)
        if dbsession.query(User).filter_by(email=value).first():
            raise colander.Invalid(node, "Email address already taken")


    class MySchema(CSRFSchema):
        email = colander.SchemaNode(colander.String(), validator=validate_unique_user_email)

Form level validation
=====================

Sometimes you might need to do complex validation where a :py:func:`colander.deferred` pattern complicates things too much. You might just want to do the validation within your view. Here is an example of how to do it.

.. code-block:: python

    class NewsletterSend(CSRFSchema):
        """Send a newsletter."""

        preview = colander.SchemaNode(colander.Boolean(), description="Is this a preview send.", default=True)

        email = colander.SchemaNode(colander.String(), title="Preview email", description="Send preview email to this email address", validator=colander.Email(), missing=colander.null)

        def validator(self, node: "NewsletterSend", appstruct: dict):
            """Custom schema level validation code."""

            # appstruct is Colander appstruct after all other validations have passed
            # Note that this method might not ever be reached
            if appstruct["preview"] and appstruct["email"] == colander.null:
                # This error message appears at the top of the form
                raise colander.Invalid(node["email"], "Please fill in email field if you want to send a preview email.")

Setting errors after validation
===============================

Sometimes you want to react to an error that arises after the form validation happens, for example, when you call a third party API service. You can convert exceptions to form validation errors.

Use ``form.widget.set_error()`` to set a form level error.

.. code-block:: python

    @view_config(context=Admin,
        name="newsletter",
        route_name="admin",
        permission="edit",
        renderer="newsletter/admin.html")
    def newsletter(context: Admin, request: Request):
        """Newsletter admin form."""
        schema = NewsletterSend().bind(request=request)

        # Create a styled button with some extra Bootstrap 3 CSS classes
        b = deform.Button(name='process', title="Send", css_class="btn-block btn-lg")
        form = deform.Form(schema, buttons=(b, ), resource_registry=ResourceRegistry(request))

        rendered_form = None

        # User submitted this form
        if request.method == "POST":
            if 'process' in request.POST:

                try:
                    appstruct = form.validate(request.POST.items())

                    if appstruct["preview"]:
                        send_newsletter(request, appstruct["subject"], preview_email=appstruct["email"])
                        messages.add(request, "Preview email sent.")
                    else:
                        send_newsletter(request, appstruct["subject"])
                        messages.add(request, "Newsletter sent.")

                    return httpexceptions.HTTPFound(request.url)

                except MailgunError as e:
                    # API call failed
                    # Do a form level error message
                    exc = colander.Invalid(form.widget, "Could not sent newsletter:" + str(e))
                    form.widget.handle_error(form, exc)

                except deform.ValidationFailure as e:
                    # Render a form version where errors are visible next to the fields,
                    # and the submitted values are posted back
                    rendered_form = e.render()
            else:
                # We don't know which control caused form submission
                return httpexceptions.HTTPBadRequest("Unknown form button pressed")

        # Render initial form
        # Default values for read only fields
        if rendered_form is None:
            rendered_form = form.render({
                "api_key": api_key,
                "domain": domain,
                "mailing_list": mailing_list,
            })

        # This loads widgets specific CSS/JavaScript in HTML code,
        # if form widgets specify any static assets.
        form.resource_registry.pull_in_resources(request, form)

        return locals()
