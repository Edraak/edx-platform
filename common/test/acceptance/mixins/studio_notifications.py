class StudioNotificationsMixin(object):
    """Adds convenient methods to work with notifications in Studio"""

    def press_the_notification_button(self, name):
        # Because the notification uses a CSS transition,
        # Selenium will always report it as being visible.
        # This makes it very difficult to successfully click
        # the "Save" button at the UI level.
        # Instead, we use JavaScript to reliably click
        # the button.
        btn_css = 'div#page-notification a.action-%s' % name.lower()
        self.browser.execute_script("$('{}').focus().click()".format(btn_css))
        self.wait_for_ajax()
