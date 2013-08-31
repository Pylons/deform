import itertools
import colander
import peppercorn
import unicodedata
import re

from chameleon.utils import Markup

from . import (
    decorator,
    exception,
    template,
    widget,
    schema,
    compat,
    )

class _Marker(object):
    def __repr__(self): # pragma: no cover
        return '(Default)'

    __str__ = __repr__

_marker = _Marker()

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
            The widget associated with this field. When no widget is
            defined in the schema node, a default widget will be created.
            The default widget will have a generated item_css_class
            containing the normalized version of the ``name`` attribute
            (with ``item`` prepended, e.g. ``item-username``).

        order
            An integer indicating the relative order of this field's
            construction to its children and parents.

        oid
            A string incorporating the ``order`` attribute that can be
            used as a unique identifier in HTML code (often for ``id``
            attributes of field-related elements).  A default oid is
            generated that looks like this: ``deformField0``.  A
            custom oid can provided, but if the field is cloned,
            the clones will get unique default oids.

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

      ``renderer``, ``counter``, ``resource_registry`` and ``appstruct`` are
      accepted as explicit keyword arguments to the :class:`deform.Field`.
      These are also available as attribute values.  ``renderer``, if passed,
      is a template renderer as described in :ref:`creating_a_renderer`.
      ``counter``, if passed, should be an :attr:`itertools.counter` object
      (useful when rendering multiple forms on the same page, see
      `http://deformdemo.repoze.org/multiple_forms/
      <http://deformdemo.repoze.org/multiple_forms/>`_.
      ``resource_registry``, if passed should be a widget resource registry
      (see also :ref:`get_widget_resources`).

      If any of these values is not passed, a suitable default values is used
      in its place.

      The ``appstruct`` constructor argument is used to prepopulate field
      values related to this form's schema.  If an appstruct is not supplied,
      the form's fields will be rendered with default values unless an
      appstruct is supplied to the ``render`` method explicitly.

      The :class:`deform.Field` constructor also accepts *arbitrary*
      keyword arguments.  When an 'unknown' keyword argument is
      passed, it is attached unmolested to the form field as an
      attribute.

      All keyword arguments (explicit and unknown) are also attached to
      all *children* nodes of the field being constructed.

    """

    error = None
    _cstruct = colander.null
    default_renderer = template.default_renderer
    default_resource_registry = widget.default_resource_registry

    def __init__(self, schema, renderer=None, counter=None,
                 resource_registry=None, appstruct=colander.null,
                 **kw):
        self.counter = counter or itertools.count()
        self.order = next(self.counter)
        self.oid = getattr(schema, 'oid', 'deformField%s' % self.order)
        self.schema = schema
        self.typ = schema.typ # required by Invalid exception
        self.name = schema.name
        self.title = schema.title
        self.description = schema.description
        self.required = schema.required
        if renderer is None:
            renderer = self.default_renderer
        if resource_registry is None:
            resource_registry = self.default_resource_registry
        self.renderer = renderer
        self.resource_registry = resource_registry
        self.children = []
        self.__dict__.update(kw)
        for child in schema.children:
            self.children.append(
                Field(
                    child,
                    renderer=renderer,
                    counter=self.counter,
                    resource_registry=resource_registry,
                    **kw
                    )
                )
        self.set_appstruct(appstruct)

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

    def translate(self, msgid):
        """ Use the translator passed to the renderer of this field to
        translate the msgid into a term and return the term.  If the renderer
        does not have a translator, this method will return the msgid."""
        translate = getattr(self.renderer, 'translate', None)
        if translate is not None:
            return translate(msgid)
        return msgid

    def __iter__(self):
        """ Iterate over the children fields of this field. """
        return iter(self.children)

    def __getitem__(self, name):
        """ Return the subfield of this field named ``name`` or raise
        a :exc:`KeyError` if a subfield does not exist named ``name``."""
        for child in self.children:
            if child.name == name:
                return child
        raise KeyError(name)

    def __contains__(self, name):
        for child in self.children:
            if child.name == name:
                return True
        return False

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
        return widget_maker(item_css_class=self._default_item_css_class())

    def _default_item_css_class(self):
        if not self.name:
            return None
        
        css_class = unicodedata.normalize('NFKD', compat.text_type(self.name)).encode('ascii', 'ignore').decode('ascii')
        css_class = re.sub('[^\w\s-]', '', css_class).strip().lower()
        css_class = re.sub('[-\s]+', '-', css_class)
        return "item-%s" % css_class


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

    def serialize(self, cstruct=_marker, **kw):
        """ Serialize the cstruct into HTML and return the HTML string.  This
        function just turns around and calls ``self.widget.serialize(**kw)``;
        therefore the field widget's ``serialize`` method should be expecting
        any values sent in ``kw``.  If ``cstruct`` is not passed, the cstruct
        attached to this node will be injected into ``kw`` as ``cstruct``.
        If ``field`` is not passed in ``kw``, this field will be injected
        into ``kw`` as ``field``.

        .. note::

           Deform versions before 0.9.8 only accepted a ``readonly``
           keyword argument to this function.  Version 0.9.8 and later accept
           arbitrary keyword arguments.  It also required that
           ``cstruct`` was passed; it's broken out from
           ``kw`` in the method signature for backwards compatibility.
        """
        if cstruct is _marker:
            cstruct = self.cstruct
        values = {'field':self, 'cstruct':cstruct}
        values.update(kw)
        return self.widget.serialize(**values)

    def deserialize(self, pstruct):
        """ Deserialize the pstruct into a cstruct and return the cstruct."""
        return self.widget.deserialize(self, pstruct)

    def render(self, appstruct=_marker, **kw):
        """ Render the field (or form) to HTML using ``appstruct`` as a set
        of default values and returns the HTML string.  ``appstruct`` is
        typically a dictionary of application values matching the schema used
        by this form, or ``colander.null`` to render all defaults.  If it
        is omitted, the rendering will use the ``appstruct`` passed to the
        constructor.

        Calling this method passing an appstruct is the same as calling::

           cstruct = form.set_appstruct(appstruct)
           form.serialize(cstruct, **kw)

        Calling this method without passing an appstruct is the same as
        calling::

           cstruct = form.cstruct
           form.serialize(cstruct, **kw)

        See the documentation for
        :meth:`colander.SchemaNode.serialize` and
        :meth:`deform.widget.Widget.serialize` .

        .. note::

           Deform versions before 0.9.8 only accepted a ``readonly``
           keyword argument to this function.  Version 0.9.8 and later accept
           arbitrary keyword arguments.
        """
        if appstruct is not _marker:
            self.set_appstruct(appstruct)
        cstruct = self.cstruct
        kw.pop('cstruct', None) # disallowed
        html = self.serialize(cstruct, **kw)
        return html

    def validate(self, controls, subcontrol=None):
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
          from deform import Form
          import colander

          from my_application import do_something

          class MySchema(colander.MappingSchema):
              color = colander.SchemaNode(colander.String())

          schema = MySchema()

          def view(request):
              form = Form(schema, buttons=('submit',))
              if 'submit' in request.POST:  # form submission needs validation
                  controls = request.POST.items()
                  try:
                      deserialized = form.validate(controls)
                      do_something(deserialized)
                      return HTTPFound(location='http://example.com/success')
                  except ValidationFailure as e:
                      return {'form':e.render()}
              else:
                  return {'form':form.render()} # the form just needs rendering

        .. warning::

            ``form.validate(controls)`` mutates the ``form`` instance, so the
            ``form`` instance should be constructed (and live) inside one
            request.

        If ``subcontrol`` is supplied, it represents a named subitem in the
        data returned by ``peppercorn.parse(controls)``.  Use this subitem as
        the pstruct to validate instead of using the entire result of
        ``peppercorn.parse(controls)`` as the pstruct to validate.  For
        example, if you've embedded a mapping in the form named ``user``, and
        you want to validate only the data contained in that mapping instead
        if all of the data in the form post, you might use
        ``form.validate(controls, subcontrol='user')``.
        """
        pstruct = peppercorn.parse(controls)
        if subcontrol is not None:
            pstruct = pstruct.get(subcontrol, colander.null)
        return self.validate_pstruct(pstruct)

    def validate_pstruct(self, pstruct):
        """
        Validate the pstruct passed.  Works exactly like the
        :class:`deform.field.validate` method, except it accepts a pstruct
        instead of a set of form controls.  A usage example follows::

          if 'submit' in request.POST:  # the form submission needs validation
              controls = request.POST.items()
              pstruct = peppercorn.parse(controls)
              substruct = pstruct['submapping']
              try:
                  deserialized = form.validate_pstruct(substruct)
                  do_something(deserialized)
                  return HTTPFound(location='http://example.com/success')
              except ValidationFailure, e:
                  return {'form':e.render()}
          else:
              return {'form':form.render()} # the form just needs rendering
        """

        exc = None

        try:
            cstruct = self.deserialize(pstruct)
        except colander.Invalid as e:
            # fill in errors raised by widgets
            self.widget.handle_error(self, e)
            cstruct = e.value
            exc = e

        self.cstruct = cstruct

        try:
            appstruct = self.schema.deserialize(cstruct)
        except colander.Invalid as e:
            # fill in errors raised by schema nodes
            self.widget.handle_error(self, e)
            exc = e

        if exc:
            raise exception.ValidationFailure(self, cstruct, exc)

        return appstruct

    def _get_cstruct(self):
        return self._cstruct

    def _set_cstruct(self, cstruct):
        self._cstruct = cstruct
        child_cstructs = self.schema.cstruct_children(cstruct)
        if not isinstance(child_cstructs, colander.SequenceItems):
            # If the schema's type returns SequenceItems, it means that the
            # node is a sequence node, which means it has one child
            # representing its prototype instead of a set of "real" children;
            # our widget handle cloning the prototype node.  The prototype's
            # cstruct will already be set up with its default value by virtue
            # of set_appstruct having been called in its constructor, and we
            # needn't (and can't) do anything more.
            for n, child in enumerate(self.children):
                child.cstruct = child_cstructs[n]

    def _del_cstruct(self):
        if '_cstruct' in self.__dict__:
            # rely on class-scope _cstruct (null)
            del self._cstruct

    cstruct = property(_get_cstruct, _set_cstruct, _del_cstruct)

    def __repr__(self):
        return '<%s.%s object at %d (schemanode %r)>' % (
            self.__module__,
            self.__class__.__name__,
            id(self),
            self.schema.name,
            )

    def set_appstruct(self, appstruct):
        """ Set the cstruct of this node (and its child nodes) using
        ``appstruct`` as input."""
        cstruct = self.schema.serialize(appstruct)
        self.cstruct = cstruct
        return cstruct

    def set_pstruct(self, pstruct):
        """ Set the cstruct of this node (and its child nodes) using
        ``pstruct`` as input."""
        try:
            cstruct = self.deserialize(pstruct)
        except colander.Invalid as e:
            # explicitly don't set errors
            cstruct = e.value
        self.cstruct = cstruct

    def render_template(self, template, **kw):
        """ Render the template named ``template`` using ``kw`` as the
        top-level keyword arguments (augmented with ``field`` and ``cstruct``
        if necessary)"""
        values = {'field':self, 'cstruct':self.cstruct}
        values.update(kw) # allow caller to override field and cstruct
        return self.renderer(template, **values)

    # retail API

    def start_mapping(self, name=None):
        """ Create a start-mapping tag (a literal).  If ``name`` is ``None``,
        the name of this node will be used to generate the name in the tag.
        See the :term:`Peppercorn` documentation for more information.
        """
        if name is None:
            name = self.name
        tag = '<input type="hidden" name="__start__" value="%s:mapping"/>'
        return Markup(tag % (name,))

    def end_mapping(self, name=None):
        """ Create an end-mapping tag (a literal).  If ``name`` is ``None``,
        the name of this node will be used to generate the name in the tag.
        See the :term:`Peppercorn` documentation for more information.
        """
        if name is None:
            name = self.name
        tag = '<input type="hidden" name="__end__" value="%s:mapping"/>'
        return Markup(tag % (name,))

    def start_sequence(self, name=None):
        """ Create a start-sequence tag (a literal).  If ``name`` is ``None``,
        the name of this node will be used to generate the name in the tag.
        See the :term:`Peppercorn` documentation for more information.
        """
        if name is None:
            name = self.name
        tag = '<input type="hidden" name="__start__" value="%s:sequence"/>'
        return Markup(tag % (name,))

    def end_sequence(self, name=None):
        """ Create an end-sequence tag (a literal).  If ``name`` is ``None``,
        the name of this node will be used to generate the name in the tag.
        See the :term:`Peppercorn` documentation for more information.
        """

        if name is None:
            name = self.name
        tag = '<input type="hidden" name="__end__" value="%s:sequence"/>'
        return Markup(tag % (name,))

    def start_rename(self, name=None):
        """ Create a start-rename tag (a literal).  If ``name`` is ``None``,
        the name of this node will be used to generate the name in the tag.
        See the :term:`Peppercorn` documentation for more information.
        """
        if name is None:
            name = self.name
        tag = '<input type="hidden" name="__start__" value="%s:rename"/>'
        return Markup(tag % (name,))

    def end_rename(self, name=None):
        """ Create a start-rename tag (a literal).  If ``name`` is ``None``,
        the name of this node will be used to generate the name in the tag.
        See the :term:`Peppercorn` documentation for more information.
        """
        if name is None:
            name = self.name
        tag = '<input type="hidden" name="__end__" value="%s:rename"/>'
        return Markup(tag % (name,))

