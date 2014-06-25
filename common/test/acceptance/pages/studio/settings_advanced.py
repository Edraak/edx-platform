"""
Course Advanced Settings page
"""

from .course_page import CoursePage
from ...mixins.codemirror import CodeMirrorMixin
from ...mixins.studio_notifications import StudioNotificationsMixin


KEY_CSS = '.key input.policy-key'


class AdvancedSettingsPage(CoursePage, CodeMirrorMixin, StudioNotificationsMixin):
    """
    Course Advanced Settings page.
    """

    url_path = "settings/advanced"

    def is_browser_on_page(self):
        return self.q(css='body.advanced').present

    def _get_index_of(self, expected_key):
        for i, element in enumerate(self.q(css=KEY_CSS)):
            # Sometimes get stale reference if I hold on to the array of elements
            key = self.q(css=KEY_CSS)[i].get_attribute('value')
            if key == expected_key:
                return i

        return -1

    def save(self):
        self.press_the_notification_button("Save")

    def cancel(self):
        self.press_the_notification_button("Cancel")

    def set(self, key, new_value):
        index = self._get_index_of(key)
        self.type_in_codemirror(index, new_value)
        self.save()

    def get(self, key):
        index = self._get_index_of(key)
        return self.get_codemirror_value(index)
