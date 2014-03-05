import unittest

from mock import Mock

from xblock.field_data import DictFieldData
from xmodule.html_module import HtmlModule

from . import get_test_system


class HtmlModuleSubstitutionTestCase(unittest.TestCase):
    descriptor = Mock()

    def test_substitution_works(self):
        sample_xml = '''%%USER_ID%%'''
        field_data = DictFieldData({'data': sample_xml})
        module_system = get_test_system()
        module = HtmlModule(self.descriptor, module_system, field_data, Mock())
        self.assertEqual(module.get_html(), str(module_system.anonymous_student_id))

    def test_substitution_without_magic_string(self):
        sample_xml = '''
            <html>
                <p>Hi USER_ID!11!</p>
            </html>
        '''
        field_data = DictFieldData({'data': sample_xml})
        module_system = get_test_system()
        module = HtmlModule(self.descriptor, module_system, field_data, Mock())
        self.assertEqual(module.get_html(), sample_xml)

    def test_substitution_without_anonymous_student_id(self):
        sample_xml = '''%%USER_ID%%'''
        field_data = DictFieldData({'data': sample_xml})
        module_system = get_test_system()
        module_system.anonymous_student_id = None
        module = HtmlModule(self.descriptor, module_system, field_data, Mock())
        self.assertEqual(module.get_html(), sample_xml)


class HtmlModuleStripTagsTestCase(unittest.TestCase):
    def test_remove_events(self):
        sample_xml = '''
            <html>
                <a onclick="alert('hi')" href="/somewhere">elt1</a>
                <div onblur  =  "alert('hi')" >elt2</div>
                <div oNbLur="alert('hi')" >elt3</div>
                <div ONMOUSEOVER
                    ="alert('hi')" >elt4</div>
                <div rel="findme">
                    <div data-onclick="javascript:foo()">elt5</div>
                </div>
            </html>
        '''
        field_data = DictFieldData({'data': sample_xml})
        module_system = get_test_system()
        module = HtmlModule(Mock(), module_system, field_data, Mock())
        html = module.get_html()
        self.assertNotIn('alert', html)
        self.assertIn('href="/somewhere"', html)
        self.assertIn('elt4', html)
        self.assertIn('data-onclick="javascript:foo()"', html)
        self.assertIn('rel="findme"', html)
