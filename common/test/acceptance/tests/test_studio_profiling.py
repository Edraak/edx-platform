"""
Acceptance tests for Studio.
"""

from bok_choy.web_app_test import WebAppTest

from ..pages.studio.howitworks import HowitworksPage
from ..pages.studio.login import LoginPage
from ..pages.studio.signup import SignupPage

from textwrap import dedent


class LoggedOutTest(WebAppTest):
    """
    Smoke test for pages in Studio that are visible when logged out.
    """

    def setUp(self):
        super(LoggedOutTest, self).setUp()
        self.pages = [LoginPage(self.browser), HowitworksPage(self.browser), SignupPage(self.browser)]

    def test_page_existence(self):
        """
        Make sure that all the pages are accessible.
        Rather than fire up the browser just to check each url,
        do them all sequentially in this testcase.
        """
        script = dedent("""
            var performance = window.performance || {};
            var timings = performance.timing || {};
            return timings;
        """)

        for page in self.pages:
            # Start up a new HAR file
            self.proxy.new_har(ref=page.url, options={'captureContent': True})

            # Visit the page
            page.visit()

            # Get the har contents from the proxy
            har = self.proxy.har

            # Capture the timings from the browser via javascript
            # TODO: add these timings to the har json before saving the HAR file
            timings = self.browser.execute_script(script)

            # TODO: better naming convention for the output file
            self.save_har_file(har, '{}{}'.format(self.id(), self.unique_id))
