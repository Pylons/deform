"""Functional tests."""
# Standard Library
import datetime
import unittest

# Pyramid
import colander

# Deform
import deform.widget


class TestFunctional(unittest.TestCase):
    def _makeSchema(self):
        # Pyramid
        from colander import Boolean
        from colander import Date
        from colander import MappingSchema
        from colander import SchemaNode
        from colander import SequenceSchema
        from colander import String

        class DatesSchema(SequenceSchema):
            date = SchemaNode(Date())

        class SeriesSchema(MappingSchema):
            name = SchemaNode(String())
            dates = DatesSchema()

        class MySchema(MappingSchema):
            name = SchemaNode(String())
            title = SchemaNode(String())
            cool = SchemaNode(Boolean(), default=True, missing=True)
            series = SeriesSchema()
            nickname = SchemaNode(
                String(),
                widget=deform.widget.TextInputWidget(
                    attributes={
                        "maxlength": 10,
                        "placeholder": "Nickname",
                        "disabled": "disabled",
                    }
                ),
            )

        schema = MySchema()
        return schema

    def _makeForm(self, schema):
        # Deform
        from deform.form import Form

        return Form(schema, formid="myform")

    def _soupify(self, html):
        from bs4 import BeautifulSoup

        return BeautifulSoup(html, "html.parser")

    def test_render_empty(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        html = form.render()
        soup = self._soupify(html)
        form = soup.form
        self.assertEqual(form.get("action", ""), "")
        inputs = form.findAll("input")
        self.assertEqual(inputs[0]["name"], "_charset_")
        self.assertEqual(inputs[1]["name"], "__formid__")
        self.assertEqual(inputs[1]["value"], "myform")
        self.assertEqual(inputs[2]["name"], "name")
        self.assertEqual(inputs[2]["value"], "")
        self.assertEqual(inputs[3]["name"], "title")
        self.assertEqual(inputs[3]["value"], "")
        self.assertEqual(inputs[4]["name"], "cool")
        self.assertEqual(inputs[4].get("checked"), "checked")
        self.assertEqual(inputs[5]["name"], "__start__")
        self.assertEqual(inputs[5]["value"], "series:mapping")
        self.assertEqual(inputs[6]["name"], "name")
        self.assertEqual(inputs[6]["value"], "")
        self.assertEqual(inputs[7]["name"], "__start__")
        self.assertEqual(inputs[7]["value"], "dates:sequence")
        self.assertEqual(inputs[8]["name"], "__end__")
        self.assertEqual(inputs[8]["value"], "dates:sequence")
        self.assertEqual(inputs[9]["name"], "__end__")
        self.assertEqual(inputs[9]["value"], "series:mapping")

    def test_render_not_empty(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        appstruct = {
            "cool": False,
            "series": {"dates": [datetime.date(2010, 3, 21)]},
        }
        html = form.render(appstruct)
        soup = self._soupify(html)
        form = soup.form
        self.assertEqual(form.get("action", ""), "")
        inputs = form.findAll("input")
        self.assertEqual(inputs[0]["name"], "_charset_")
        self.assertEqual(inputs[1]["name"], "__formid__")
        self.assertEqual(inputs[1]["value"], "myform")
        self.assertEqual(inputs[2]["name"], "name")
        self.assertEqual(inputs[2]["value"], "")
        self.assertEqual(inputs[3]["name"], "title")
        self.assertEqual(inputs[3]["value"], "")
        self.assertEqual(inputs[4]["name"], "cool")
        self.assertEqual(inputs[4].get("checked"), None)
        self.assertEqual(inputs[5]["name"], "__start__")
        self.assertEqual(inputs[5]["value"], "series:mapping")
        self.assertEqual(inputs[6]["name"], "name")
        self.assertEqual(inputs[6]["value"], "")
        self.assertEqual(inputs[7]["name"], "__start__")
        self.assertEqual(inputs[7]["value"], "dates:sequence")
        self.assertEqual(inputs[9]["name"], "date")
        self.assertEqual(inputs[9]["value"], "2010-03-21")
        self.assertEqual(inputs[11]["name"], "__end__")
        self.assertEqual(inputs[11]["value"], "dates:sequence")
        self.assertEqual(inputs[12]["name"], "__end__")
        self.assertEqual(inputs[12]["value"], "series:mapping")

    def test_render_attributes(self):
        schema = self._makeSchema()
        form = self._makeForm(schema)
        html = form.render()
        soup = self._soupify(html)
        form = soup.form
        self.assertEqual(form.get("action", ""), "")
        inputs = form.findAll("input")
        self.assertEqual(inputs[10]["name"], "nickname")
        self.assertEqual(inputs[10]["value"], "")
        self.assertEqual(inputs[10]["placeholder"], "Nickname")
        self.assertEqual(inputs[10]["disabled"], "disabled")
        self.assertEqual(inputs[10]["maxlength"], "10")

    def test_widget_deserialize(self):
        filled = {
            "name": "project1",
            "title": "Cool project",
            "nickname": "petproject",
            "series": {
                "name": "date series 1",
                "dates": [{"date": "2008-10-12"}, {"date": "2009-10-12"}],
            },
        }
        schema = self._makeSchema()
        form = self._makeForm(schema)
        result = form.widget.deserialize(form, filled)
        expected = {
            "series": {
                "dates": ["2008-10-12", "2009-10-12"],
                "name": "date series 1",
            },
            "cool": "false",
            "nickname": "petproject",
            "name": "project1",
            "title": "Cool project",
        }
        self.assertEqual(result, expected)

    def test_validate(self):
        # Pyramid
        from colander import null

        # Deform
        from deform.exception import ValidationFailure

        schema = self._makeSchema()
        form = self._makeForm(schema)
        try:
            form.validate([])
        except ValidationFailure as vf:
            e = vf.error
            ve = vf
        self.assertEqual(form.error, e)
        self.assertEqual(form.children[0].error, e.children[0])
        self.assertEqual(form.children[1].error, e.children[1])
        self.assertEqual(form.children[3].error, e.children[2])
        self.assertEqual(
            form.children[3].children[0].error, e.children[2].children[0]
        )
        self.assertEqual(
            ve.cstruct,
            {
                "series": {"dates": [], "name": null},
                "cool": "false",
                "nickname": null,
                "name": null,
                "title": null,
            },
        )


@colander.deferred
def deferred_date_validator(node, kw):
    max_date = kw.get("max_date", datetime.date.today())
    return colander.Range(min=datetime.date.min, max=max_date)


@colander.deferred
def deferred_date_description(node, kw):
    max_date = kw.get("max_date", datetime.date.today())
    return "Blog post date (no earlier than %s)" % max_date.ctime()


@colander.deferred
def deferred_date_missing(node, kw):
    default_date = kw.get("default_date", datetime.date.today())
    return default_date


@colander.deferred
def deferred_body_validator(node, kw):
    max_bodylen = kw.get("max_bodylen", 1 << 18)
    return colander.Length(max=max_bodylen)


@colander.deferred
def deferred_body_description(node, kw):
    max_bodylen = kw.get("max_bodylen", 1 << 18)
    return "Blog post body (no longer than %s bytes)" % max_bodylen


@colander.deferred
def deferred_body_widget(node, kw):
    body_type = kw.get("body_type")
    if body_type == "richtext":
        widget = deform.widget.RichTextWidget()
    else:  # pragma: no cover
        widget = deform.widget.TextAreaWidget()
    return widget


@colander.deferred
def deferred_category_validator(node, kw):
    categories = kw.get("categories", [])
    return colander.OneOf([x[0] for x in categories])


@colander.deferred
def deferred_category_widget(node, kw):
    categories = kw.get("categories", [])
    return deform.widget.RadioChoiceWidget(values=categories)


class BlogPostSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title="Title",
        description="Blog post title",
        validator=colander.Length(min=5, max=100),
        widget=deform.widget.TextInputWidget(),
    )
    date = colander.SchemaNode(
        colander.Date(),
        title="Date",
        missing=deferred_date_missing,
        description=deferred_date_description,
        validator=deferred_date_validator,
        widget=deform.widget.DateInputWidget(),
    )
    body = colander.SchemaNode(
        colander.String(),
        title="Body",
        description=deferred_body_description,
        validator=deferred_body_validator,
        widget=deferred_body_widget,
    )
    category = colander.SchemaNode(
        colander.String(),
        title="Category",
        description="Blog post category",
        validator=deferred_category_validator,
        widget=deferred_category_widget,
    )


class IntSchema(colander.Schema):
    int_field = colander.SchemaNode(
        colander.Int(),
        widget=deform.widget.RadioChoiceWidget(
            values=((0, "zero"), (1, "one"))
        ),
    )


class RichTextSchema(colander.Schema):
    richtext = colander.SchemaNode(
        colander.String(), widget=deform.widget.RichTextWidget()
    )


class AutofocusDefaultSchema(colander.Schema):
    input1 = colander.SchemaNode(colander.String(),)


class AutofocusSchema(colander.Schema):
    input1 = colander.SchemaNode(colander.String(),)
    input2 = colander.SchemaNode(colander.String(), autofocus="on")


def remove_date(node, kw):
    if kw.get("nodates"):
        del node["date"]


class TestSchemas(unittest.TestCase):
    def test_int_on_radio_widget(self):
        schema = IntSchema()
        form = deform.Form(schema, buttons=("submit",))
        result_without_checked = form.render()

        self.assertFalse("checked" in result_without_checked)

        result_with_checked = form.render({"int_field": 1})
        value_index = result_with_checked.index('value="1"')
        checked_index = result_with_checked.index(
            'checked="checked"', value_index
        )
        self.assertTrue(checked_index > 0)

    def test_rich_text_textarea_escaped(self):
        schema = RichTextSchema()
        form = deform.Form(schema, buttons=('submit',))
        unescaped = '<script>boom</script>'
        result = form.render({'richtext': unescaped})
        self.assertTrue('boom' in result)
        self.assertTrue(unescaped not in result)

    def test_autofocus_off(self):
        schema = AutofocusSchema()
        form = deform.Form(schema, buttons=("submit",), focus="off")
        rendered = form.render()
        self.assertFalse('autofocus="autofocus"' in rendered)

    def test_autofocus_on(self):
        schema = AutofocusSchema()
        form = deform.Form(schema, buttons=("submit",), focus="on")
        rendered = form.render()
        self.assertTrue('autofocus="autofocus"' in rendered)

    def test_autofocus_default(self):
        schema = AutofocusDefaultSchema()
        form = deform.Form(schema, buttons=("submit",))
        rendered = form.render()
        self.assertTrue('autofocus="autofocus"' in rendered)


class TestDeferredFunction(unittest.TestCase):
    def test_it(self):
        schema = BlogPostSchema(after_bind=remove_date).bind(
            max_date=datetime.date.max,
            max_bodylen=5000,
            body_type="richtext",
            default_date=datetime.date.today(),
            categories=[("one", "One"), ("two", "Two")],
        )
        self.assertEqual(schema["date"].missing, datetime.date.today())
        self.assertEqual(schema["date"].validator.max, datetime.date.max)
        self.assertEqual(
            schema["date"].widget.__class__.__name__, "DateInputWidget"
        )
        self.assertEqual(
            schema["body"].description,
            "Blog post body (no longer than 5000 bytes)",
        )
        self.assertEqual(schema["body"].validator.max, 5000)
        self.assertEqual(
            schema["body"].widget.__class__.__name__, "RichTextWidget"
        )
        self.assertEqual(schema["category"].validator.choices, ["one", "two"])
        self.assertEqual(
            schema["category"].widget.values, [("one", "One"), ("two", "Two")]
        )
        new_schema = schema.bind(nodates=True)
        self.assertNotIn("date", new_schema)
