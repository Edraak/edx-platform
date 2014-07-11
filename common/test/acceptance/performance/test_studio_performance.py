"""
Single page performance tests for Studio.
"""
from bok_choy.performance import WebAppPerfReport, with_cache
from ..pages.studio.login import LoginPage
from ..pages.studio.signup import SignupPage


class StudioPagePerformanceTest(WebAppPerfReport):
    """
    Example test case.
    """

    @with_cache
    def test_signup_flow_with_cache(self):
        """
        Produce a report for the login --> signup page performance.

        This example will produde two har files. The first will show the performance
        of the flow when it starts from a browser with an empty cache. The second (which
        with have '_cached_2' on the end of the file name), will show the performance when
        the browser has already been through the flow once before and has cached some assets.
        """
        # Declaring a new page will instatiate a new har instance if one hasn't been already.
        self.new_page('LoginPage')

        login_page = LoginPage(self.browser)
        login_page.visit()

        # Declare that you are going to a new page first, then navigate to the next page.
        self.new_page('SignupPage')
        signup_page = SignupPage(self.browser)
        signup_page.visit()

        # Save the har file, passing it a name for the file
        self.save_har('LoginPage_and_SignupPage')

    def test_signup_flow_no_cache(self):
        """
        Produce a report for the login --> signup page performance.

        This example will produde two har files. The first will show the performance
        of the LoginPage when it starts from a browser with an empty cache. The second will show
        the performance of the SignUp page when the browser has already been to the LoginPage
        and has cached some assets.
        """

        self.new_page('LoginPage')
        login_page = LoginPage(self.browser)
        login_page.visit()

        # Save the first har file.
        # Note that saving will 'unset' the har, so that if you were to declare another new
        # page after this point, it would start recording a new har. This means that you can
        # also explitily capture many hars in a single test. See the next example.
        self.save_har('LoginPage')

        # Declare that you are going to a new page, then navigate to the next page.
        # This will start recording a new har here.
        self.new_page('SignupPage')
        signup_page = SignupPage(self.browser)
        signup_page.visit()
        # Save the second har file.
        self.save_har('SignupPage')
