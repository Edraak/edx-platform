"""
Acceptance tests for Studio.
"""

import json

from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.studio.settings_advanced import AdvancedSettingsPage
from ..pages.studio.settings_group_configurations import GroupConfigurationsPage
from ..fixtures.course import CourseFixture
from xmodule.partitions.partitions import Group, UserPartition

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
        link_css = 'li.nav-course-settings-group-configurations a'
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
        link_css = 'li.nav-course-settings-group-configurations a'
        self.advanced_settings.set('advanced_modules', '[]')
        self.browser.refresh()
        self.advanced_settings.wait_for_page()
        self.assertFalse(self.advanced_settings.q(css=link_css).present)


class GroupConfigurationsTest(UniqueCourseTest):
    """
    Tests that Group Configurations page works correctly with previously
    added configurations in Studio
    """

    def setUp(self):
        super(GroupConfigurationsTest, self).setUp()

        course_fix = CourseFixture(**self.course_info)
        course_fix.add_advanced_settings({
            u"advanced_modules": ["split_test"],
        })

        course_fix.install()
        self.course_fix = course_fix
        self.user = course_fix.user

        self.auth_page = AutoAuthPage(
            self.browser,
            staff=False,
            username=course_fix.user.get('username'),
            email=course_fix.user.get('email'),
            password=course_fix.user.get('password')
        )
        self.auth_page.visit()

        self.page = GroupConfigurationsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

    def test_is_empty(self):
        """
        Ensure that message telling me to create a new group configuration is
        shown when group configurations were not added.
        """
        self.page.visit()
        css = ".wrapper-content .no-group-configurations-content"
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
        self.course_fix.add_advanced_settings({
            u"user_partitions": [
                UserPartition(0, 'Name of the Group Configuration', 'Description of the group configuration.', [Group("0", 'Group 0'), Group("1", 'Group 1')]).to_json(),
                UserPartition(1, 'Name of second Group Configuration', 'Second group configuration.', [Group("0", 'Alpha'), Group("1", 'Beta'), Group("2", 'Gamma')]).to_json()
            ],
        })
        self.course_fix._add_advanced_settings()

        self.page.visit()

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
