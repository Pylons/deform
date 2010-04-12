import os
from pkg_resources import resource_filename

from chameleon.zpt import language
from chameleon.zpt.template import PageTemplateFile

from deform.exception import TemplateError

def cache(func):
    def load(self, *args):
        template = self.registry.get(args)
        if template is None:
            self.registry[args] = template = func(self, *args)
        return template
    return load

class ChameleonZPTTemplateLoader(object):
    parser = language.Parser()

    def __init__(self, search_path=None, auto_reload=False, encoding='utf-8',
                 translate=None):
        if search_path is None:
            search_path = []
        if isinstance(search_path, basestring):
            search_path = [search_path]
        self.search_path = search_path
        self.auto_reload = auto_reload
        self.encoding = encoding
        self.translate = translate
        self.registry = {}
        self.notexists = {}

    @cache
    def load(self, filename):
        for path in self.search_path:
            path = os.path.join(path, filename)
            if (path in self.notexists) and (not self.auto_reload):
                raise TemplateError("Can not find template %s" % filename)
            try:
                return PageTemplateFile(path, parser=self.parser,
                                        auto_reload=self.auto_reload,
                                        encoding=self.encoding,
                                        translate=self.translate)
            except OSError:
                self.notexists[path] = True

        raise TemplateError("Can not find template %s" % filename)

def make_renderer(search_path,
                  auto_reload=False,
                  encoding='utf-8',
                  translate=None):
    """
    Return a Chameleon ZPT :term:`renderer` which uses 

    The returned renderer callable accepts a template name *without*
    the ``.pt`` file extension.

    **Arguments**

    search_path
      A sequence of strings representing fully qualified filesystem
      directories containing Deform Chameleon template sources.  The
      order in which the directories are listed within ``search_path``
      is the order in which they are checked for the template provided
      to the renderer.

    auto_reload
       If true, automatically reload templates when they change.
       Default: ``False``.

    encoding
       The encoding that the on-disk representation of the templates
       and all non-ASCII values passed to the template should be
       expected to adhere to.  Default: ``utf-8``.

    translate
       A translation function used for internationalization when the
       ``i18n:translate`` attribute syntax is used in the Chameleon
       template, or, when :mod:`zope.i18n` is active, a
       :class:`zope.i18nmessageid.Message` is encountered in input.
       Default: ``None`` (no translation performed).
    """
    
    loader = ChameleonZPTTemplateLoader(search_path=search_path,
                                        auto_reload=auto_reload,
                                        encoding=encoding,
                                        translate=translate)

    def renderer(template_name, **kw):
        return loader.load(template_name + '.pt')(**kw)

    return renderer

default_dir = resource_filename('deform', 'templates/')
default_renderer = make_renderer((default_dir,))

