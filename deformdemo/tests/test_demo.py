# -*- coding: utf-8 -*-

import unittest

# to run:
# console 1: java -jar selenium-server.jar
# console 2: start the deform demo server (paster serve deformdemo.ini)
# console 3: python test_demo.py

# Instead of using -browserSessionReuse as an arg to
# selenium-server.jar to speed up tests, we rely on
# setUpModule/tearDownModule functionality.

browser = None

def setUpModule():
    from selenium import selenium
    global browser
    browser = selenium("localhost", 4444, "*chrome", "http://localhost:8521/")
    browser.start()
    return browser

def tearDownModule():
    browser.stop()

def _getFile(name):
    import os
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), name)
    filename = os.path.split(path)[-1]
    return path, filename

class CheckboxChoiceWidgetTests(unittest.TestCase):
    url = "/checkboxchoice/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Pepper"))
        self.failIf(browser.is_checked("deformField1-0"))
        self.failIf(browser.is_checked("deformField1-1"))
        self.failIf(browser.is_checked("deformField1-2"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_unchecked(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        self.failIf(browser.is_checked("deformField1-0"))
        self.failIf(browser.is_checked("deformField1-1"))
        self.failIf(browser.is_checked("deformField1-2"))
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_one_checked(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("deformField1-0")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_checked("deformField1-0"))
        self.assertEqual(browser.get_text('css=#captured'),
                         "{'pepper': set([u'habanero'])}")

    def test_submit_three_checked(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("deformField1-0")
        browser.click("deformField1-1")
        browser.click("deformField1-2")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_checked("deformField1-0"))
        self.failUnless(browser.is_checked("deformField1-1"))
        self.failUnless(browser.is_checked("deformField1-2"))
        target = browser.get_text('css=#captured')
        data = eval(target)
        self.assertEqual(data['pepper'],
                         set([u'habanero', u'jalapeno', u'chipotle']))

class CheckboxWidgetTests(unittest.TestCase):
    url = "/checkbox/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("I Want It!"))
        self.failIf(browser.is_checked("deformField1"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_unchecked(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_checked("deformField1"))
        self.assertEqual(browser.get_text('css=#captured'), "{'want': False}")

    def test_submit_checked(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("deformField1")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_checked("deformField1"))
        self.assertEqual(browser.get_text('css=#captured'), "{'want': True}")
    
class CheckedInputWidgetTests(unittest.TestCase):
    url = "/checkedinput/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Email Address"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_value('deformField1-confirm'), '')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_value('deformField1-confirm'), '')
        self.assertEqual(browser.get_text('css=#captured'), "None")

    def test_submit_invalid(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'this')
        browser.type('deformField1-confirm', 'this')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Invalid email address')
        self.assertEqual(browser.get_value('deformField1'), 'this')
        self.assertEqual(browser.get_value('deformField1-confirm'), 'this')
        self.assertEqual(browser.get_text('css=#captured'), "None")

    def test_submit_mismatch(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'this@example.com')
        browser.type('deformField1-confirm', 'that@example.com')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Fields did not match')
        self.assertEqual(browser.get_value('deformField1'), 'this@example.com')
        self.assertEqual(browser.get_value('deformField1-confirm'),
                         'that@example.com')
        self.assertEqual(browser.get_text('css=#captured'), "None")

    def test_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'user@example.com')
        browser.type('deformField1-confirm', 'user@example.com')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'), 'user@example.com')
        self.assertEqual(browser.get_value('deformField1-confirm'),
                         'user@example.com')
        self.assertEqual(browser.get_text('css=#captured'),
                         "{'email': u'user@example.com'}")

class CheckedPasswordWidgetTests(unittest.TestCase):
    url = "/checkedpassword/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Password"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_value('deformField1-confirm'), '')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(
            browser.get_attribute('css=#deformField1@type'),
            'password')
        self.assertEqual(
            browser.get_attribute('css=#deformField1-confirm@type'),
            'password')

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_value('deformField1-confirm'), '')
        self.assertEqual(browser.get_text('css=#captured'), "None")
        self.assertEqual(
            browser.get_attribute('css=#deformField1@type'),
            'password')
        self.assertEqual(
            browser.get_attribute('css=#deformField1-confirm@type'),
            'password')

    def test_submit_tooshort(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'this')
        browser.type('deformField1-confirm', 'this')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         'Shorter than minimum length 5')
        self.assertEqual(browser.get_value('deformField1'), 'this')
        self.assertEqual(browser.get_value('deformField1-confirm'), 'this')
        self.assertEqual(browser.get_text('css=#captured'), "None")
        self.assertEqual(
            browser.get_attribute('css=#deformField1@type'),
            'password')
        self.assertEqual(
            browser.get_attribute('css=#deformField1-confirm@type'),
            'password')

    def test_submit_mismatch(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'this123')
        browser.type('deformField1-confirm', 'that123')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         'Password did not match confirm')
        self.assertEqual(browser.get_value('deformField1'), 'this123')
        self.assertEqual(browser.get_value('deformField1-confirm'),
                         'that123')
        self.assertEqual(browser.get_text('css=#captured'), "None")
        self.assertEqual(
            browser.get_attribute('css=#deformField1@type'),
            'password')
        self.assertEqual(
            browser.get_attribute('css=#deformField1-confirm@type'),
            'password')

    def test_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'this123')
        browser.type('deformField1-confirm', 'this123')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'), 'this123')
        self.assertEqual(browser.get_value('deformField1-confirm'), 'this123')
        self.assertEqual(browser.get_text('css=#captured'),
                         "{'password': u'this123'}")
        self.assertEqual(
            browser.get_attribute('css=#deformField1@type'),
            'password')
        self.assertEqual(
            browser.get_attribute('css=#deformField1-confirm@type'),
            'password')

class DatePartsWidgetTests(unittest.TestCase):
    url = '/date/'
    def test_render_default(self):
        browser.open(self.url)
        self.failUnless(browser.is_text_present("Date"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_value('deformField1-month'), '')
        self.assertEqual(browser.get_value('deformField1-day'), '')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Incomplete')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_value('deformField1-month'), '')
        self.assertEqual(browser.get_value('deformField1-day'), '')
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_only_year(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '2010')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Incomplete')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '2010')
        self.assertEqual(browser.get_value('deformField1-month'), '')
        self.assertEqual(browser.get_value('deformField1-day'), '')
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_only_year_and_month(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '2010')
        browser.type('deformField1-month', '1')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Incomplete')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '2010')
        self.assertEqual(browser.get_value('deformField1-month'), '1')
        self.assertEqual(browser.get_value('deformField1-day'), '')
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_tooearly(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '2008')
        browser.type('deformField1-month', '1')
        browser.type('deformField1-day', '1')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         '2010-01-01 is earlier than earliest date 2008-01-01')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '2008')
        self.assertEqual(browser.get_value('deformField1-month'), '1')
        self.assertEqual(browser.get_value('deformField1-day'), '1')
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '2010')
        browser.type('deformField1-month', '1')
        browser.type('deformField1-day', '1')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#captured'),
                         "{'date': datetime.date(2010, 1, 1)}")
        self.assertEqual(browser.get_value('deformField1'), '2010')
        self.assertEqual(browser.get_value('deformField1-month'), '01')
        self.assertEqual(browser.get_value('deformField1-day'), '01')

class EditFormTests(unittest.TestCase):
    url = "/edit/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_element_present('css=#req-deformField1'))
        self.failUnless(browser.is_element_present('css=#req-deformField3'))
        self.failUnless(browser.is_element_present('css=#req-deformField4'))
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '42')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'number')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.assertEqual(browser.get_attribute('deformField3@name'), 'name')
        self.assertEqual(browser.get_value('deformField4'), '2010')
        self.assertEqual(browser.get_attribute('deformField4@name'), 'year')
        self.assertEqual(browser.get_value('deformField4-month'), '04')
        self.assertEqual(browser.get_attribute('deformField4-month@name'),
                         'month')
        self.assertEqual(browser.get_value('deformField4-day'), '09')
        self.assertEqual(browser.get_attribute('deformField4-day@name'),
                         'day')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField3'),
                         'Required')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField3', 'name')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failIf(browser.is_element_present('css=#error-deformField1'))
        self.failIf(browser.is_element_present('css=#error-deformField3'))
        self.failIf(browser.is_element_present('css=#error-deformField4'))
        self.assertEqual(browser.get_value('deformField1'), '42')
        self.assertEqual(browser.get_value('deformField3'), 'name')
        self.assertEqual(browser.get_value('deformField4'), '2010')
        self.assertEqual(browser.get_value('deformField4-month'), '04')
        self.assertEqual(browser.get_value('deformField4-day'), '09')
        self.assertEqual(
            browser.get_text('css=#captured'),
            (u"{'number': 42, 'mapping': {'date': datetime.date(2010, 4, 9), "
             "'name': u'name'}}"))

class MappingWidgetTests(unittest.TestCase):
    url = "/mapping/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_element_present('css=#req-deformField1'))
        self.failUnless(browser.is_element_present('css=#req-deformField3'))
        self.failUnless(browser.is_element_present('css=#req-deformField4'))
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'number')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.assertEqual(browser.get_attribute('deformField3@name'), 'name')
        self.assertEqual(browser.get_value('deformField4'), '')
        self.assertEqual(browser.get_attribute('deformField4@name'), 'year')
        self.assertEqual(browser.get_value('deformField4-month'), '')
        self.assertEqual(browser.get_attribute('deformField4-month@name'),
                         'month')
        self.assertEqual(browser.get_value('deformField4-day'), '')
        self.assertEqual(browser.get_attribute('deformField4-day@name'),
                         'day')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField1'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField3'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField4'),
                         'Incomplete')
        self.assertEqual(browser.get_text('css=#captured'),
                         'None')

    def test_submit_invalid_number(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'notanumber')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField1'),
                         '"notanumber" is not a number')
        self.assertEqual(browser.get_text('css=#error-deformField3'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField4'),
                         'Incomplete')
        self.assertEqual(browser.get_text('css=#captured'),
                         'None')

    def test_submit_invalid_date(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '1')
        browser.type('deformField3', 'name')
        browser.type('deformField4', 'year')
        browser.type('deformField4-month', 'month')
        browser.type('deformField4-day', 'day')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.failIf(browser.is_element_present('css=#error-deformField1'))
        self.failIf(browser.is_element_present('css=#error-deformField3'))
        self.assertEqual(browser.get_text('css=#error-deformField4'),
                         'Invalid date')
        self.assertEqual(browser.get_value('deformField1'), '1')
        self.assertEqual(browser.get_value('deformField3'), 'name')
        self.assertEqual(browser.get_value('deformField4'), 'year')
        self.assertEqual(browser.get_value('deformField4-month'), 'month')
        self.assertEqual(browser.get_value('deformField4-day'), 'day')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '1')
        browser.type('deformField3', 'name')
        browser.type('deformField4', '2010')
        browser.type('deformField4-month', '1')
        browser.type('deformField4-day', '1')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failIf(browser.is_element_present('css=#error-deformField1'))
        self.failIf(browser.is_element_present('css=#error-deformField3'))
        self.failIf(browser.is_element_present('css=#error-deformField4'))
        self.assertEqual(browser.get_value('deformField1'), '1')
        self.assertEqual(browser.get_value('deformField3'), 'name')
        self.assertEqual(browser.get_value('deformField4'), '2010')
        self.assertEqual(browser.get_value('deformField4-month'), '01')
        self.assertEqual(browser.get_value('deformField4-day'), '01')
        self.assertEqual(
            browser.get_text('css=#captured'),
            (u"{'number': 1, 'mapping': {'date': datetime.date(2010, 1, 1), "
             "'name': u'name'}}"))

class FieldDefaultTests(unittest.TestCase):
    url = "/fielddefaults/"
    def test_render_default(self):
        browser.open(self.url)
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failIf(browser.is_element_present('css=#req-deformField1'))
        self.failIf(browser.is_element_present('css=#req-deformField2'))
        self.failUnless(browser.is_element_present('css=#req-deformField3'))
        self.assertEqual(browser.get_value('deformField1'), 'Grandaddy')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'artist')
        self.assertEqual(browser.get_value('deformField2'),
                         'Just Like the Fambly Cat')
        self.assertEqual(browser.get_attribute('deformField2@name'), 'album')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.assertEqual(browser.get_attribute('deformField3@name'), 'song')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'), 'Grandaddy')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'artist')
        self.assertEqual(browser.get_value('deformField2'),
                         'Just Like the Fambly Cat')
        self.assertEqual(browser.get_attribute('deformField2@name'), 'album')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.assertEqual(browser.get_attribute('deformField3@name'), 'song')
        self.assertEqual(browser.get_text('css=#error-deformField3'),
                         'Required')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'abc')
        browser.type('deformField2', 'def')
        browser.type('deformField3', 'ghi')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'), 'abc')
        self.assertEqual(browser.get_value('deformField2'), 'def')
        self.assertEqual(browser.get_value('deformField3'), 'ghi')
        self.assertEqual(
            browser.get_text('css=#captured'),
            u"{'album': u'def', 'song': u'ghi', 'artist': u'abc'}")

class HiddenFieldWidgetTests(unittest.TestCase):
    url = "/hidden_field/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField1@name'), 'sneaky')
        self.assertEqual(browser.get_value('deformField1'), 'true')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
    
    def test_render_submitted(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField1@name'), 'sneaky')
        self.assertEqual(browser.get_value('deformField1'), 'true')
        self.assertEqual(browser.get_text('css=#captured'), "{'sneaky': True}")

class FileUploadTests(unittest.TestCase):
    url = "/file/"

    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_element_present('css=#req-deformField1'))
        self.assertEqual(browser.get_attribute('deformField1@name'), 'upload')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'upload')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_filled(self):
        # submit one first
        path, filename = _getFile('tests.py')
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', path)
        browser.click('submit')
        browser.wait_for_page_to_load("30000")

        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField1@name'), 'upload')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_text('css=#deformField1-filename'),
                         filename)
        uid = browser.get_value('css=#deformField1-uid')
        captured = browser.get_text('css=#captured')
        self.failUnless("'filename': u'%s" % filename in captured)
        self.failUnless(uid in captured)

        # resubmit without entering a new filename should not change the file
        browser.click('submit')
        browser.wait_for_page_to_load("30000")

        self.assertEqual(browser.get_value('css=#deformField1-uid'), uid)
        self.assertEqual(browser.get_text('css=#deformField1-filename'),
                         filename)

        # resubmit after entering a new filename should change the file
        path2, filename2 = _getFile('selenium.py')
        browser.type('deformField1', path2)
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('css=#deformField1-filename'),
                         filename2)
        captured = browser.get_text('css=#captured')
        self.failUnless("'filename': u'%s" % filename2 in captured)
        self.assertEqual(browser.get_value('css=#deformField1-uid'), uid)

class InterFieldValidationTests(unittest.TestCase):
    url=  "/interfield/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_element_present('css=#req-deformField1'))
        self.failUnless(browser.is_element_present('css=#req-deformField2'))
        self.assertEqual(browser.get_attribute('deformField1@name'), 'name')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_attribute('deformField2@name'), 'title')
        self.assertEqual(browser.get_value('deformField2'), '')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
    
    def test_submit_both_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        error_node2 = 'css=#error-deformField2'
        self.assertEqual(browser.get_text(error_node2), 'Required')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'name')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_attribute('deformField2@name'), 'title')
        self.assertEqual(browser.get_value('deformField2'), '')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_one_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'abc')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.failIf(browser.is_element_present('css=#error-deformField1'))
        error_node2 = 'css=#error-deformField2'
        self.assertEqual(browser.get_text(error_node2), 'Required')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'name')
        self.assertEqual(browser.get_value('deformField1'), 'abc')
        self.assertEqual(browser.get_attribute('deformField2@name'), 'title')
        self.assertEqual(browser.get_value('deformField2'), '')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_first_doesnt_start_with_second(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'abc')
        browser.type('deformField2', 'def')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.failIf(browser.is_element_present('css=#error-deformField1'))
        error_node2 = 'css=#error-deformField2'
        self.assertEqual(browser.get_text(error_node2),
                         'Must start with name abc')
        self.assertEqual(browser.get_attribute('deformField1@name'), 'name')
        self.assertEqual(browser.get_value('deformField1'), 'abc')
        self.assertEqual(browser.get_attribute('deformField2@name'), 'title')
        self.assertEqual(browser.get_value('deformField2'), 'def')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'abc')
        browser.type('deformField2', 'abcdef')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failIf(browser.is_element_present('css=#error-deformField1'))
        self.failIf(browser.is_element_present('css=#error-deformField2'))
        self.assertEqual(browser.get_attribute('deformField1@name'), 'name')
        self.assertEqual(browser.get_value('deformField1'), 'abc')
        self.assertEqual(browser.get_attribute('deformField2@name'), 'title')
        self.assertEqual(browser.get_value('deformField2'), 'abcdef')
        self.assertEqual(eval(browser.get_text('css=#captured')),
                         {'name': u'abc', 'title': u'abcdef'})

class InternationalizationTests(unittest.TestCase):
    url = "/i18n/"
    def test_render_default(self):
        browser.open(self.url)
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_element_present('css=#req-deformField1'))
        self.assertEqual(browser.get_attribute('deformField1@name'), 'number')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        label = browser.get_text('css=label')
        self.assertEqual(label, 'A number between 1 and 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, 'Submit')

    def test_render_en(self):
        browser.open("%s?_LOCALE_=en" % self.url)
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_element_present('css=#req-deformField1'))
        label = browser.get_text('css=label')
        self.assertEqual(label, 'A number between 1 and 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, 'Submit')
    
    def test_render_ru(self):
        browser.open("%s?_LOCALE_=ru" % self.url)
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_element_present('css=#req-deformField1'))
        label = browser.get_text('css=label')
        self.assertEqual(label, u'Число между 1 и 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, u'отправить')
    
    def test_submit_empty_en(self):
        browser.open("%s?_LOCALE_=en" % self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        errorMsgLbl = browser.get_text('css=.errorMsgLbl')
        errorMsg = browser.get_text('css=.errorMsg')
        self.assertEqual(errorMsgLbl,
                         'There was a problem with your submission')
        self.assertEqual(errorMsg, 'Errors have been highlighted below')
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        label = browser.get_text('css=label')
        self.assertEqual(label, 'A number between 1 and 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, 'Submit')

    def test_submit_empty_ru(self):
        browser.open("%s?_LOCALE_=ru" % self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        errorMsgLbl = browser.get_text('css=.errorMsgLbl')
        errorMsg = browser.get_text('css=.errorMsg')
        self.assertEqual(errorMsgLbl,
                         u'Данные которые вы предоставили содержат ошибку')
        self.assertEqual(errorMsg,
                         u'Ниже вы найдёте подробное описание ошибок')
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), u'требуется')
        label = browser.get_text('css=label')
        self.assertEqual(label, u'Число между 1 и 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, u'отправить')

    def test_submit_toolow_en(self):
        browser.open("%s?_LOCALE_=en" % self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '0')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        errorMsgLbl = browser.get_text('css=.errorMsgLbl')
        errorMsg = browser.get_text('css=.errorMsg')
        self.assertEqual(errorMsgLbl,
                         'There was a problem with your submission')
        self.assertEqual(errorMsg, 'Errors have been highlighted below')
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         '0 is less than minimum value 1')
        label = browser.get_text('css=label')
        self.assertEqual(label, 'A number between 1 and 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, 'Submit')

    def test_submit_toolow_ru(self):
        browser.open("%s?_LOCALE_=ru" % self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '0')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        errorMsgLbl = browser.get_text('css=.errorMsgLbl')
        errorMsg = browser.get_text('css=.errorMsg')
        self.assertEqual(errorMsgLbl,
                         u'Данные которые вы предоставили содержат ошибку')
        self.assertEqual(errorMsg,
                         u'Ниже вы найдёте подробное описание ошибок')
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         u'0 меньше чем 1')
        label = browser.get_text('css=label')
        self.assertEqual(label, u'Число между 1 и 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, u'отправить')

    def test_submit_toohigh_en(self):
        browser.open("%s?_LOCALE_en" % self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '11')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        errorMsgLbl = browser.get_text('css=.errorMsgLbl')
        errorMsg = browser.get_text('css=.errorMsg')
        self.assertEqual(errorMsgLbl,
                         'There was a problem with your submission')
        self.assertEqual(errorMsg, 'Errors have been highlighted below')
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         '11 is greater than maximum value 10')
        label = browser.get_text('css=label')
        self.assertEqual(label, 'A number between 1 and 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, 'Submit')

    def test_submit_toohigh_ru(self):
        browser.open("%s?_LOCALE_=ru" % self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '11')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        errorMsgLbl = browser.get_text('css=.errorMsgLbl')
        errorMsg = browser.get_text('css=.errorMsg')
        self.assertEqual(errorMsgLbl,
                         u'Данные которые вы предоставили содержат ошибку')
        self.assertEqual(errorMsg,
                         u'Ниже вы найдёте подробное описание ошибок')
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         u'11 больше чем 10')
        label = browser.get_text('css=label')
        self.assertEqual(label, u'Число между 1 и 10*')
        button = browser.get_text('css=button')
        self.assertEqual(button, u'отправить')

class PasswordWidgetTests(unittest.TestCase):
    url = "/password/"
    def test_render_default(self):
        browser.open(self.url)
        self.failUnless(browser.is_text_present("Password"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_attribute('css=#deformField1@type'),
                         'password')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
                         
    def test_render_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Password"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_attribute('css=#deformField1@type'),
                         'password')
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')

    def test_render_submit_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'abcdef123')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Password"))
        self.assertEqual(browser.get_text('css=#captured'),
                         "{'password': u'abcdef123'}")
        self.assertEqual(browser.get_value('deformField1'), 'abcdef123')
        self.assertEqual(browser.get_attribute('css=#deformField1@type'),
                         'password')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))

class RadioChoiceWidgetTests(unittest.TestCase):
    url = "/radiochoice/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Pepper"))
        self.failIf(browser.is_checked("deformField1-0"))
        self.failIf(browser.is_checked("deformField1-1"))
        self.failIf(browser.is_checked("deformField1-2"))
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_unchecked(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.get_text('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        self.failIf(browser.is_checked("deformField1-0"))
        self.failIf(browser.is_checked("deformField1-1"))
        self.failIf(browser.is_checked("deformField1-2"))
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_one_checked(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("deformField1-0")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.failUnless(browser.is_checked("deformField1-0"))
        self.assertEqual(browser.get_text('css=#captured'),
                         "{'pepper': u'habanero'}")

class ReadOnlySequenceOfMappingTests(unittest.TestCase):
    url = "/readonly_sequence_of_mappings/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField6'), 'name1')
        self.assertEqual(browser.get_text('deformField7'), '23')
        self.assertEqual(browser.get_text('deformField9'), 'name2')
        self.assertEqual(browser.get_text('deformField10'), '25')

class SequenceOfFileUploads(unittest.TestCase):
    url = "/sequence_of_fileuploads/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField1-addtext'), 'Add Upload')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_none_added(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField1-addtext'), 'Add Upload')
        self.assertEqual(browser.get_text('css=#captured'), "{'uploads': []}")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_two_unfilled(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd')
        browser.click('deformField1-seqAdd')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField3'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField4'),
                         'Required')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, 'None')

    def test_upload_one_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd')
        path, filename = _getFile('test_demo.py')
        browser.type("deformField3", path)
        browser.click("submit")
        browser.wait_for_page_to_load("30000")

        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField3@name'), 'upload')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename)
        uid = browser.get_value('css=#deformField3-uid')
        captured = browser.get_text('css=#captured')
        self.failUnless("'filename': u'%s" % filename in captured)
        self.failUnless(uid in captured)
    
    def test_upload_multi_interaction(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd')
        path, filename = _getFile('test_demo.py')
        browser.type("deformField3", path)
        browser.click("submit")
        browser.wait_for_page_to_load("30000")

        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField3@name'), 'upload')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename)
        uid = browser.get_value('css=#deformField3-uid')
        captured = browser.get_text('css=#captured')
        self.failUnless("'filename': u'%s" % filename in captured)
        self.failUnless(uid in captured)
    
        # resubmit without entering a new filename should not change the file
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_value('css=#deformField3-uid'), uid)
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename)

        # resubmit after entering a new filename should change the file
        path2, filename2 = _getFile('selenium.py')
        browser.type('deformField3', path2)
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename2)
        captured = browser.get_text('css=#captured')
        self.failUnless("'filename': u'%s" % filename2 in captured)
        self.assertEqual(browser.get_value('css=#deformField3-uid'), uid)

        # add a new file
        browser.click('deformField1-seqAdd')
        path, filename = _getFile('test_demo.py')
        browser.type("deformField4", path)
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename2)
        self.assertEqual(browser.get_text('css=#deformField4-filename'),
                         filename)
        captured = browser.get_text('css=#captured')
        uid2 = browser.get_value('css=#deformField4-uid')
        self.failUnless("'filename': u'%s" % filename2 in captured)
        self.failUnless("'filename': u'%s" % filename in captured)
        self.assertEqual(browser.get_value('css=#deformField3-uid'), uid)
        
        # resubmit should not change either file
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_value('css=#deformField3-uid'), uid)
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename2)
        self.assertEqual(browser.get_value('css=#deformField4-uid'), uid2)
        self.assertEqual(browser.get_text('css=#deformField4-filename'),
                         filename)

        # remove a file
        browser.click('deformField4-close')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_value('css=#deformField3-uid'), uid)
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename2)
        self.failIf(browser.is_element_present('css=#deformField4-uid'))
        captured = browser.get_text('css=#captured')
        self.failIf("'filename': u'%s" % filename in captured)

class SequenceOfFileUploadsWithInitialItem(unittest.TestCase):
    url = "/sequence_of_fileuploads_with_initial_item/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField1-addtext'), 'Add Upload')
        self.assertEqual(browser.get_attribute('deformField3@name'),
                         'upload')
        self.assertEqual(browser.get_attribute('deformField3@type'),
                         'file')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_none_added(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField3'),
                         'Required')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, 'None')

    def test_upload_one_success(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd')
        path, filename = _getFile('test_demo.py')
        browser.type("dom=document.forms[0].upload[0]", path)
        browser.type("dom=document.forms[0].upload[1]", path)
        browser.click("submit")
        browser.wait_for_page_to_load("30000")

        self.failIf(browser.is_element_present('css=.errorMsgLbl'))

        # first element present
        self.assertEqual(browser.get_attribute('deformField3@name'), 'upload')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.assertEqual(browser.get_text('css=#deformField3-filename'),
                         filename)
        uid = browser.get_value('css=#deformField3-uid')

        # second element present
        self.assertEqual(browser.get_attribute('deformField4@name'), 'upload')
        self.assertEqual(browser.get_value('deformField4'), '')
        self.assertEqual(browser.get_text('css=#deformField4-filename'),
                         filename)
        uid = browser.get_value('css=#deformField3-uid')

        # got some files
        captured = browser.get_text('css=#captured')
        self.failUnless("'filename': u'%s" % filename in captured)
        self.failUnless(uid in captured)

class SequenceOfMappings(unittest.TestCase):
    url = "/sequence_of_mappings/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.deformProto'))
        self.assertEqual(browser.get_text('deformField1-addtext'),'Add Person')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_none_added(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField1-addtext'),
                         'Add Person')
        self.assertEqual(browser.get_text('css=#captured'), "{'people': []}")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_two_unfilled(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd')
        browser.click('deformField1-seqAdd')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField6'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField7'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField9'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField10'),
                         'Required')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, 'None')

    def test_submit_complex_interaction(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd') # add one
        browser.type("name", 'name')
        browser.type("age", '23')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField6@name'), 'name')
        self.assertEqual(browser.get_value('deformField6'), 'name')
        self.assertEqual(browser.get_attribute('deformField7@name'), 'age')
        self.assertEqual(browser.get_value('deformField7'), '23')
        captured = browser.get_text('css=#captured')
        captured = eval(captured)
        self.assertEqual(captured,
                         {'people': [{'name': u'name', 'age': 23}]})

        browser.click('deformField1-seqAdd') # add another
        name1 = 'dom=document.forms[0].name[0]'
        age1 = 'dom=document.forms[0].age[0]'
        name2 = 'dom=document.forms[0].name[1]'
        age2 = 'dom=document.forms[0].age[1]'
        browser.type(name1, 'name-changed')
        browser.type(age1, '24')
        browser.type(name2, 'name2')
        browser.type(age2, '26')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField6@name'), 'name')
        self.assertEqual(browser.get_value('deformField6'), 'name-changed')
        self.assertEqual(browser.get_attribute('deformField7@name'), 'age')
        self.assertEqual(browser.get_value('deformField7'), '24')
        self.assertEqual(browser.get_attribute('deformField9@name'), 'name')
        self.assertEqual(browser.get_value('deformField9'), 'name2')
        self.assertEqual(browser.get_attribute('deformField10@name'), 'age')
        self.assertEqual(browser.get_value('deformField10'), '26')
        captured = browser.get_text('css=#captured')
        captured = eval(captured)

        self.assertEqual(
            captured,
            {'people': [{'name': u'name-changed', 'age': 24},
                        {'name': u'name2', 'age': 26}]})

        browser.click('deformField5-close') # remove the first mapping
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_attribute('deformField6@name'), 'name')
        self.assertEqual(browser.get_value('deformField6'), 'name2')
        self.assertEqual(browser.get_attribute('deformField7@name'), 'age')
        self.assertEqual(browser.get_value('deformField7'), '26')

        captured = browser.get_text('css=#captured')
        captured = eval(captured)

        self.assertEqual(
            captured,
            {'people': [{'name': u'name2', 'age': 26}]})


class SequenceOfMappingsWithInitialItem(unittest.TestCase):
    url = "/sequence_of_mappings_with_initial_item/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.deformProto'))
        self.assertEqual(browser.get_text('deformField1-addtext'),'Add Person')
        self.assertEqual(browser.get_attribute('css=#deformField6@name'),
                         'name')
        self.assertEqual(browser.get_attribute('css=#deformField7@name'),
                         'age')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_none_added(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField1-addtext'),
                         'Add Person')
        self.assertEqual(browser.get_text('css=#error-deformField6'),
                         'Required')
        self.assertEqual(browser.get_text('css=#error-deformField7'),
                         'Required')
        self.assertEqual(browser.get_text('css=#captured'), "None")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_add_one(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd')
        browser.type("dom=document.forms[0].name[0]", 'name0')
        browser.type("dom=document.forms[0].age[0]", '23')
        browser.type("dom=document.forms[0].name[1]", 'name1')
        browser.type("dom=document.forms[0].age[1]", '25')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField1-addtext'),
                         'Add Person')
        self.assertEqual(browser.get_attribute('css=#deformField6@name'),
                         'name')
        self.assertEqual(browser.get_attribute('css=#deformField6@value'),
                         'name0')
        self.assertEqual(browser.get_attribute('css=#deformField7@name'),
                         'age')
        self.assertEqual(browser.get_attribute('css=#deformField7@value'),
                         '23')
        self.assertEqual(browser.get_attribute('css=#deformField9@name'),
                         'name')
        self.assertEqual(browser.get_attribute('css=#deformField9@value'),
                         'name1')
        self.assertEqual(browser.get_attribute('css=#deformField10@name'),
                         'age')
        self.assertEqual(browser.get_attribute('css=#deformField10@value'),
                         '25')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        captured = browser.get_text('css=#captured')
        self.assertEqual(eval(captured),
                         {'people': [{'name': u'name0', 'age': 23},
                                     {'name': u'name1', 'age': 25}]}
                         )

class SelectWidgetTests(unittest.TestCase):
    url = "/select/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Pepper"))
        self.assertEqual(browser.get_attribute("deformField1@name"), 'pepper')
        self.assertEqual(browser.get_selected_index('deformField1'), '0')
        options = browser.get_select_options('deformField1')
        self.assertEqual(
            options,
            [u'- Select -', u'Habanero', u'Jalapeno', u'Chipotle']) 
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Pepper"))
        self.assertEqual(browser.get_attribute("deformField1@name"), 'pepper')
        self.assertEqual(browser.get_selected_index('deformField1'), '0')
        self.assertEqual(browser.get_text('css=#error-deformField1'),
                         'Required')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, 'None')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_selected(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.select('deformField1', 'index=1')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_selected_index('deformField1'), '1')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, "{'pepper': u'habanero'}")

class TextInputWidgetTests(unittest.TestCase):
    url = "/textinput/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Text"))
        self.assertEqual(browser.get_attribute("deformField1@name"), 'text')
        self.assertEqual(browser.get_attribute("deformField1@type"), 'text')
        self.assertEqual(browser.get_value("deformField1"), '')
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField1'),
                         'Required')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, 'None')

    def test_submit_filled(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'hello')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'), 'hello')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, "{'text': u'hello'}")

class TextAreaWidgetTests(unittest.TestCase):
    url = "/textarea/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Text"))
        self.assertEqual(browser.get_attribute("deformField1@name"), 'text')
        self.assertEqual(browser.get_attribute("deformField1@rows"), '10')
        self.assertEqual(browser.get_attribute("deformField1@cols"), '60')
        self.assertEqual(browser.get_value("deformField1"), '')
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_text('css=#error-deformField1'),
                         'Required')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, 'None')

    def test_submit_filled(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'hello')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'), 'hello')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, "{'text': u'hello'}")

class UnicodeEverywhereTests(unittest.TestCase):
    url = "/unicodeeverywhere/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        description=(u"子曰：「學而時習之，不亦說乎？有朋自遠方來，不亦樂乎？ "
                     u"人不知而不慍，不亦君子乎？」")

        self.failUnless(browser.is_text_present(u"По оживлённым берегам"))
        self.assertEqual(browser.get_attribute("item-deformField1@title"),
                         description)
        self.assertEqual(browser.get_attribute("css=label@title"),
                         description)
        self.assertEqual(browser.get_attribute("deformField1@name"), 'field')
        self.assertEqual(browser.get_value("deformField1"), u'☃')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'), u'☃')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, u"{'field': u'\\u2603'}")

class SequenceOfSequences(unittest.TestCase):
    url = "/sequence_of_sequences/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_text('deformField1-addtext'),
                         'Add Names and Titles')
        self.assertEqual(browser.get_text('deformField6-addtext'),
                         'Add Name and Title')
        self.assertEqual(browser.get_value('deformField21'), '')
        self.assertEqual(browser.get_value('deformField22'), '')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_add_two(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('deformField1-seqAdd')
        browser.click('deformField6-seqAdd')
        browser.type('dom=document.forms[0].name[0]', 'name')
        browser.type('dom=document.forms[0].title[0]', 'title')
        browser.type('dom=document.forms[0].name[1]', 'name')
        browser.type('dom=document.forms[0].title[1]', 'title')
        browser.type('dom=document.forms[0].name[2]', 'name')
        browser.type('dom=document.forms[0].title[2]', 'title')
        browser.click("submit")
        browser.wait_for_page_to_load("30000")
        captured = eval(browser.get_text('css=#captured'))
        self.assertEqual(captured,
                         {'names_and_titles_sequence': [
                             [{'name': u'name', 'title': u'title'},
                              {'name': u'name', 'title': u'title'}],
                             [{'name': u'name', 'title': u'title'}]]}
                         )

class TextAreaCSVWidgetTests(unittest.TestCase):
    url = "/textareacsv/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_text_present("Csv"))
        self.assertEqual(browser.get_attribute("deformField1@name"), 'csv')
        self.assertEqual(browser.get_attribute("deformField1@rows"), '10')
        self.assertEqual(browser.get_attribute("deformField1@cols"), '60')
        self.assertEqual(browser.get_value("deformField1"),
                         '1,hello,4.5\n2,goodbye,5.5')
        self.assertEqual(browser.get_text('css=.req'), '*')
        self.assertEqual(browser.get_text('css=#captured'), 'None')

    def test_submit_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))
        self.assertEqual(browser.get_value('deformField1'),
                         '1,hello,4.5\n2,goodbye,5.5')
        captured = browser.get_text('css=#captured')
        self.assertEqual(
            captured,
            (u'{\'csv\': [(1, u\'hello\', Decimal("4.5")), '
            u'(2, u\'goodbye\', Decimal("5.5"))]}'))

    def test_submit_line_error(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '1,2,3\nwrong')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node),
                         ('line 2: {\'1\': u\'"[\\\'wrong\\\']" has an '
                          'incorrect number of elements (expected 3, was 1)\'}')
                         )
        self.assertEqual(browser.get_value('deformField1'), '1,2,3\nwrong')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, "None")

    def test_submit_empty(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', '')
        browser.click('submit')
        browser.wait_for_page_to_load("30000")
        self.failUnless(browser.is_element_present('css=.errorMsgLbl'))
        error_node = 'css=#error-deformField1'
        self.assertEqual(browser.get_text(error_node), 'Required')
        self.assertEqual(browser.get_value('deformField1'), '')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, "None")

class WidgetAdapterTests(TextAreaCSVWidgetTests):
    url = "/widget_adapter/"

class MultipleFormsTests(unittest.TestCase):
    url = "/multiple_forms/"
    def test_render_default(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_attribute("deformField1@name"), 'name1')
        self.assertEqual(browser.get_value('deformField1'), '')
        self.assertEqual(browser.get_attribute("deformField3@name"), 'name2')
        self.assertEqual(browser.get_value('deformField3'), '')
        self.failIf(browser.is_element_present('css=.errorMsgLbl'))

    def test_submit_first(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField1', 'hey')
        browser.click('form1submit')
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_value('deformField1'), 'hey')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, u"{'name1': u'hey'}")

    def test_submit_second(self):
        browser.open(self.url)
        browser.wait_for_page_to_load("30000")
        browser.type('deformField3', 'hey')
        browser.click('form2submit')
        browser.wait_for_page_to_load("30000")
        self.assertEqual(browser.get_value('deformField3'), 'hey')
        captured = browser.get_text('css=#captured')
        self.assertEqual(captured, u"{'name2': u'hey'}")

if __name__ == '__main__':
    setUpModule()
    try:
        unittest.main()
    finally:
        tearDownModule()
