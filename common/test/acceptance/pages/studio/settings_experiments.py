"""
Course Group Configurations page.
"""

from .course_page import CoursePage


class ExperimentsPage(CoursePage):
    """
    Course Group Configurations page.
    """

    url_path = "group_experiments"

    def is_browser_on_page(self):
        return self.q(css='body.group-experiments').present

    def group_configurations(self):
        """
        Returns list of the group configurations for the course.
        """
        css = '.wrap-group-experiment'
        parent = self.q(css='body.group-experiments')[0]
        return [GroupConfiguration(parent, index) for index in xrange(len(self.q(css=css)))]


class GroupConfiguration(object):
    """
    Group Configuration wrapper.
    """
    SELECTOR = '.wrap-group-experiment'

    def __init__(self, parent, index):
        self.index = index
        self.parent = parent
        self.element = self.get_element()

    def find_css(self, selector, parent=None):
        """
        Find elements as defined by css locator.

        This method will return a list of WebDriverElements.
        """
        element = parent or self.element
        return element.find_elements_by_css_selector(selector)

    def get_element(self):
        """
        Returns the element.
        """
        return self.find_css(self.SELECTOR, parent=self.parent)[self.index]

    def toggle(self):
        """
        Expand/collapse group configuration.
        """
        css = 'a.group-toggle'
        self.find_css(css)[0].click()
        self.element = self.get_element()

    @property
    def id(self):
        """
        Returns group configuration id.
        """
        css = '.group-experiment-id .group-experiment-value'
        return self.find_css(css)[0].text

    @property
    def name(self):
        """
        Returns group configuration name.
        """
        css = '.group-experiment-title'
        return self.find_css(css)[0].text

    @property
    def description(self):
        """
        Returns group configuration description.
        """
        css = '.group-experiment-description'
        return self.find_css(css)[0].text

    @property
    def groups(self):
        """
        Returns list of groups.
        """
        css = '.group'
        return [Group(group) for group in self.find_css(css)]

    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.name)


class Group(object):
    """
    Group wrapper.
    """
    def __init__(self, element):
        self.element = element

    def find_css(self, selector):
        """
        Find elements as defined by css locator.

        This method will return a list of WebDriverElements.
        """
        return self.element.find_elements_by_css_selector(selector)

    @property
    def name(self):
        """
        Returns group name.
        """
        css = '.group-name'
        return self.find_css(css)[0].text

    @property
    def percent(self):
        """
        Returns percent for the group.
        """
        css = '.group-percent'
        return self.find_css(css)[0].text

    def __repr__(self):
        return "<%s:%s>" % (self.__class__.__name__, self.name)
