from django.utils.translation import ugettext_noop

from courseware.tabs import EnrolledTab


class UniversityIDTab(EnrolledTab):
    """
    A course tab that links to the "University ID" view.
    """

    type = 'university_id'
    title = ugettext_noop('University ID')
    priority = None
    view_name = 'edraak_university.views.id_tab'
    is_default = True

    @classmethod
    def is_enabled(cls, course, user=None):
        # raise Exception('Hello it`s me')
        return True
        # return course.enable_university_id
