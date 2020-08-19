"""Renderer."""
from pkg_resources import resource_filename

# Deform
import deform
import deform.form


def configure_zpt_renderer(search_path=(), translator=None):
    """Initialize ZPT widget rendering for Deform forms.

    Include given package asset paths in the paths Deform uses to
    look up widgets.

    Example:

    .. code-block:: python

        from pyramid.threadlocal import get_current_request

        #
        # Set up Chameleon templates (ZTP) rendering paths
        #

        def translator(term):
            # i18n localizing function
            return get_localizer(get_current_request()).translate(term)

        # Configure renderer
        configure_zpt_renderer(("deformdemo:custom_widgets",), translator)


    :param search_path: List of additional search paths for widget templates.

    :param translator: Translator function to localizing i18n strings
    """

    # Don't let the user to slip in a string
    assert type(search_path) in (tuple, list)

    # Add more paths to besides the default one
    default_paths = deform.form.Form.default_renderer.loader.search_path
    paths = []
    for path in search_path:
        pkg, resource_name = path.split(":")
        paths.append(resource_filename(pkg, resource_name))

    deform.form.Form.default_renderer = deform.ZPTRendererFactory(
        tuple(paths) + default_paths, translator=translator
    )
