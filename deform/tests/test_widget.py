"""Widget tests."""
# Standard Library
import unittest

# Pyramid
import colander

# Deform
from deform.compat import text_type


def invalid_exc(func, *arg, **kw):
    try:
        func(*arg, **kw)
    except colander.Invalid as e:
        return e
    else:
        raise AssertionError("Invalid not raised")  # pragma: no cover


class TestWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import Widget

        return Widget(**kw)

    def test_ctor(self):
        widget = self._makeOne(a=1, b=2)
        self.assertEqual(widget.a, 1)
        self.assertEqual(widget.b, 2)

    def test_serialize(self):
        widget = self._makeOne()
        self.assertRaises(NotImplementedError, widget.serialize, None, None)

    def test_deserialize(self):
        widget = self._makeOne()
        self.assertRaises(NotImplementedError, widget.deserialize, None, None)

    def test_handle_error(self):
        inner_widget = self._makeOne()
        outer_widget = self._makeOne()
        inner_field = DummyField()
        inner_field.widget = inner_widget
        outer_field = DummyField()
        outer_field.widget = outer_widget
        outer_field.children = [inner_field]
        inner_error = DummyInvalid()
        outer_error = DummyInvalid(inner_error)
        outer_widget.handle_error(outer_field, outer_error)
        self.assertEqual(inner_field.error, inner_error)
        self.assertEqual(outer_field.error, outer_error)

    def test_handle_error_already_has_error(self):
        widget = self._makeOne()
        widget.error = "abc"
        field = DummyField()
        error = DummyInvalid()
        widget.handle_error(field, error)
        self.assertEqual(widget.error, "abc")


class TestTextInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import TextInputWidget

        return TextInputWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize_strip(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = " abc "
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "abc")

    def test_deserialize_no_strip(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = " abc "
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, " abc ")

    def test_deserialize_null(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = ""
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, colander.null)

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {}
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)


class TestMoneyInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import MoneyInputWidget

        return MoneyInputWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")
        self.assertEqual(renderer.kw["mask_options"], "{}")

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")
        self.assertEqual(renderer.kw["mask_options"], "{}")

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)
        self.assertEqual(renderer.kw["mask_options"], "{}")

    def test_serialize_not_null_with_options(self):
        widget = self._makeOne(options={"allowZero": True})
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)
        self.assertEqual(renderer.kw["mask_options"], '{"allowZero": true}')

    def test_serialize_not_null_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)
        self.assertEqual(renderer.kw["mask_options"], "{}")

    def test_deserialize_strip(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = " abc "
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "abc")

    def test_deserialize_null(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = ""
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, colander.null)

    def test_deserialize_with_default_thousands_separator(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = "1,000,000.00"
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "1000000.00")

    def test_deserialize_with_nondefault_thousands_separator(self):
        widget = self._makeOne()
        widget.options = {"thousands": "!"}
        field = DummyField()
        pstruct = "1!000!000.00"
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "1000000.00")

    def test_deserialize_bad_type(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})


class TestAutocompleteInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import AutocompleteInputWidget

        return AutocompleteInputWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_removed_delay(self):
        widget = self._makeOne()
        widget.delay = 300
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        self.assertRaises(ValueError, widget.serialize, field, None)

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_url(self):
        import json

        widget = self._makeOne()
        url = "http://example.com"
        widget.values = url
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)
        self.assertEqual(
            json.loads(renderer.kw["options"]),
            {
                "limit": 8,
                "minLength": 1,
                "remote": "http://example.com?term=%QUERY",
            },
        )

    def test_serialize_iterable(self):
        import json

        widget = self._makeOne()
        vals = [1, 2, 3, 4]
        widget.values = vals
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)
        self.assertEqual(
            json.loads(renderer.kw["options"]),
            {"local": [1, 2, 3, 4], "minLength": 1, "limit": 8},
        )

    def test_serialize_not_null_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize_strip(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = " abc "
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "abc")

    def test_deserialize_no_strip(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = " abc "
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, " abc ")

    def test_deserialize_null(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = ""
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, colander.null)

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})


class TestDateInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import DateInputWidget

        return DateInputWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "")
        self.assertEqual(result, colander.null)

    def test_deserialize_date_submit(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(
            field, {"date": "foo", "date_submit": "bar"}
        )
        self.assertEqual(result, "bar")

    def test_deserialize_date(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, {"date": "foo", "date_submit": ""})
        self.assertEqual(result, "foo")

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, "garbage"
        )

    def test_deserialize_missing_fields(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_bad_field(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {"date": {}, "date_submit": {}}
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)

    def test_options_changed_and_default(self):
        widget2 = self._makeOne()
        widget = self._makeOne(options={"format": "foo"})
        self.assertEqual(widget.options["format"], "foo")
        self.assertEqual(widget2.options, None)


class TestTimeInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import TimeInputWidget

        return TimeInputWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "")
        self.assertEqual(result, colander.null)

    def test_deserialize_success(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, {"time": "14:15:16"})
        self.assertEqual(result, "14:15:16")

    def test_deserialize_time_submit(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(
            field, {"time": "14:15:16", "time_submit": "14:15:17"}
        )
        self.assertEqual(result, "14:15:17")

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, "garbage"
        )

    def test_deserialize_missing_fields(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_bad_field(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {"time": {}, "time_submit": "14:15:17"}
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)

    def test_options_changed_and_default(self):
        widget2 = self._makeOne()
        widget = self._makeOne(options={"format": "foo"})
        self.assertEqual(widget.options["format"], "foo")
        self.assertEqual(widget2.options["format"], "HH:i")


class TestDateTimeInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import DateTimeInputWidget

        return DateTimeInputWidget(**kw)

    def test_date_options_changed_and_default(self):
        widget2 = self._makeOne()
        widget = self._makeOne(date_options={"format": "foo"})
        self.assertEqual(widget.date_options["format"], "foo")
        self.assertEqual(widget2.date_options, None)

    def test_serialize_with_timezone(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(DummySchema(), renderer=renderer)
        cstruct = "2011-12-13T14:15:16+01:00"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["date"], "2011-12-13")
        self.assertEqual(renderer.kw["time"], "14:15:16")

    def test_serialize_with_timezone_and_microseconds(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(DummySchema(), renderer=renderer)
        cstruct = "2011-12-13T14:15:16.10932+01:00"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertNotEqual(renderer.kw["cstruct"], cstruct)
        self.assertEqual(renderer.kw["date"], "2011-12-13")
        self.assertEqual(renderer.kw["time"], "14:15:16")
        self.assertEqual(renderer.kw["cstruct"], "2011-12-13T14:15:16.10932")

    def test_serialize_without_timezone(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(DummySchema(), renderer=renderer)
        cstruct = "2011-12-13T14:15:16"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.kw["date"], "2011-12-13")
        self.assertEqual(renderer.kw["time"], "14:15:16")

    def test_serialize_no_separator(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(DummySchema(), renderer=renderer)
        cstruct = ""
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.kw["date"], "")
        self.assertEqual(renderer.kw["time"], "")

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(DummySchema(), renderer=renderer)
        cstruct = colander.null
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.kw["date"], "")
        self.assertEqual(renderer.kw["time"], "")

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = colander.null
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, colander.null)

    def test_deserialize_success(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {"date": "2011-12-13", "time": "14:15:16"}
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "2011-12-13T14:15:16")

    def test_deserialize_nochanges(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "2011-12-13",
            "date_submit": "",
            "time": "14:15:16",
            "time_submit": "",
        }
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "2011-12-13T14:15:16")

    def test_deserialize_date_changed(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "2011-12-13",
            "date_submit": "2011-12-12",
            "time": "14:15:16",
            "time_submit": "",
        }
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "2011-12-12T14:15:16")

    def test_deserialize_time_changed(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "2011-12-13",
            "date_submit": "",
            "time": "14:15:16",
            "time_submit": "14:15:15",
        }
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "2011-12-13T14:15:15")

    def test_deserialize_date_and_time_changed(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "2011-12-13",
            "date_submit": "2011-12-12",
            "time": "14:15:16",
            "time_submit": "14:15:15",
        }
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "2011-12-12T14:15:15")

    def test_deserialize_no_date(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "",
            "date_submit": "",
            "time": "14:15:16",
            "time_submit": "14:15:15",
        }
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)

    def test_deserialize_no_time(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "2011-12-13",
            "date_submit": "2011-12-12",
            "time": "",
            "time_submit": "",
        }
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)

    def test_deserialize_no_time_no_date(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "",
            "date_submit": "",
            "time": "",
            "time_submit": "",
        }
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, colander.null)

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, "garbage"
        )

    def test_deserialize_missing_fields(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_bad_field(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {
            "date": "2011-12-13",
            "date_submit": "2011-12-12",
            "time": {},
            "time_submit": {},
        }
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)


class TestHiddenWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import HiddenWidget

        return HiddenWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = "abc"
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, "abc")

    def test_deserialize_null(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, "")
        self.assertEqual(result, colander.null)

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, ["a", "b"]
        )


class TestPasswordWidget(TestTextInputWidget):
    def _makeOne(self, **kw):
        from deform.widget import PasswordWidget

        return PasswordWidget(**kw)


class TestTextAreaWidget(TestTextInputWidget):
    def _makeOne(self, **kw):
        from deform.widget import TextAreaWidget

        return TextAreaWidget(**kw)


class TestRichTextWidget(TestTextInputWidget):
    def _makeOne(self, **kw):
        from deform.widget import RichTextWidget

        return RichTextWidget(**kw)

    def test_options(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        options = {
            "theme_advanced_buttons1": "bold,italic,bullist,numlist",
            "verify_html": True,
            "element_format": "html",
        }
        widget = self._makeOne(options=options)
        cstruct = "abc"
        widget.serialize(field, cstruct)

        # Default options should be provided
        result = renderer.kw["tinymce_options"]
        self.assertTrue('"height": 240' in result)
        self.assertTrue('"width": 0' in result)

        # Custom options should be set
        self.assertTrue(
            '"theme_advanced_buttons1": "bold,italic,bullist,numlist"'
            in result
        )
        self.assertTrue('"verify_html": true' in result)
        self.assertTrue('"element_format": "html"' in result)


class TestCheckboxWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckboxWidget

        return CheckboxWidget(**kw)

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, "false")

    def test_deserialize_true_val(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "true")
        self.assertEqual(result, "true")

    def test_deserialize_false_val(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "false")
        self.assertEqual(result, "false")

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})


class TestRadioChoiceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import RadioChoiceWidget

        return RadioChoiceWidget(**kw)

    def test_serialize_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_null_alternate_null_value(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.null_value = "fred"
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "fred")

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_other(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "true")
        self.assertEqual(result, "true")

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})


class TestSelectWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import SelectWidget

        return SelectWidget(**kw)

    def test_serialize_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_null_alternate_null_value(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.null_value = "fred"
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "fred")

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = "abc"
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = "abc"
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_integer_values(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne(values=((1, "one"),))
        widget.serialize(field, None)
        self.assertEqual(renderer.kw["values"], [("1", "one")])

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_null_value(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "")
        self.assertEqual(result, colander.null)

    def test_deserialize_other(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "true")
        self.assertEqual(result, "true")

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_multiple(self):
        widget = self._makeOne(multiple=True)
        field = DummyField()
        result = widget.deserialize(field, ["foo", "bar"])
        self.assertEqual(result, ["foo", "bar"])

    def test_deserialize_multiple_bad_type(self):
        widget = self._makeOne(multiple=True)
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_multiple_bad_item(self):
        widget = self._makeOne(multiple=True)
        field = DummyField()
        pstruct = ["foo", {}]
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)

    def test_selected_tag(self):
        """Test apply 'selected' to select."""
        widget = self._makeOne(multiple=False)
        widget.get_select_value("foo", "foo") == "selected"
        widget.get_select_value("foo", "bar") is None

    def test_selected_tag_multiple(self):
        """Test apply 'selected' to multiselect."""
        widget = self._makeOne(multiple=True)
        widget.get_select_value(["foo", "bar"], "foo") == "selected"
        widget.get_select_value(["foo", "bar"], "moo") is None


class TestCheckboxChoiceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckboxChoiceWidget

        return CheckboxChoiceWidget(**kw)

    def test_serialize_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], ())

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], ())

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = ("abc",)
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = ("abc",)
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_integer_values(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne(values=((1, "one"),))
        widget.serialize(field, None)
        self.assertEqual(renderer.kw["values"], [("1", "one")])

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_single_string(self):
        # If only one checkbox was checked:  DAMN HTML forms!
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, "abc")
        self.assertEqual(result, ("abc",))

    def test_deserialize_other(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, ["abc"])
        self.assertEqual(result, ("abc",))

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_bad_field(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = ["abd", []]
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)


class TestCheckedInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckedInputWidget

        return CheckedInputWidget(**kw)

    def test_serialize_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")
        self.assertEqual(renderer.kw["confirm"], "")

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")
        self.assertEqual(renderer.kw["confirm"], "")

    def test_serialize_true(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, True)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], True)
        self.assertEqual(renderer.kw["confirm"], True)

    def test_serialize_false(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, False)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], False)
        self.assertEqual(renderer.kw["confirm"], False)

    def test_serialize_true_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, True, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], True)
        self.assertEqual(renderer.kw["confirm"], True)

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_empty(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, {"name": "", "name-confirm": ""})
        self.assertEqual(result, colander.null)
        self.assertEqual(field.error, None)

    def test_deserialize_nonmatching(self):
        widget = self._makeOne()
        field = DummyField()
        e = invalid_exc(
            widget.deserialize,
            field,
            {"name": "password", "name-confirm": "not"},
        )
        self.assertEqual(e.value, "password")
        self.assertEqual(e.msg, "Fields did not match")

    def test_deserialize_confirm_hint_on_field(self):
        widget = self._makeOne()
        field = DummyField()
        e = invalid_exc(
            widget.deserialize,
            field,
            {"name": "password", "name-confirm": "not"},
        )
        self.assertEqual(e.value, "password")
        self.assertEqual(getattr(field, "name-confirm", ""), "not")

    def test_deserialize_matching(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(
            field, {"name": "password", "name-confirm": "password"}
        )
        self.assertEqual(result, "password")
        self.assertEqual(field.error, None)

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, "garbage"
        )
        self.assertEqual(field.error, None)

    def test_deserialize_missing_fields(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_bad_field(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {"name": "x", "name-confirm": ["x"]}
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)


class TestCheckedPasswordWidget(TestCheckedInputWidget):
    def _makeOne(self, **kw):
        from deform.widget import CheckedPasswordWidget

        return CheckedPasswordWidget(**kw)

    def test_deserialize_nonmatching(self):
        widget = self._makeOne()
        field = DummyField()
        e = invalid_exc(
            widget.deserialize,
            field,
            {"name": "password", "name-confirm": "not"},
        )
        self.assertEqual(e.value, "password")
        self.assertEqual(e.msg, "Password did not match confirm")


class TestFileUploadWidget(unittest.TestCase):
    def _makeOne(self, tmpstore, **kw):
        from deform.widget import FileUploadWidget

        return FileUploadWidget(tmpstore, **kw)

    def test_serialize_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], {})

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], {})

    def test_serialize_uid_not_in_tmpstore(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        cstruct = {"uid": "uid"}
        widget.serialize(field, cstruct)
        self.assertEqual(tmpstore["uid"], cstruct)

    def test_serialize_uid_in_tmpstore(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        existing = {"uid": "santa"}
        tmpstore["uid"] = existing
        widget = self._makeOne(tmpstore)
        cstruct = {"uid": "notsanta"}
        widget.serialize(field, cstruct)
        self.assertEqual(tmpstore["uid"], existing)

    def test_serialize_uid_in_tmpstore_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        existing = {"uid": "santa"}
        tmpstore["uid"] = existing
        widget = self._makeOne(tmpstore)
        cstruct = {"uid": "notsanta"}
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(tmpstore["uid"], existing)

    def test_deserialize_null(self):
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_no_file_selected_no_previous_file(self):
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {})
        self.assertEqual(result, colander.null)

    def test_deserialize_no_file_selected_no_previous_file_with_upload(self):
        # If no upload is selected the browser sends back the name 'upload'.
        # In pyramid under python3 we have {'upload': b''} as cstruct
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {"upload": b""})
        self.assertEqual(result, colander.null)

    def test_deserialize_no_file_selected_with_previous_file(self):
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        tmpstore["uid"] = "abc"
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {"uid": "uid"})
        self.assertEqual(result, "abc")

    def test_deserialize_no_file_selected_with_previous_file_missing(self):
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {"uid": "uid"})
        self.assertEqual(result, colander.null)

    def test_deserialize_file_selected_no_previous_file(self):
        schema = DummySchema()
        field = DummyField(schema)
        upload = DummyUpload()
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {"upload": upload})
        uid = list(tmpstore.keys())[0]
        self.assertEqual(result["uid"], uid)
        self.assertEqual(result["fp"], "fp")
        self.assertEqual(result["filename"], "filename")
        self.assertEqual(result["mimetype"], "mimetype")
        self.assertEqual(result["size"], "size")
        self.assertEqual(result["preview_url"], "http://localhost/filename")
        self.assertEqual(tmpstore[uid], result)

    def test_deserialize_file_selected_with_previous_file(self):
        schema = DummySchema()
        field = DummyField(schema)
        upload = DummyUpload()
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {"upload": upload, "uid": "uid"})
        self.assertEqual(result["uid"], "uid")
        self.assertEqual(result["fp"], "fp")
        self.assertEqual(result["filename"], "filename")
        self.assertEqual(result["mimetype"], "mimetype")
        self.assertEqual(result["size"], "size")
        self.assertEqual(result["preview_url"], "http://localhost/filename")
        self.assertEqual(tmpstore["uid"], result)

    def test_deserialize_file_selected_with_previous_file_IE_whole_path(self):
        schema = DummySchema()
        field = DummyField(schema)
        upload = DummyUpload()
        upload.filename = r"c:\foo\bar\baz.pt"
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {"upload": upload, "uid": "uid"})
        self.assertEqual(result["uid"], "uid")
        self.assertEqual(result["fp"], "fp")
        self.assertEqual(result["filename"], "baz.pt")
        self.assertEqual(result["mimetype"], "mimetype")
        self.assertEqual(result["size"], "size")
        self.assertEqual(result["preview_url"], "http://localhost/baz.pt")
        self.assertEqual(tmpstore["uid"], result)

    def test_deserialize_bad_type(self):
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, "garbage"
        )

    def test_deserialize_bad_field(self):
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        field = DummyField()
        pstruct = {"upload": "garbage"}
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)


class TestDatePartsWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import DatePartsWidget

        return DatePartsWidget(**kw)

    def test_serialize_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["year"], "")
        self.assertEqual(renderer.kw["month"], "")
        self.assertEqual(renderer.kw["day"], "")

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, "2010-12-1")
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["year"], "2010")
        self.assertEqual(renderer.kw["month"], "12")
        self.assertEqual(renderer.kw["day"], "1")

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, "2010-12-1", readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["year"], "2010")
        self.assertEqual(renderer.kw["month"], "12")
        self.assertEqual(renderer.kw["day"], "1")

    def test_deserialize_not_null(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        result = widget.deserialize(
            field, {"year": "1", "month": "2", "day": "3"}
        )
        self.assertEqual(result, "1-2-3")

    def test_deserialize_assume_y2k_2digit(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        result = widget.deserialize(
            field, {"year": "01", "month": "2", "day": "3"}
        )
        self.assertEqual(result, "2001-2-3")

    def test_deserialize_dont_assume_y2k_2digit(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        widget.assume_y2k = False
        result = widget.deserialize(
            field, {"year": "01", "month": "2", "day": "3"}
        )
        self.assertEqual(result, "01-2-3")

    def test_deserialize_null(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptyfields(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        result = widget.deserialize(
            field, {"year": "\t", "month": "", "day": ""}
        )
        self.assertEqual(result, colander.null)

    def test_deserialize_incomplete(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        e = invalid_exc(
            widget.deserialize, field, {"year": "1", "month": "", "day": ""}
        )
        self.assertEqual(e.msg, "Incomplete date")

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, "garbage"
        )

    def test_deserialize_missing_fields(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, {})

    def test_deserialize_bad_field(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = {"year": "1970", "month": "1", "day": []}
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)


class TestMappingWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import MappingWidget

        return MappingWidget(**kw)

    def test_serialize_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], {})

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], {})

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = {"a": 1}
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = {"a": 1}
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], cstruct)

    def test_deserialize_null(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, {})

    def test_deserialize_non_null(self):
        widget = self._makeOne()
        field = DummyField()
        inner_field = DummyField()
        inner_field.name = "a"
        inner_widget = DummyWidget()
        inner_widget.name = "a"
        inner_field.widget = inner_widget
        field.children = [inner_field]
        pstruct = {"a": 1}
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, {"a": 1})

    def test_deserialize_error(self):
        widget = self._makeOne()
        field = DummyField()
        inner_field = DummyField()
        inner_field.name = "a"
        inner_widget = DummyWidget(
            exc=colander.Invalid(inner_field, "wrong", value="a")
        )
        inner_widget.name = "a"
        inner_field.widget = inner_widget
        field.children = [inner_field]
        pstruct = {"a": 1}
        e = invalid_exc(widget.deserialize, field, pstruct)
        self.assertEqual(e.value, {"a": "a"})
        self.assertEqual(e.children[0].value, "a")

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, ["a", 1]
        )


class TestSequenceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import SequenceWidget

        return SequenceWidget(**kw)

    def test_prototype_unicode(self):
        from deform.compat import url_unquote

        renderer = DummyRenderer(text_type("abc"))
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        protofield = DummyField(None, renderer)
        field.children = [protofield]
        result = widget.prototype(field)
        self.assertEqual(type(result), str)
        self.assertEqual(url_unquote(result), "abc")
        self.assertEqual(protofield.cloned, True)

    def test_prototype_field_has_no_name(self):
        from deform.compat import url_unquote  # noQA

        renderer = DummyRenderer(text_type("abc"))
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        protofield = DummyField(None, renderer)
        protofield.name = ""
        field.children = [protofield]
        self.assertRaises(ValueError, widget.prototype, field)

    def test_prototype_str(self):
        from deform.compat import url_unquote

        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        protofield = DummyField(None, renderer)
        field.children = [protofield]
        result = widget.prototype(field)
        self.assertEqual(type(result), str)
        self.assertEqual(url_unquote(result), "abc")
        self.assertEqual(protofield.cloned, True)

    def test_serialize_null(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        result = widget.serialize(field, colander.null)
        self.assertEqual(result, "abc")
        self.assertEqual(len(renderer.kw["subfields"]), 0)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], [])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_None(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        result = widget.serialize(field, None)
        self.assertEqual(result, "abc")
        self.assertEqual(len(renderer.kw["subfields"]), 0)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], [])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_null_min_len_larger_than_cstruct(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        widget.min_len = 2
        result = widget.serialize(field, ["abc"])
        self.assertEqual(result, "abc")
        self.assertEqual(len(renderer.kw["subfields"]), 2)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], ["abc", colander.null])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_null_min_one(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        widget.min_len = 1
        result = widget.serialize(field, colander.null)
        self.assertEqual(result, "abc")
        self.assertEqual(len(renderer.kw["subfields"]), 1)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], [colander.null])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_add_subitem_value(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        widget.add_subitem_text_template = "Yo ${subitem_description}"
        widget.serialize(field, colander.null)
        self.assertEqual(
            renderer.kw["add_subitem_text"].interpolate(), "Yo description"
        )

    def test_serialize_add_subitem_translates_title(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer, {"title": "titel"})
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        widget.add_subitem_text_template = "Yo ${subitem_title}"
        widget.serialize(field, colander.null)
        self.assertEqual(
            renderer.kw["add_subitem_text"].interpolate(), "Yo titel"
        )

    def test_serialize_add_subitem_translates_title_with_default_domain(self):
        # By default, we get a TranslationString whose domain is 'deform'
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer, {"title": "titel"})
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        widget.add_subitem_text_template = "Yo ${subitem_title}"
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.kw["add_subitem_text"].domain, "deform")

    def test_serialize_add_subitem_translates_title_with_another_domain(self):
        from translationstring import TranslationStringFactory

        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer, {"title": "titel"})
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        # Here we provide our own TranslationString with a custom domain
        custom_domain = "not_deform"
        _ = TranslationStringFactory(custom_domain)
        widget.add_subitem_text_template = _("Yo ${subitem_title}")
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.kw["add_subitem_text"].domain, custom_domain)

    def test_serialize_add_subitem_translates_description(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer, {"description": "omschrijving"})
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        widget.add_subitem_text_template = "Yo ${subitem_description}"
        widget.serialize(field, colander.null)
        self.assertEqual(
            renderer.kw["add_subitem_text"].interpolate(), "Yo omschrijving"
        )

    def test_serialize_subitem_value(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.kw["item_field"], inner)

    def test_serialize_not_null(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        result = widget.serialize(field, ["123"])
        self.assertEqual(result, "abc")
        self.assertEqual(len(renderer.kw["subfields"]), 1)
        self.assertEqual(renderer.kw["subfields"][0], ("123", inner))
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], ["123"])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        result = widget.serialize(field, ["123"], readonly=True)
        self.assertEqual(result, "abc")
        self.assertEqual(len(renderer.kw["subfields"]), 1)
        self.assertEqual(renderer.kw["subfields"][0], ("123", inner))
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], ["123"])
        self.assertEqual(renderer.template, widget.readonly_template)

    def test_serialize_with_sequence_widgets(self):
        renderer = DummyRenderer("abc")
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        inner = DummyField()
        field.children = [inner]
        sequence_field = DummyField()
        field.sequence_fields = [sequence_field]
        result = widget.serialize(field, ["123"])
        self.assertEqual(result, "abc")
        subfields = renderer.kw["subfields"]
        self.assertEqual(len(subfields), 1)
        self.assertEqual(subfields[0], ("123", sequence_field))
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], ["123"])
        self.assertEqual(renderer.template, widget.template)

    def test_deserialize_null(self):
        field = DummyField()
        inner_field = DummyField()
        field.children = [inner_field]
        widget = self._makeOne()
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, [])
        self.assertEqual(field.sequence_fields, [])

    def test_deserialize_not_null(self):
        field = DummyField()
        inner_field = DummyField()
        inner_field.widget = DummyWidget()
        field.children = [inner_field]
        widget = self._makeOne()
        result = widget.deserialize(field, ["123"])
        self.assertEqual(result, ["123"])
        self.assertEqual(len(field.sequence_fields), 1)
        self.assertEqual(field.sequence_fields[0], inner_field)

    def test_deserialize_error(self):
        field = DummyField()
        inner_field = DummyField()
        inner_field.widget = DummyWidget(
            exc=colander.Invalid(inner_field, "wrong", "a")
        )
        field.children = [inner_field]
        widget = self._makeOne()
        e = invalid_exc(widget.deserialize, field, ["123"])
        self.assertEqual(e.value, ["a"])
        self.assertEqual(e.children[0].value, "a")

    def test_handle_error(self):
        field = DummyField()
        widget = self._makeOne()
        inner_widget = DummyWidget()
        inner_invalid = DummyInvalid()
        inner_invalid.pos = 0
        error = DummyInvalid(inner_invalid)
        inner_field = DummyField()
        inner_field.widget = inner_widget
        field.sequence_fields = [inner_field]
        widget.handle_error(field, error)
        self.assertEqual(field.error, error)
        self.assertEqual(inner_widget.error, inner_invalid)

    def test_handle_error_already_has_error(self):
        widget = self._makeOne()
        widget.error = "abc"
        field = DummyField()
        error = DummyInvalid()
        widget.handle_error(field, error)
        self.assertEqual(widget.error, "abc")

    def test_deserialize_bad_type(self):
        field = DummyField()
        inner_field = DummyField()
        inner_field.widget = DummyWidget()
        field.children = [inner_field]
        widget = self._makeOne()
        self.assertRaises(
            colander.Invalid, widget.deserialize, field, {"x": "123"}
        )


class TestFormWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import FormWidget

        return FormWidget(**kw)

    def test_template(self):
        form = self._makeOne()
        self.assertEqual(form.template, "form")


class TestTextAreaCSVWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import TextAreaCSVWidget

        return TextAreaCSVWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_with_unparseable(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        field.unparseable = "aloooo"
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "aloooo")

    def test_serialize_not_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = [("a", "1")]
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "a,1\r\n")

    def test_serialize_not_None_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = [("a", "1")]
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "a,1\r\n")

    def test_serialize_csv_delimiter(self):
        widget = self._makeOne(delimiter=";")
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = [("a", "1")]
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "a;1\r\n")

    def test_deserialize(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = "a,1\r\n"
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, [["a", "1"]])

    def test_deserialize_bad_csv(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = "a,1\raa\r\r\n\n"
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)
        self.assertEqual(field.unparseable, pstruct)

    def test_deserialize_null(self):
        widget = self._makeOne(strip=False)
        schema = DummySchema()
        schema.required = False
        field = DummyField(schema=schema)
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne(strip=False)
        schema = DummySchema()
        schema.required = False
        field = DummyField(schema=schema)
        result = widget.deserialize(field, "")
        self.assertEqual(result, colander.null)

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, [])

    def test_handle_error_outermost_has_msg(self):
        widget = self._makeOne()
        error = DummyInvalid()
        error.msg = "msg"
        field = DummyField()
        widget.handle_error(field, error)
        self.assertEqual(field.error, error)

    def test_handle_error_children_have_msgs(self):
        widget = self._makeOne()
        error = DummyInvalid()
        inner_error1 = DummyInvalid()
        inner_error1.msg = "a"
        inner_error1.pos = 0
        inner_error2 = DummyInvalid()
        inner_error2.msg = "b"
        inner_error2.pos = 1
        error.children = [inner_error1, inner_error2]
        error.msg = None
        field = DummyField()
        field.schema = None
        widget.handle_error(field, error)
        self.assertEqual(field.error.msg, "line 1: Invalid\nline 2: Invalid")

    def test_deserialize_csv_delimiter(self):
        widget = self._makeOne(delimiter=";")
        field = DummyField()
        pstruct = "a;1\r\n"
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, [["a", "1"]])


class TestTextInputCSVWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import TextInputCSVWidget

        return TextInputCSVWidget(**kw)

    def test_serialize_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, colander.null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "")

    def test_serialize_with_unparseable(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        field.unparseable = "aloooo"
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "aloooo")

    def test_serialize_not_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = ("a", "1")
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "a,1")

    def test_serialize_not_None_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = ("a", "1")
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw["field"], field)
        self.assertEqual(renderer.kw["cstruct"], "a,1")

    def test_deserialize(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = "a,1\r\n"
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, ["a", "1"])

    def test_deserialize_bad_csv(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = "a,1\raa\r\r\n\n"
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)
        self.assertEqual(field.unparseable, pstruct)

    def test_deserialize_null(self):
        widget = self._makeOne(strip=False)
        schema = DummySchema()
        schema.required = False
        field = DummyField(schema=schema)
        result = widget.deserialize(field, colander.null)
        self.assertEqual(result, colander.null)

    def test_deserialize_emptystring(self):
        widget = self._makeOne(strip=False)
        schema = DummySchema()
        schema.required = False
        field = DummyField(schema=schema)
        result = widget.deserialize(field, "")
        self.assertEqual(result, colander.null)

    def test_deserialize_bad_type(self):
        widget = self._makeOne()
        field = DummyField()
        self.assertRaises(colander.Invalid, widget.deserialize, field, [])

    def test_handle_error_outermost_has_msg(self):
        widget = self._makeOne()
        error = DummyInvalid()
        error.msg = "msg"
        field = DummyField()
        widget.handle_error(field, error)
        self.assertEqual(field.error, error)

    def test_handle_error_children_have_msgs(self):
        widget = self._makeOne()
        error = DummyInvalid()
        inner_error1 = DummyInvalid()
        inner_error1.msg = "a"
        inner_error2 = DummyInvalid()
        inner_error2.msg = "b"
        error.children = [inner_error1, inner_error2]
        error.msg = None
        field = DummyField()
        field.schema = None
        widget.handle_error(field, error)
        self.assertEqual(field.error.msg, "Invalid\nInvalid")


class TestResourceRegistry(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import ResourceRegistry

        return ResourceRegistry(**kw)

    def test_use_defaults(self):
        from deform.widget import default_resources

        reg = self._makeOne()
        self.assertEqual(reg.registry, default_resources)

    def test_dont_use_defaults(self):
        from deform.widget import default_resources

        reg = self._makeOne(use_defaults=False)
        self.assertNotEqual(reg.registry, default_resources)

    def test_set_js_resources(self):
        reg = self._makeOne()
        reg.set_js_resources("abc", "123", 1, 2)
        self.assertEqual(reg.registry["abc"]["123"]["js"], (1, 2))

    def test_set_css_resources(self):
        reg = self._makeOne()
        reg.set_css_resources("abc", "123", 1, 2)
        self.assertEqual(reg.registry["abc"]["123"]["css"], (1, 2))

    def test___call___no_requirement(self):
        reg = self._makeOne()
        self.assertRaises(ValueError, reg.__call__, (("abc", "def"),))

    def test___call___no_version(self):
        reg = self._makeOne()
        reg.registry = {"abc": {"123": {"js": (1, 2)}}}
        self.assertRaises(ValueError, reg.__call__, (("abc", "def"),))

    def test___call___(self):
        reg = self._makeOne()
        reg.registry = {"abc": {"123": {"js": (1, 2)}}}
        result = reg([("abc", "123")])
        self.assertEqual(result, {"js": [1, 2], "css": []})

    def test___call___leaf_isnt_iterable(self):
        reg = self._makeOne()
        reg.registry = {"abc": {"123": {"js": "123", "css": "2"}}}
        result = reg([("abc", "123")])
        self.assertEqual(result, {"js": ["123"], "css": ["2"]})


class TestNormalizeChoices(unittest.TestCase):
    def _call(self, values):
        from deform.widget import _normalize_choices

        return _normalize_choices(values)

    def test_empty(self):
        self.assertEqual(self._call(()), [])

    def test_string(self):
        self.assertEqual(
            self._call((("value", "description"),)), [("value", "description")]
        )

    def test_text_type(self):
        self.assertEqual(
            self._call(((text_type("value"), "description"),)),
            [("value", "description")],
        )

    def test_integer(self):
        self.assertEqual(
            self._call(((1, "description"),)), [("1", "description")]
        )

    def test_optgroup_and_tuple(self):
        from deform.widget import OptGroup

        optgroup = OptGroup("label", (2, "two"))
        normalized = self._call(((1, "description"), optgroup))
        self.assertEqual(len(normalized), 2)
        self.assertEqual(normalized[0], ("1", "description"))
        self.assertTrue(isinstance(normalized[1], OptGroup))
        self.assertEqual(normalized[1].label, "label")
        self.assertEqual(normalized[1].options, (("2", "two"),))


class DummyRenderer(object):
    def __init__(self, result=""):
        self.result = result

    def __call__(self, template, **kw):
        self.template = template
        self.kw = kw
        return self.result


class DummyWidget(object):
    name = "name"

    def __init__(self, exc=None):
        self.exc = exc

    def deserialize(self, field, pstruct):
        if self.exc:
            raise self.exc
        return pstruct

    def handle_error(self, field, error):
        self.error = error


class DummySchema(object):
    pass


class DummyInvalid(object):
    pos = 0

    def __init__(self, *children):
        self.children = children

    def __str__(self):
        return "Invalid"


class DummyField(object):
    default = None
    error = None
    children = ()
    title = "title"
    description = "description"
    name = "name"
    cloned = False
    oid = "deformField1"
    required = True
    cstruct = colander.null

    def __init__(self, schema=None, renderer=None, translations=None):
        self.schema = schema
        self.renderer = renderer
        self.translations = translations

    def clone(self):
        self.cloned = True
        return self

    def deserialize(self, pstruct):
        return self.widget.deserialize(self, pstruct)

    def translate(self, term):
        if self.translations is None:
            return term
        return self.translations.get(term, term)

    def render_template(self, template, **kw):
        return self.renderer(template, **kw)


class DummyTmpStore(dict):
    def preview_url(self, uid):
        return "http://localhost/%s" % self[uid]["filename"]


class DummyUpload(object):
    file = "fp"
    filename = "filename"
    type = "mimetype"  # noQA
    length = "size"

    def __nonzero__(self):  # pragma: no cover
        # cgi.FieldStorage for file uploads are falsey
        return False
