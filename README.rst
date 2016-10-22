Deform
======

.. image:: https://travis-ci.org/Pylons/deform.png?branch=master
        :target: https://travis-ci.org/Pylons/deform

.. image:: https://readthedocs.org/projects/deform/badge/?version=master
        :target: http://docs.pylonsproject.org/projects/deform/en/master/
        :alt: Master Documentation Status

.. image:: https://readthedocs.org/projects/deform/badge/?version=latest
        :target: http://docs.pylonsproject.org/projects/deform/en/latest/
        :alt: Latest Documentation Status

.. contents:: :local:

Introduction
============

Deform is a Python HTML form library independent of underlying web framework. Deform is ideal for complex server-side generated forms with JavaScript integration. More complex examples include nested forms where one can dynamically add and remove subform items. Date and time picking widgets and other rich widgets are supported out of the box.

Deform comes with `Chameleon templates <https://chameleon.readthedocs.io/en/latest/>`_ for `Bootstrap <http://getbootstrap.com>`_ based widgets. It uses `Colander <https://github.com/Pylons/colander>`_ as for form schema and validation definitions. Deform integrates well with `Pyramid web framework <https://trypyramid.com/>`_  and several other web frameworks. Peppercorn library is used to convert flat HTML name value mapping form submissions to stream of name value mappings submissions, allowing building complex and nested form structure.

Even if Deform uses Chameleon templates internally, you can embed rendered Deform forms into any template language.

Example
-------

* `See all widget examples <http://deformdemo.repoze.org>`_. Below is a sample form loop using `Pyramid <http://trypyramid.com/>`_ web framework.

.. image:: https://github.com/Pylons/deform/raw/master/docs/example.png
    :width: 400px

Example code::

    """Self-contained Deform demo example."""
    from __future__ import print_function

    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig
    from pyramid.httpexceptions import HTTPFound

    import colander
    import deform


    class ExampleSchema(deform.schema.CSRFSchema):

        name = colander.SchemaNode(
            colander.String(),
            title="Name")

        age = colander.SchemaNode(
            colander.Int(),
            default=18,
            title="Age",
            help_text="Your age in years")


    def mini_example(request):
        """Sample Deform form with validation."""

        schema = ExampleSchema().bind(request=request)

        # Create a styled button with some extra Bootstrap 3 CSS classes
        process_btn = deform.form.Button(name='process', title="Process")
        form = deform.form.Form(schema, buttons=(process_btn,))

        # User submitted this form
        if request.method == "POST":
            if 'process' in request.POST:

                try:
                    appstruct = form.validate(request.POST.items())

                    # Save form data from appstruct
                    print("Your name:", appstruct["name"])
                    print("Your age:", appstruct["age"])

                    # Thank user and take him/her to the next page
                    request.session.flash('Thank you for the submission.')

                    # Redirect to the page shows after succesful form submission
                    return HTTPFound("/")

                except deform.exception.ValidationFailure as e:
                    # Render a form version where errors are visible next to the fields,
                    # and the submitted values are posted back
                    rendered_form = e.render()
        else:
            # Render a form with initial default values
            rendered_form = form.render()

        return {
            "rendered_form": rendered_form,
        }


    def main(global_config, **settings):
        """pserve entry point"""
        session_factory = UnencryptedCookieSessionFactoryConfig('seekrit!')
        config = Configurator(settings=settings, session_factory=session_factory)
        config.include('pyramid_chameleon')
        deform.renderer.configure_zpt_renderer()
        config.add_static_view('static_deform', 'deform:static')
        config.add_route('mini_example', path='/')
        config.add_view(mini_example, route_name="mini_example", renderer="templates/mini.pt")
        return config.make_wsgi_app()


Status
------

This library is actively developed and maintained.

Community and links
-------------------

* `Widget examples <http://deformdemo.repoze.org>`_

* `Issue tracker <http://github.com/Pylons/deform>`_

* `Demo project <https://github.com/Pylons/deformdemo/>`_

* `Documentation <http://docs.pylonsproject.org/projects/deform/en/latest/>`_

* `Chat and mailing list <http://docs.pylonsproject.org/projects/pyramid/en/latest/#support-and-development>`_



