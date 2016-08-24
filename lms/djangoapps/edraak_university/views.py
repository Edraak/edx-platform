from edxmako.shortcuts import render_to_response

from django.views.generic.edit import FormView

from opaque_keys.edx import locator
from xmodule.modulestore.django import modulestore

from forms import UniversityIDForm


class UniversityIDView(FormView):
    template_name = 'edraak_university/university_id.html'
    form_class = UniversityIDForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.student = self.request.user
        instance.course_key = self.get_course().id
        return super(UniversityIDView, self).form_valid(form)

    def get_course(self):
        course_key = locator.CourseLocator.from_string(self.kwargs['course_id'])
        return modulestore().get_course(course_key)

    def get_context_data(self, **kwargs):
        return {
            'course': self.get_course(),
        }


# Comply with the openedx.course_tab functionality
university_id = UniversityIDView.as_view()
