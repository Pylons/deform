import itertools
import colander
import peppercorn

from deform import decorator
from deform import exception
from deform import template
from deform import widget
from deform import schema

from deform.compat import (
    next,
)

class Field(object):
    """ Represents an individual form field (a visible object in a
    form rendering).

    A :class:`deform.form.Field` object instance is meant to last for
    the duration of a single web request. As a result, a field object
    is often used as a scratchpad by the widget associated with that
    field.  Using a field as a scratchpad makes it possible to build
    implementations of state-retaining widgets while instances of
    those widget still only need to be constructed once instead of on
    each request.
    
    *Attributes*

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
            ``deformField0``.

        name
            An alias for self.schema.name
        
        title
            An alias for self.schema.title

        description
            An alias for self.schema.description

        required
            An alias for self.schema.required

        typ
            An alias for self.schema.typ

        children
            Child fields of this field.

        error
            The exception raised by the last attempted validation of the
            schema element associated with this field.  By default, this
            attribute is ``None``.  If non-None, this attribute is usually
            an instance of the exception class
            :exc:`colander.Invalid`, which has a ``msg`` attribute
            providing a human-readable validation error message.

        errormsg
            The ``msg`` attribute of the ``error`` attached to this field
            or ``None`` if the ``error`` attached to this field is ``None``.

        renderer
            The template :term:`renderer` associated with the form.  If a
            renderer is not passed to the constructor, the default deform
            renderer will be used (the :term:`default renderer`).

        counter
            ``None`` or an instance of ``itertools.counter`` which is used
            to generate sequential order-related attributes such as
            ``oid`` and ``order``.

        resource_registry
            The :term:`resource registry` associated with this field.

    *Constructor Arguments*

      ``renderer``, ``counter`` and ``resource_registry`` are accepted
      as explicit keyword arguments to the :class:`deform.Field`.
      These are also available as attribute values.  ``renderer``, if
      passed, is a template renderer as described in
      :ref:`creating_a_renderer`.  ``counter``, if passed, should be
      an :attr:`itertools.counter` object (useful when rendering
      multiple forms on the same page, see
      `http://deformdemo.repoze.org/multiple_forms/
      <http://deformdemo.repoze.org/multiple_forms/>`_.
      ``resource_registry``, if passed should be a widget resource
      registry (see also :ref:`get_widget_resources`).

      If any of these values is ``None`` (their default), suitable
      default values are used in their place.

      The :class:`deform.Field` constructor also accepts *arbitrary*
      keyword arguments.  When an 'unknown' keyword argument is
      passed, it is attached unmolested to the form field as an
      attribute.

      All keyword arguments (explicit and unknown) are also attached to
      all *children* nodes of the field being constructed.

    """

    error = None
    default_renderer = template.default_renderer
    default_resource_registry = widget.default_resource_registry

    def __init__(self, schema, renderer=None, counter=None,
                 resource_registry=None, **kw):
        self.counter = counter or itertools.count()
        self.order = next(self.counter)
        self.oid = 'deformField%s' % self.order
        self.schema = schema
        self.typ = self.schema.typ # required by Invalid exception
        if renderer is None:
            renderer = self.default_renderer
        if resource_registry is None:
            resource_registry = self.default_resource_registry
        self.renderer = renderer
        self.resource_registry = resource_registry
        self.name = schema.name
        self.title = schema.title
        self.description = schema.description
        self.required = schema.required
        self.children = []
        self.__dict__.update(kw)
        for child in schema.children:
            self.children.append(Field(child,
                                       renderer=renderer,
                                       counter=self.counter,
                                       resource_registry=resource_registry,
                                       **kw))

    def __iter__(self):
        """ Iterate over the children fields of this field. """
        return iter(self.children)

    @classmethod
    def set_zpt_renderer(cls, search_path, auto_reload=True,
                         debug=True, encoding='utf-8',
                         translator=None):
        """ Create a :term:`Chameleon` ZPT renderer that will act as a
        :term:`default renderer` for instances of the associated class
        when no ``renderer`` argument is provided to the class'
        constructor.  The arguments to this classmethod have the same
        meaning as the arguments provided to a
        :class:`deform.ZPTRendererFactory`.

        Calling this method resets the :term:`default renderer`.

        This method is effectively a shortcut for
        ``cls.set_default_renderer(ZPTRendererFactory(...))``."""
        cls.default_renderer = template.ZPTRendererFactory(
            search_path,
            auto_reload=auto_reload,
            debug=debug,
            encoding=encoding,
            translator=translator,
            )

    def translate(self, msgid):
        """ Use the translator passed to the renderer of this field to
        translate the msgid into a term.  If the renderer does not have a
        translator, this method will return the msgid."""
        translate = getattr(self.renderer, 'translate', None)
        if translate is not None:
            return translate(msgid)
        return msgid

    @classmethod
    def set_default_renderer(cls, renderer):
        """ Set the callable that will act as a default renderer for
        instances of the associated class when no ``renderer``
        argument is provided to the class' constructor.  Useful when
        you'd like to use an alternate templating system.

        Calling this method resets the :term:`default renderer`.
        """
        cls.default_renderer = staticmethod(renderer)

    @classmethod
    def set_default_resource_registry(cls, registry):

        """ Set the callable that will act as a default
        :term:`resource registry` for instances of the associated
        class when no ``resource_registry`` argument is provided to
        the class' constructor.  Useful when you'd like to use
        non-default requirement to resource path mappings for the
        entirety of a process.

        Calling this method resets the default :term:`resource registry`.
        """
        cls.default_resource_registry = registry

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
        cloned.order = next(cloned.counter)
        cloned.oid = 'deformField%s' % cloned.order
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
        wdg = getattr(self.schema, 'widget', None)
        if wdg is not None:
            return wdg
        widget_maker = getattr(self.schema.typ, 'widget_maker', None)
        if widget_maker is None:
            widget_maker = schema.default_widget_makers.get(
                self.schema.typ.__class__)
            if widget_maker is None:
                for (cls, wgt) in schema.default_widget_makers.items():
                    if isinstance(self.schema.typ, cls):
                        widget_maker = wgt
                        break
        if widget_maker is None:
            widget_maker = widget.TextInputWidget
        return widget_maker()

    def get_widget_requirements(self):
        """ Return a sequence of two tuples in the form
        [(``requirement_name``, ``version``), ..].

        The first element in each two-tuple represents a requirement
        name.  When a requirement name is returned as part of
        ``get_widget_requirements``, it means that one or more CSS or
        Javascript resources need to be loaded by the page performing
        the form rendering in order for some widget on the page to
        function properly.
        
        The second element in each two-tuple is the reqested version
        of the library resource.  It may be ``None``, in which case
        the version is unspecified.

        See also the ``requirements`` attribute of
        :class:`deform.Widget` and the explanation of widget
        requirements in :ref:`get_widget_requirements`.
        """
        L = []
        requirements = self.widget.requirements
        if requirements:
            for requirement in requirements:
                reqt = tuple(requirement)
                if not reqt in L:
                    L.append(reqt)
        for child in self.children:
            for requirement in child.get_widget_requirements():
                reqt = tuple(requirement)
                if not reqt in L:
                    L.append(reqt)
        return L

    def get_widget_resources(self, requirements=None):
        """ Return a resources dictionary in the form ``{'js':[seq],
        'css':[seq]}``.  ``js`` represents Javascript resources,
        ``css`` represents CSS resources.  ``seq`` represents a
        sequence of resource paths.  Each path in ``seq`` represents a
        relative resource name, as defined by the mapping of a
        requirement to a set of resource specification by the
        :term:`resource registry` attached to this field or form.

        This method may raise a :exc:`ValueError` if the resource
        registry associated with this field or form cannot resolve a
        requirement to a set of resource paths.

        The ``requirements`` argument represents a set of requirements
        as returned by a manual call to
        :meth:`deform.Field.get_widget_requirements`.  If
        ``requirements`` is not supplied, the requirement are implied
        by calling the :meth:`deform.Field.get_widget_requirements`
        method against this form field.

        See also :ref:`get_widget_resources`.
        """
        if requirements is None:
            requirements = self.get_widget_requirements()
        return self.resource_registry(requirements)

    def set_widgets(self, values, separator='.'):
        """ set widgets of the child fields of this field
        or form element.  ``widgets`` should be a dictionary in the
        form::

           {'dotted.field.name':Widget(),
            'dotted.field.name2':Widget()}

        The keys of the dictionary are dotted names.  Each dotted name
        refers to a single field in the tree of fields that are
        children of the field or form object upon which this method is
        called.

        The dotted name is split on its dots and the resulting list of
        names is used as a search path into the child fields of this
        field in order to find a field to which to assign the
        associated widget.

        Two special cases exist:

        - If the key is the empty string (``''``), the widget is
          assigned to the field upon which this method is called.

        - If the key contains an asterisk as an element name, the
          first child of the found element is traversed.  This is most
          useful for sequence fields, because the first (and only)
          child of sequence fields is always the prototype field which
          is used to render all fields in the sequence within a form
          rendering.

        If the ``separator`` argument is passed, it is should be a
        string to be used as the dot character when splitting the
        dotted names (useful for supplying if one of your field object
        has a dot in its name, and you need to use a different
        separator).

        Examples follow.  If the following form is used::

          class Person(Schema):
              first_name = SchemaNode(String())
              last_name = SchemaNode(String())

          class People(SequenceSchema):
              person = Person()

          class Conference(Schema):
              people = People()
              name = SchemaNode(String())

          schema = Conference()
          form = Form(schema)

        The following invocations will have the following results
        against the schema defined above:

        ``form.set_widgets({'people.person.first_name':TextAreaWidget()})``

          Set the ``first_name`` field's widget to a ``TextAreaWidget``.

        ``form.set_widgets({'people.*.first_name':TextAreaWidget()})``

          Set the ``first_name`` field's widget to a
          ``TextAreaWidget``.
        
        ``form.set_widgets({'people':MySequenceWidget()})``

          Set the ``people`` sequence field's widget to a
          ``MySequenceWidget``.

        ``form.set_widgets({'people.*':MySequenceWidget()})``

          Set the *person* field's widget to a ``MySequenceWidget``.

        ``form.set_widgets({'':MyMappingWidget()})``

          Set *form* node's widget to a ``MyMappingWidget``.

        """
        for k, v in values.items():
            if not k:
                self.widget = v
            else:
                path = k.split(separator)
                field = self
                while path:
                    element = path.pop(0)
                    if element == '*':
                        field = field.children[0]
                    else:
                        field = field[element]
                field.widget = v
                
    @property
    def errormsg(self):
        """ Return the ``msg`` attribute of the ``error`` attached to
        this field.  If the ``error`` attribute is ``None``,
        the return value will be ``None``."""
        return getattr(self.error, 'msg', None)

    def serialize(self, cstruct, readonly=False):
        """ Serialize the cstruct into HTML.  If ``readonly`` is
        ``True``, render a read-only rendering (no input fields)."""
        return self.widget.serialize(self, cstruct=cstruct, readonly=readonly)

    def deserialize(self, pstruct):
        """ Deserialize the pstruct into a cstruct."""
        return self.widget.deserialize(self, pstruct)

    def render(self, appstruct=colander.null, readonly=False):
        """ Render the field (or form) to HTML using ``appstruct`` as
        a set of default values.  ``appstruct`` is typically a
        dictionary of application values matching the schema used by
        this form, or ``None``.

        Calling this method is the same as calling::

           cstruct = form.schema.serialize(appstruct)
           form.widget.serialize(field, cstruct)

        The ``readonly`` argument causes the rendering to be entirely
        read-only (no input elements at all).

        See the documentation for
        :meth:`colander.SchemaNode.serialize` and
        :meth:`deform.widget.Widget.serialize` .
        """
        cstruct = self.schema.serialize(appstruct)
        return self.serialize(cstruct, readonly=readonly)

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
          :exc:`deform.exception.ValidationFailure` exception is raised.

        The typical usage of ``validate`` in the wild is often
        something like this (at least in terms of code found within
        the body of a :mod:`pyramid` view function, the particulars
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
        exc = None

        try:
            cstruct = self.deserialize(pstruct)
        except colander.Invalid as e:
            # fill in errors raised by widgets
            self.widget.handle_error(self, e)
            cstruct = e.value
            exc = e

        try:
            appstruct = self.schema.deserialize(cstruct)
        except colander.Invalid as e:
            # fill in errors raised by schema nodes
            self.widget.handle_error(self, e)
            exc = e

        if exc:
            raise exception.ValidationFailure(self, cstruct, exc)

        return appstruct

    def __repr__(self):
        return '<%s.%s object at %d (schemanode %r)>' % (
            self.__module__,
            self.__class__.__name__,
            id(self),
            self.schema.name,
            )
