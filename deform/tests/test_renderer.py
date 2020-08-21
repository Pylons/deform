# Standard Library
import unittest

# Deform
import deform


class TestConfigureZPT_Renderer(unittest.TestCase):
    def test_configure_zpt_renderer(self):
        # Pyramid
        from pyramid.i18n import get_localizer
        from pyramid.threadlocal import get_current_request

        #
        # Set up Chameleon templates (ZPT) rendering paths
        #

        def translator(term):
            # i18n localizing function
            return get_localizer(get_current_request()).translate(term)

        # Configure renderer
        deform.renderer.configure_zpt_renderer(
            search_path=["deform:custom_widgets"], translator=translator
        )

        self.assertTrue(
            isinstance(
                deform.form.Form.default_renderer,
                deform.template.ZPTRendererFactory,
            )
        )

        self.assertTrue(
            "custom_widgets"
            in str(deform.form.Form.default_renderer.loader.search_path)
        )
