import os.path
from pkg_resources import resource_filename

from .exception import TemplateError
from translationstring import ChameleonTranslate

from chameleon.zpt.loader import TemplateLoader

class ZPTTemplateLoader(TemplateLoader):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('encoding', 'utf-8')
        super(ZPTTemplateLoader, self).__init__(*args, **kwargs)

    def load(self, filename, *args, **kwargs):
        if ':' in filename:
            pkg_name, fn = filename.split(':', 1)
            filename = resource_filename(pkg_name, fn)
        else:
            path, ext = os.path.splitext(filename)
            if not ext:
                filename = filename + '.pt'
        try:
            return super(ZPTTemplateLoader, self).load(
                filename, *args, **kwargs)
        except ValueError:
            raise TemplateError(filename)

class ZPTRendererFactory(object):
    """
    Construct a custom Chameleon ZPT :term:`renderer` for Deform.

    If the template name is an asset spec (has a colon in it, e.g.
    ``mypackage:subdir/subdir2/mytemplate.pt``), use
    ``pkg_resources.resource_filename`` to resolve it.
    Otherwise, fall back to search-path-based machinery to resolve it.

    Allowing an asset spec allows users to specify templates without the
    trouble of needing to add search paths to the deform rendering machinery.

    **Arguments**

    search_path
      A sequence of strings representing fully qualified filesystem
      directories containing Deform Chameleon template sources.  The
      order in which the directories are listed within ``search_path``
      is the order in which they are checked for the template provided
      to the renderer.  If every resource is an asset spec, however,
      the search path is never used.

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
        loader = ZPTTemplateLoader(
            search_path=search_path,
            auto_reload=auto_reload,
            debug=debug,
            encoding=encoding,
            translate=ChameleonTranslate(translator)
            )
        self.loader = loader

    def __call__(self, template_name, **kw):
        return self.load(template_name)(**kw)

    def load(self, template_name):
        return self.loader.load(template_name)
        
default_dir = resource_filename('deform', 'templates/')
default_renderer = ZPTRendererFactory((default_dir,))
