import deform
import deform.form

from pkg_resources import resource_filename


def configure_zpt_renderer(search_path=()):
    """Initialize ZPT widget rendering for Deform forms.

    Include given package asset paths in the paths Deform uses to
    look up widgets.

    Example:

    .. code-block:: python

        configure_zpt_renderer()

    :param search_path: List of additional search paths for widget templates.
    """

    default_paths = deform.form.Form.default_renderer.loader.search_path
    paths = []
    for path in search_path:
        pkg, resource_name = path.split(':')
        paths.append(resource_filename(pkg, resource_name))

    deform.form.Form.default_renderer = deform.ZPTRendererFactory(tuple(paths) + default_paths)