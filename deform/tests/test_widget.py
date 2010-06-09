import unittest

def invalid_exc(func, *arg, **kw):
    from colander import Invalid
    try:
        func(*arg, **kw)
    except Invalid, e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover

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
        outer_field.children = [ inner_field ]
        inner_error = DummyInvalid()
        outer_error = DummyInvalid(inner_error)
        outer_widget.handle_error(outer_field, outer_error)
        self.assertEqual(inner_field.error, inner_error)
        self.assertEqual(outer_field.error, outer_error)

    def test_handle_error_already_has_error(self):
        widget = self._makeOne()
        widget.error = 'abc'
        field = DummyField()
        error = DummyInvalid()
        widget.handle_error(field, error)
        self.assertEqual(widget.error, 'abc')

class TestTextInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import TextInputWidget
        return TextInputWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_serialize_not_null_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = 'abc'
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_strip(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = ' abc '
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, 'abc')

    def test_deserialize_no_strip(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = ' abc '
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, ' abc ')

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_emptystring(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        pstruct = ''
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, null)

class TestDateInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import DateInputWidget
        return DateInputWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_serialize_not_null_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = 'abc'
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_emptystring(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, '')
        self.assertEqual(result, null)

class TestHiddenWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import HiddenWidget
        return HiddenWidget(**kw)
    
    def test_serialize_null(self):
        from colander import null
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_not_null(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)
        
    def test_deserialize(self):
        widget = self._makeOne()
        field = DummyField()
        pstruct = 'abc'
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, 'abc')

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne(strip=False)
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

class TestPasswordWidget(TestTextInputWidget):
    def _makeOne(self, **kw):
        from deform.widget import PasswordWidget
        return PasswordWidget(**kw)

class TestTextAreaWidget(TestTextInputWidget):
    def _makeOne(self, **kw):
        from deform.widget import TextAreaWidget
        return TextAreaWidget(**kw)

class TestCheckboxWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckboxWidget
        return CheckboxWidget(**kw)

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, 'false')

    def test_deserialize_true_val(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'true')
        self.assertEqual(result, 'true')

    def test_deserialize_false_val(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'false')
        self.assertEqual(result, 'false')

class TestRadioChoiceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import RadioChoiceWidget
        return RadioChoiceWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_null_alternate_null_value(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.null_value = 'fred'
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'fred')

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_other(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'true')
        self.assertEqual(result, 'true')

class TestSelectWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import SelectWidget
        return SelectWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_null_alternate_null_value(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.null_value = 'fred'
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'fred')

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = 'abc'
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_null_value(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, '')
        self.assertEqual(result, null)

    def test_deserialize_other(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'true')
        self.assertEqual(result, 'true')

class TestCheckboxChoiceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckboxChoiceWidget
        return CheckboxChoiceWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], ())

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], ())

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = ('abc',)
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = ('abc',)
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_single_string(self):
        # If only one checkbox was checked:  DAMN HTTP forms!
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, 'abc')
        self.assertEqual(result, ('abc',))

    def test_deserialize_other(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, ['abc'])
        self.assertEqual(result, ('abc',))

class TestCheckedInputWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import CheckedInputWidget
        return CheckedInputWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_true(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, True)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], True)

    def test_serialize_false(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, False)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], False)

    def test_serialize_true_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, True, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], True)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_empty(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, {'value':'',
                                            'confirm':''})
        self.assertEqual(result, null)
        self.assertEqual(field.error, None)

    def test_deserialize_nonmatching(self):
        widget = self._makeOne()
        field = DummyField()
        e = invalid_exc(widget.deserialize, field,
                                    {'value':'password', 'confirm':'not'})
        self.assertEqual(e.value, 'password')
        self.assertEqual(e.msg, 'Fields did not match')

    def test_deserialize_matching(self):
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, {'value':'password',
                                            'confirm':'password'})
        self.assertEqual(result, 'password')
        self.assertEqual(field.error, None)

class TestCheckedPasswordWidget(TestCheckedInputWidget):
    def _makeOne(self, **kw):
        from deform.widget import CheckedPasswordWidget
        return CheckedPasswordWidget(**kw)

    def test_deserialize_nonmatching(self):
        widget = self._makeOne()
        field = DummyField()
        e = invalid_exc(widget.deserialize, field,
                                    {'value':'password', 'confirm':'not'})
        self.assertEqual(e.value, 'password')
        self.assertEqual(e.msg, 'Password did not match confirm')


class TestFileUploadWidget(unittest.TestCase):
    def _makeOne(self, tmpstore, **kw):
        from deform.widget import FileUploadWidget
        return FileUploadWidget(tmpstore, **kw)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], {})

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], {})

    def test_serialize_uid_not_in_tmpstore(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        cstruct = {'uid':'uid'}
        widget.serialize(field, cstruct)
        self.assertEqual(tmpstore['uid'], cstruct)

    def test_serialize_uid_in_tmpstore(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        existing = {'uid':'santa'}
        tmpstore['uid'] = existing
        widget = self._makeOne(tmpstore)
        cstruct = {'uid':'notsanta'}
        widget.serialize(field, cstruct)
        self.assertEqual(tmpstore['uid'], existing)

    def test_serialize_uid_in_tmpstore_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        tmpstore = DummyTmpStore()
        existing = {'uid':'santa'}
        tmpstore['uid'] = existing
        widget = self._makeOne(tmpstore)
        cstruct = {'uid':'notsanta'}
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(tmpstore['uid'], existing)

    def test_deserialize_null(self):
        from colander import null
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_no_file_selected_no_previous_file(self):
        from colander import null
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {})
        self.assertEqual(result, null)

    def test_deserialize_no_file_selected_with_previous_file(self):
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        tmpstore['uid'] = 'abc'
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {'uid':'uid'})
        self.assertEqual(result, 'abc')

    def test_deserialize_no_file_selected_with_previous_file_missing(self):
        from colander import null
        schema = DummySchema()
        field = DummyField(schema)
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {'uid':'uid'})
        self.assertEqual(result, null)

    def test_deserialize_file_selected_no_previous_file(self):
        schema = DummySchema()
        field = DummyField(schema)
        upload = DummyUpload()
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {'upload':upload})
        uid = tmpstore.keys()[0]
        self.assertEqual(result['uid'], uid)
        self.assertEqual(result['fp'], 'fp')
        self.assertEqual(result['filename'], 'filename')
        self.assertEqual(result['mimetype'], 'mimetype')
        self.assertEqual(result['size'], 'size')
        self.assertEqual(result['preview_url'], 'preview_url')
        self.assertEqual(tmpstore[uid], result)

    def test_deserialize_file_selected_with_previous_file(self):
        schema = DummySchema()
        field = DummyField(schema)
        upload = DummyUpload()
        tmpstore = DummyTmpStore()
        widget = self._makeOne(tmpstore)
        result = widget.deserialize(field, {'upload':upload, 'uid':'uid'})
        self.assertEqual(result['uid'], 'uid')
        self.assertEqual(result['fp'], 'fp')
        self.assertEqual(result['filename'], 'filename')
        self.assertEqual(result['mimetype'], 'mimetype')
        self.assertEqual(result['size'], 'size')
        self.assertEqual(result['preview_url'], 'preview_url')
        self.assertEqual(tmpstore['uid'], result)

class TestDatePartsWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import DatePartsWidget
        return DatePartsWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['year'], '')
        self.assertEqual(renderer.kw['month'], '')
        self.assertEqual(renderer.kw['day'], '')

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, '2010-12-1')
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['year'], '2010')
        self.assertEqual(renderer.kw['month'], '12')
        self.assertEqual(renderer.kw['day'], '1')

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, '2010-12-1', readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['year'], '2010')
        self.assertEqual(renderer.kw['month'], '12')
        self.assertEqual(renderer.kw['day'], '1')

    def test_deserialize_not_null(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        result = widget.deserialize(field, {'year':'1', 'month':'2', 'day':'3'})
        self.assertEqual(result, '1-2-3')

    def test_deserialize_assume_y2k_2digit(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        result = widget.deserialize(field,
                                    {'year':'01', 'month':'2', 'day':'3'})
        self.assertEqual(result, '2001-2-3')

    def test_deserialize_dont_assume_y2k_2digit(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        widget.assume_y2k = False
        result = widget.deserialize(field,
                                    {'year':'01', 'month':'2', 'day':'3'})
        self.assertEqual(result, '01-2-3')

    def test_deserialize_null(self):
        from colander import null
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_incomplete(self):
        schema = DummySchema()
        field = DummyField(schema, None)
        widget = self._makeOne()
        e = invalid_exc(widget.deserialize,
                        field, {'year':'1', 'month':'', 'day':''})
        self.assertEqual(e.msg, 'Incomplete')


class TestMappingWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import MappingWidget
        return MappingWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], {})

    def test_serialize_None(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], {})

    def test_serialize_not_null(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = {'a':1}
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        cstruct = {'a':1}
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], cstruct)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne()
        field = DummyField()
        result = widget.deserialize(field, null)
        self.assertEqual(result, {})

    def test_deserialize_non_null(self):
        widget = self._makeOne()
        field = DummyField()
        inner_field = DummyField()
        inner_field.name = 'a'
        inner_widget = DummyWidget()
        inner_widget.name = 'a'
        inner_field.widget = inner_widget
        field.children = [inner_field]
        pstruct = {'a':1}
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, {'a':1})

    def test_deserialize_error(self):
        from colander import Invalid
        widget = self._makeOne()
        field = DummyField()
        inner_field = DummyField()
        inner_field.name = 'a'
        inner_widget = DummyWidget(exc=Invalid(inner_field, 'wrong', value='a'))
        inner_widget.name = 'a'
        inner_field.widget = inner_widget
        field.children = [inner_field]
        pstruct = {'a':1}
        e = invalid_exc(widget.deserialize, field, pstruct)
        self.assertEqual(e.value, {'a':'a'})
        self.assertEqual(e.children[0].value, 'a')

class TestSequenceWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import SequenceWidget
        return SequenceWidget(**kw)

    def test_prototype_unicode(self):
        import urllib
        renderer = DummyRenderer(u'abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        protofield = DummyField()
        field.children=[protofield]
        result = widget.prototype(field)
        self.assertEqual(type(result), str)
        self.assertEqual(urllib.unquote(result), 'abc')
        self.assertEqual(protofield.cloned, True)

    def test_prototype_str(self):
        import urllib
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        protofield = DummyField()
        field.children=[protofield]
        result = widget.prototype(field)
        self.assertEqual(type(result), str)
        self.assertEqual(urllib.unquote(result), 'abc')
        self.assertEqual(protofield.cloned, True)

    def test_serialize_null(self):
        from colander import null
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children=[inner]
        widget = self._makeOne()
        result = widget.serialize(field, null)
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 0)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], [])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_None(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children=[inner]
        widget = self._makeOne()
        result = widget.serialize(field, None)
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 0)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], [])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_null_render_initial_item(self):
        from colander import null
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children=[inner]
        widget = self._makeOne()
        widget.render_initial_item = True
        result = widget.serialize(field, null)
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 1)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], [null])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_add_subitem_value(self):
        from colander import null
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children=[inner]
        widget = self._makeOne()
        widget.add_subitem_text_template = 'Yo ${subitem_description}'
        widget.serialize(field, null)
        self.assertEqual(renderer.kw['add_subitem_text'].interpolate(),
                         'Yo description')

    def test_serialize_subitem_value(self):
        from colander import null
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children=[inner]
        widget = self._makeOne()
        widget.serialize(field, null)
        self.assertEqual(renderer.kw['item_field'], inner)

    def test_serialize_not_null(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        result = widget.serialize(field, ['123'])
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 1)
        self.assertEqual(renderer.kw['subfields'][0], ('123', inner))
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], ['123'])
        self.assertEqual(renderer.template, widget.template)

    def test_serialize_not_null_readonly(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        inner = DummyField()
        field.children = [inner]
        widget = self._makeOne()
        result = widget.serialize(field, ['123'], readonly=True)
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 1)
        self.assertEqual(renderer.kw['subfields'][0], ('123', inner))
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], ['123'])
        self.assertEqual(renderer.template, widget.readonly_template)

    def test_serialize_with_sequence_widgets(self):
        renderer = DummyRenderer('abc')
        schema = DummySchema()
        field = DummyField(schema, renderer)
        widget = self._makeOne()
        inner = DummyField()
        field.children = [inner]
        sequence_field = DummyField()
        field.sequence_fields = [sequence_field]
        result = widget.serialize(field, ['123'])
        self.assertEqual(result, 'abc')
        self.assertEqual(len(renderer.kw['subfields']), 1)
        self.assertEqual(renderer.kw['subfields'][0], ('123', sequence_field))
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], ['123'])
        self.assertEqual(renderer.template, widget.template)

    def test_deserialize_null(self):
        from colander import null
        field = DummyField()
        inner_field = DummyField()
        field.children = [inner_field]
        widget = self._makeOne()
        result = widget.deserialize(field, null)
        self.assertEqual(result, [])
        self.assertEqual(field.sequence_fields, [])

    def test_deserialize_not_null(self):
        field = DummyField()
        inner_field = DummyField()
        inner_field.widget = DummyWidget()
        field.children = [inner_field]
        widget = self._makeOne()
        result = widget.deserialize(field, ['123'])
        self.assertEqual(result, ['123'])
        self.assertEqual(len(field.sequence_fields), 1)
        self.assertEqual(field.sequence_fields[0], inner_field)

    def test_deserialize_error(self):
        from colander import Invalid
        field = DummyField()
        inner_field = DummyField()
        inner_field.widget = DummyWidget(exc=Invalid(inner_field, 'wrong', 'a'))
        field.children = [inner_field]
        widget = self._makeOne()
        e = invalid_exc(widget.deserialize, field, ['123'])
        self.assertEqual(e.value, ['a'])
        self.assertEqual(e.children[0].value, 'a')

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
        widget.error = 'abc'
        field = DummyField()
        error = DummyInvalid()
        widget.handle_error(field, error)
        self.assertEqual(widget.error, 'abc')

class TestFormWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import FormWidget
        return FormWidget(**kw)

    def test_template(self):
        form = self._makeOne()
        self.assertEqual(form.template, 'form')

class TestTextAreaCSVWidget(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.widget import TextAreaCSVWidget
        return TextAreaCSVWidget(**kw)

    def test_serialize_null(self):
        from colander import null
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        widget.serialize(field, null)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], '')

    def test_serialize_with_unparseable(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        field = DummyField(None, renderer=renderer)
        field.unparseable = 'aloooo'
        widget.serialize(field, None)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'aloooo')

    def test_serialize_not_None(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = [('a', '1')]
        widget.serialize(field, cstruct)
        self.assertEqual(renderer.template, widget.template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'a,1\r\n')

    def test_serialize_not_None_readonly(self):
        widget = self._makeOne()
        renderer = DummyRenderer()
        schema = DummySchema()
        field = DummyField(schema, renderer=renderer)
        cstruct = [('a', '1')]
        widget.serialize(field, cstruct, readonly=True)
        self.assertEqual(renderer.template, widget.readonly_template)
        self.assertEqual(renderer.kw['field'], field)
        self.assertEqual(renderer.kw['cstruct'], 'a,1\r\n')

    def test_deserialize(self):
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = 'a,1\r\n'
        result = widget.deserialize(field, pstruct)
        self.assertEqual(result, [['a', '1']])

    def test_deserialize_bad_csv(self):
        import colander
        widget = self._makeOne(strip=False)
        field = DummyField()
        pstruct = 'a,1\raa\r\r\n\n'
        self.assertRaises(colander.Invalid, widget.deserialize, field, pstruct)
        self.assertEqual(field.unparseable, pstruct)

    def test_deserialize_null(self):
        from colander import null
        widget = self._makeOne(strip=False)
        schema = DummySchema()
        schema.required = False
        field = DummyField(schema=schema)
        result = widget.deserialize(field, null)
        self.assertEqual(result, null)

    def test_deserialize_emptystring(self):
        from colander import null
        widget = self._makeOne(strip=False)
        schema = DummySchema()
        schema.required = False
        field = DummyField(schema=schema)
        result = widget.deserialize(field, '')
        self.assertEqual(result, null)

    def test_handle_error_outermost_has_msg(self):
        widget = self._makeOne()
        error = DummyInvalid()
        error.msg = 'msg'
        field = DummyField()
        widget.handle_error(field, error)
        self.assertEqual(field.error, error)
        
    def test_handle_error_children_have_msgs(self):
        widget = self._makeOne()
        error = DummyInvalid()
        inner_error1 = DummyInvalid()
        inner_error1.msg = 'a'
        inner_error1.pos = 0
        inner_error2 = DummyInvalid()
        inner_error2.msg = 'b'
        inner_error2.pos = 1
        error.children = [ inner_error1, inner_error2 ]
        error.msg = None
        field = DummyField()
        field.schema = None
        widget.handle_error(field, error)
        self.assertEqual(field.error.msg, 'line 1: Invalid\nline 2: Invalid')

class DummyRenderer(object):
    def __init__(self, result=''):
        self.result = result

    def __call__(self, template, **kw):
        self.template = template
        self.kw = kw
        return self.result

class DummyWidget(object):
    name = 'name'
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
        return 'Invalid'

class DummyField(object):
    default = None
    error = None
    children = ()
    title = 'title'
    description = 'description'
    name = 'name'
    cloned = False
    def __init__(self, schema=None, renderer=None):
        self.schema = schema
        self.renderer = renderer

    def clone(self):
        self.cloned = True
        return self

    def deserialize(self, pstruct):
        return self.widget.deserialize(self, pstruct)

class DummyTmpStore(dict):
    def preview_url(self, uid):
        return 'preview_url'

class DummyUpload(object):
    file = 'fp'
    filename = 'filename'
    type = 'mimetype'
    length = 'size'

