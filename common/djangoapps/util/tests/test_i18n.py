# -*- coding: utf-8 -*-

import unittest
from mock import patch

from django.utils.translation import override as override_lang
from django.utils.translation import ugettext_noop

from util.i18n import force_translate


class I18NUtilsTest(unittest.TestCase):
    def test_happy_scenario(self):
        value = 'Submit'

        with override_lang('eo'):
            with patch('util.i18n.ugettext') as patched_ugettext:
                result = force_translate(
                    value,
                    ugettext_noop('Submit'),
                    ugettext_noop('Cancel'),
                )

        self.assertNotEqual(value, unicode(result))
        patched_ugettext.assert_called_once_with('Submit')

    @patch('django.utils.translation.ugettext')
    def test_not_in_the_list(self, patched_ugettext):
        value = 'Submit'

        with override_lang('eo'):
            with patch('util.i18n.ugettext') as patched_ugettext:
                force_translate(
                    value,
                    ugettext_noop('Name'),
                    ugettext_noop('Cancel'),
                )

        self.assertFalse(patched_ugettext.called, 'ugettext should not be called!')

        result = force_translate(
            value,
            ugettext_noop('Name'),
            ugettext_noop('Cancel'),
        )

        self.assertEqual(value, result)
