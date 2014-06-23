"""
Course Group Configurations page.
"""

from .course_page import CoursePage


class ExperimentsPage(CoursePage):
    """
    Course Group Configurations page.
    """

    url_path = "settings/group_experiments"

    def is_browser_on_page(self):
        return self.q(css='body.group-experiments').present
