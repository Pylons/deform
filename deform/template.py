import os
from pkg_resources import resource_filename

from deform.exception import TemplateError
from translationstring import ChameleonTranslate

try: # pragma: no cover (chameleon 1)
    from chameleon.zpt import language # will raise exception for c2
    from chameleon.zpt.template import PageTemplateFile

    def cache(func):
        def load(self, *args):
            template = self.registry.get(args)
            if template is None:
                self.registry[args] = template = func(self, *args)
            return template
        return load

    class ZPTTemplateLoader(object):
        """ A Chameleon ZPT template loader """
        parser = language.Parser()

        def __init__(self, search_path=None, auto_reload=True, debug=True,
                     encoding='utf-8', translate=None):
            if search_path is None:
                search_path = []
            if isinstance(search_path, basestring):
                search_path = [search_path]
            self.search_path = search_path
            self.auto_reload = auto_reload
            self.debug = debug
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
                                            debug = self.debug,
                                            encoding=self.encoding,
                                            translate=self.translate)
                except OSError:
                    self.notexists[path] = True

            raise TemplateError("Can not find template %s" % filename)
except ImportError:
    # Chameleon 2
    from chameleon.zpt.loader import TemplateLoader
    class ZPTTemplateLoader(TemplateLoader):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault('encoding', 'utf-8')
            super(ZPTTemplateLoader, self).__init__(*args, **kwargs)

        def load(self, filename, *args, **kwargs):
            try:
                return super(ZPTTemplateLoader, self).load(
                    filename, *args, **kwargs)
            except ValueError:
                raise TemplateError(filename)

class ZPTRendererFactory(object):
    """
    Construct a Chameleon ZPT :term:`renderer`.

    The resulting renderer callable accepts a template name *without*
    the ``.pt`` file extension and a set of keyword` values.

    **Arguments**

    search_path
      A sequence of strings representing fully qualified filesystem
      directories containing Deform Chameleon template sources.  The
      order in which the directories are listed within ``search_path``
      is the order in which they are checked for the template provided
      to the renderer.

    auto_reload
       If true, automatically reload templates when they change (slows
       rendering).  Default: ``True``.

    debug
       If true, show nicer tracebacks during Chameleon template rendering
       errors (slows rendering).  Default: ``True``.

    encoding
       The encoding that the on-disk representation of the templates
       and all non-ASCII values passed to the template should be
       expected to adhere to.  Default: ``utf-8``.

    translator
       A translation function used for internationalization when the
       ``i18n:translate`` attribute syntax is used in the Chameleon
       template is active or a
       :class:`translationstring.TranslationString` is encountered
       during output.  It must accept a translation string and return
       an interpolated translation.  Default: ``None`` (no translation
       performed).
    """
    def __init__(self, search_path, auto_reload=True, debug=False,
                 encoding='utf-8', translator=None):
        self.translate = translator
        loader = ZPTTemplateLoader(search_path=search_path,
                                   auto_reload=auto_reload,
                                   debug=debug,
                                   encoding=encoding,
                                   translate=ChameleonTranslate(translator))
        self.loader = loader

    def __call__(self, template_name, **kw):
        return self.load(template_name)(**kw)

    def load(self, template_name):
        return self.loader.load(template_name + '.pt')


default_dir = resource_filename('deform', 'templates/')
default_renderer = ZPTRendererFactory((default_dir,))
