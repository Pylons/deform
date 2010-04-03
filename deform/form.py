import itertools
import colander
import peppercorn

from deform import decorator
from deform import exception
from deform import template
from deform import widget

class Field(object):
    """ Represents an individual form field (a visible object in a
    form rendering).

    A :class:`deform.form.Field` object instance is meant to last for
    the duration of a single web request. A field may be used as a
    scratchpad by the widget associated with the field.  Using a field
    as a scratchpad makes it possible to build implementations of
    state-retaining widgets while instances of those widget still only
    need to be constructed once instead of on each request.
    
    All field objects have the following attributes:

    schema
        The schema node associated with this field.

    widget
        The widget associated with this field.

    order
        An integer indicating the relative order of this field's
        construction to its children and parents.

    oid
        A string incorporating the ``order`` attribute that can be
        used as a unique identifier in HTML code (often for ``id``
        attributes of field-related elements).  An example oid is
        ``deform_field0``.

    name
        An alias for self.schema.name
    
    title
        An alias for self.schema.title

    description
        An alias for self.schema.description

    required
        An alias for self.schema.required

    default
        An alias for self.schema.sdefault

    typ
        An alias for self.schema.typ

    children
        Child fields of this field.

    error
        The exception raised by the last attempted validation of the
        schema element associated with this field.  By default, this
        attribute is ``None``.  If non-None, this attribute is usually
        an instance of the exception class
        :exc:`deform.exception.Invalid`, which has a ``msg`` attribute
        providing a human-readable validation error message.

    errormsg
        The ``msg`` attribute of the ``error`` attached to this field
        or ``None`` if the ``error`` attached to this field is ``None``.

    renderer
        The template :term:`renderer` associated with the form.  If a
        renderer is not passed to the constructor, the default deform
        renderer will be used (only templates from
        ``deform/templates/`` will be used).
    """

    error = None

    def __init__(self, schema, renderer=None, counter=None):
        self.counter = counter or itertools.count()
        self.order = self.counter.next()
        self.oid = 'deform_field%s' % self.order
        self.schema = schema
        self.typ = self.schema.typ # required by Invalid exception
        self.renderer = renderer or template.default_renderer
        self.name = schema.name
        self.title = schema.title
        self.description = schema.description
        self.required = schema.required
        self.children = []
        for child in schema.children:
            self.children.append(Field(child,renderer=renderer,
                                       counter=self.counter))

    def __getitem__(self, name):
        """ Return the subfield of this field named ``name`` or raise
        a :exc:`KeyError` if a subfield does not exist named ``name``."""
        for child in self.children:
            if child.name == name:
                return child
        raise KeyError(name)

    def clone(self):
        """ Clone the field and its subfields, retaining attribute
        information.  Return the cloned field.  The ``order``
        attribute of the node is not cloned; instead the field
        receives a new order attribute; it will be a number larger
        than the last renderered field of this set."""
        cloned = self.__class__(self.schema)
        cloned.__dict__.update(self.__dict__)
        cloned.order = cloned.counter.next()
        cloned.oid = 'field%s' % cloned.order
        cloned.children = [ field.clone() for field in self.children ]
        return cloned

    @decorator.reify
    def widget(self):
        """ If a widget is not assigned directly to a field, this
        function will be called to generate a default widget (only
        once). The result of this function will then be assigned as
        the ``widget`` attribute of the field for the rest of the
        lifetime of this field. If a widget is assigned to a field
        before form processing, this function will not be called."""
        widget_maker = getattr(self.schema.typ, 'default_widget_maker', None)
        if widget_maker is None:
            widget_maker = widget.TextInputWidget
        return widget_maker()

    @decorator.reify
    def default(self):
        """ The serialized schema default """
        return self.schema.sdefault

    @property
    def errormsg(self):
        """ Return the ``msg`` attribute of the ``error`` attached to
        this field.  If the ``error`` attribute is ``None``,
        the return value will be ``None``."""
        return getattr(self.error, 'msg', None)

    def render(self, appstruct=None):
        """ Render the field (or form) to HTML using ``appstruct`` as
        a set of default values.  ``appstruct`` is typically a
        dictionary of application values matching the schema used by
        this form, or ``None``.

        Calling this method is the same as calling::

           cstruct = form.schema.serialize(appstruct)
           form.widget.serialize(field, cstruct)

        See the documentation for
        :meth:`deform.schema.SchemaNode.serialize` and
        :meth:`deform.widget.Widget.serialize` .
        """
        if appstruct is None:
            appstruct = {}
        cstruct = self.schema.serialize(appstruct)
        return self.widget.serialize(self, cstruct)

    def validate(self, controls):
        """
        Validate the set of controls returned by a form submission
        against the schema associated with this field or form.
        ``controls`` should be a *document-ordered* sequence of
        two-tuples that represent the form submission data.  Each
        two-tuple should be in the form ``(key, value)``.  ``node``
        should be the schema node associated with this widget.

        For example, using WebOb, you can compute a suitable value for
        ``controls`` via::

          request.POST.items()

        Or, if you're using a ``cgi.FieldStorage`` object named
        ``fs``, you can compute a suitable value for ``controls``
        via::

          controls = []
          if fs.list:
              for control in fs.list:
                  if control.filename:
                      controls.append((control.name, control))
                  else:
                      controls.append((control.name, control.value))

        Equivalent ways of computing ``controls`` should be available to
        any web framework.

        When the ``validate`` method is called:

        - if the fields are successfully validated, a data structure
          represented by the deserialization of the data as per the
          schema is returned.  It will be a mapping.

        - If the fields cannot be successfully validated, a
          :exc:`deform.Invalid` exception is raised.

        The typical usage of ``validate`` in the wild is often
        something like this (at least in terms of code found within
        the body of a :mod:`repoze.bfg` view function, the particulars
        will differ in your web framework)::

          from webob.exc import HTTPFound
          from deform.exception import ValidationFailure
          from deform import schema
          from deform.form import Form

          from my_application import do_something

          class MySchema(schema.MappingSchema):
              color = schema.SchemaNode(schema.String())

          schema = MySchema()
          form = Form(schema)
          
          if 'submit' in request.POST:  # the form submission needs validation
              controls = request.POST.items()
              try:
                  deserialized = form.validate(controls)
                  do_something(deserialized)
                  return HTTPFound(location='http://example.com/success')
              except ValidationFailure, e:
                  return {'form':e.render()}
          else:
              return {'form':form.render()} # the form just needs rendering
        """
        pstruct = peppercorn.parse(controls)
        cstruct = self.widget.deserialize(self, pstruct)
        try:
            return self.schema.deserialize(cstruct)
        except colander.Invalid, e:
            self.widget.handle_error(self, e)
            raise exception.ValidationFailure(self, cstruct, e)


class Form(Field):
    """
    Field representing an entire form.

    Arguments:

    schema
        A :class:`deform.schema.SchemaNode` object representing a
        schema to be rendered.  Required.

    action
        The form action (inserted into the ``action`` attribute of
        the form's form tag when rendered).  Default ``.`` (single
        dot).

    method
        The form method (inserted into the ``method`` attribute of
        the form's form tag when rendered).  Default: ``POST``.

    buttons
        A sequence of strings or :class:`deform.widget.Button`
        objects representing submit buttons that will be placed at
        the bottom of the form.  If any string is passed in the
        sequence, it is converted to
        :class:`deform.widget.Button` objects.

    """
    def __init__(self, schema, renderer=None, action='.', method='POST',
                 buttons=()):
        Field.__init__(self, schema, renderer=renderer)
        _buttons = []
        for button in buttons:
            if isinstance(button, basestring):
                button = Button(button)
            _buttons.append(button)
        self.action = action
        self.method = method
        self.buttons = _buttons
        self.widget = widget.FormWidget()

class Button(object):
    """
    A class representing a form submit button.  A sequence of
    :class:`deform.widget.Button` objects may be passed to the
    constructor of a :class:`deform.form.Form` class when it is
    created to represent the buttons renderered at the bottom of the
    form.

    Arguments:

    name
        The string or unicode value used as the ``name`` of the button
        when rendered (the ``name`` attribute of the button or input
        tag resulting from a form rendering).  Default: ``submit``.

    title
        The value used as the title of the button when rendered (shows
        up in the button inner text).  Default: capitalization of
        whatever is passed as ``name``.  E.g. if ``name`` is passed as
        ``submit``, ``title`` will be ``Submit``.

    value
        The value used as the value of the button when rendered (the
        ``value`` attribute of the button or input tag resulting from
        a form rendering).  Default: same as ``name`` passed.
    """
    def __init__(self, name='submit', title=None, value=None):
        if title is None:
            title = name.capitalize()
        if value is None:
            value = name
        self.name = name
        self.title = title
        self.value = value

