"""
Course Advanced Settings page
"""

from .course_page import CoursePage


KEY_CSS = '.key input.policy-key'


class AdvancedSettingsPage(CoursePage):
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

    def _type_in_codemirror(self, index, text, find_prefix="$"):
        script = """
        var cm = {find_prefix}('div.CodeMirror:eq({index})').get(0).CodeMirror;
        CodeMirror.signal(cm, "focus", cm);
        cm.setValue(arguments[0]);
        CodeMirror.signal(cm, "blur", cm);""".format(index=index, find_prefix=find_prefix)
        self.browser.execute_script(script, str(text))
        self.wait_for_ajax()

    def _get_codemirror_value(self, index=0, find_prefix="$"):
        return self.browser.execute_script(
            """
            return {find_prefix}('div.CodeMirror:eq({index})').get(0).CodeMirror.getValue();
            """.format(index=index, find_prefix=find_prefix)
        )

    def _press_the_notification_button(self, name):
        # Because the notification uses a CSS transition,
        # Selenium will always report it as being visible.
        # This makes it very difficult to successfully click
        # the "Save" button at the UI level.
        # Instead, we use JavaScript to reliably click
        # the button.
        btn_css = 'div#page-notification a.action-%s' % name.lower()
        self.browser.execute_script("$('{}').focus().click()".format(btn_css))
        self.wait_for_ajax()

    def save(self):
        self._press_the_notification_button("Save")

    def cancel(self):
        self._press_the_notification_button("Cancel")

    def set(self, key, new_value):
        index = self._get_index_of(key)
        self._type_in_codemirror(index, new_value)
        self.save()
        self.wait_for_ajax()

    def get(self, key):
        index = self._get_index_of(key)
        return self._get_codemirror_value(index)
