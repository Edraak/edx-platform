"""
Acceptance tests for Studio.
"""

import json

from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.studio.settings_advanced import AdvancedSettingsPage
from ..pages.studio.settings_experiments import ExperimentsPage
from ..fixtures.course import CourseFixture

from .helpers import UniqueCourseTest


class SettingsMenuTest(UniqueCourseTest):
    """
    Tests that Setting menu is rendered correctly in Studio
    """

    def setUp(self):
        super(SettingsMenuTest, self).setUp()

        course_fix = CourseFixture(**self.course_info)
        course_fix.install()

        self.auth_page = AutoAuthPage(
            self.browser,
            staff=False,
            username=course_fix.user.get('username'),
            email=course_fix.user.get('email'),
            password=course_fix.user.get('password')
        )
        self.auth_page.visit()

        self.advanced_settings = AdvancedSettingsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )
        self.advanced_settings.visit()

    def test_link_exist_if_split_test_enabled(self):
        """
        Ensure that the link to the "Group Configurations" page is shown in the
        Settings menu.
        """
        link_css = 'li.nav-course-settings-experiments a'
        self.assertFalse(self.advanced_settings.q(css=link_css).present)

        self.advanced_settings.set('advanced_modules', '["split_test"]')

        self.browser.refresh()
        self.advanced_settings.wait_for_page()

        self.assertIn(
            "split_test",
            json.loads(self.advanced_settings.get('advanced_modules')),
        )

        self.assertTrue(self.advanced_settings.q(css=link_css).present)

    def test_link_does_not_exist_if_split_test_disabled(self):
        """
        Ensure that the link to the "Group Configurations" page does not exist
        in the Settings menu.
        """
        link_css = 'li.nav-course-settings-experiments a'
        self.advanced_settings.set('advanced_modules', '[]')
        self.browser.refresh()
        self.advanced_settings.wait_for_page()
        self.assertFalse(self.advanced_settings.q(css=link_css).present)


class GroupExperimentsTest(UniqueCourseTest):
    """
    Tests that Group Configurations page works correctly in Studio
    """

    def setUp(self):
        super(GroupExperimentsTest, self).setUp()

        course_fix = CourseFixture(**self.course_info)
        course_fix.install()

        self.auth_page = AutoAuthPage(
            self.browser,
            staff=False,
            username=course_fix.user.get('username'),
            email=course_fix.user.get('email'),
            password=course_fix.user.get('password')
        )
        self.auth_page.visit()

        self.advanced_settings = AdvancedSettingsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        self.page = ExperimentsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        self.advanced_settings.visit()
        self._enable_split_test()
        self.page.visit()

    def _enable_split_test(self):
        """
        Enables "split_test" module in advanced settings.
        """
        self.advanced_settings.set('advanced_modules', '["split_test"]')

    def _set_advanced_settings(self, values):
        """
        Sets advanced settings to the course.

        Arguments:
            values (dict): dictionary where key is setting name and value is value
            that needs to be set.
        """
        self.advanced_settings.visit()
        for key, value in values.items():
            self.advanced_settings.set(key, value)
        self.page.visit()

    def test_is_empty(self):
        """
        Ensure that message telling me to create a new group configuration is
        shown when group configurations were not added.
        """
        css = ".wrapper-content .no-group-experiments-content"
        self.assertTrue(self.page.q(css=css).present)
        self.assertIn(
            "You haven't created any group configurations yet.",
            self.page.q(css=css).text[0]
        )

    def test_configuration_exist(self):
        """
        Ensure that the group configuration is rendered correctly in
        expanded/collapsed mode.
        """
        self._set_advanced_settings({
            'user_partitions': '''[
                {
                    "description": "Description of the group configuration.",
                    "version": 1,
                    "id": 0,
                    "groups": [
                        {
                            "version": 1,
                            "id": 0,
                            "name": "Group 1"
                        },
                        {
                            "version": 1,
                            "id": 1,
                            "name": "Group 2"
                        }
                    ],
                    "name": "Name of the Group Configuration"
                },
                {
                    "description": "Second group configuration.",
                    "version": 1,
                    "id": 1,
                    "groups": [
                        {
                            "version": 1,
                            "id": 2,
                            "name": "Alpha"
                        },
                        {
                            "version": 1,
                            "id": 3,
                            "name": "Beta"
                        },
                        {
                            "version": 1,
                            "id": 4,
                            "name": "Gamma"
                        }

                    ],
                    "name": "Name of second Group Configuration"
                }

            ]''',
        })
        config = self.page.group_configurations()[0]
        self.assertIn("Name of the Group Configuration", config.name)
        self.assertEqual(config.id, '0')
        config.toggle()
        self.assertIn("Description of the group configuration.", config.description)
        self.assertEqual(len(config.groups), 2)

        config = self.page.group_configurations()[1]
        self.assertIn("Name of second Group Configuration", config.name)
        self.assertEqual(len(config.groups), 0)  # no groups when the partition is collapsed
        config.toggle()
        self.assertEqual(len(config.groups), 3)
        self.assertEqual("Beta", config.groups[1].name)
