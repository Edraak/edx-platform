from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView

from opaque_keys.edx.locator import CourseLocator
from xmodule.modulestore.django import modulestore

from student.models import UserProfile

from forms import UniversityIDForm
from models import UniversityID

class UniversityIDView(FormView):
    template_name = 'edraak_university/university_id.html'
    form_class = UniversityIDForm

    def get_form_kwargs(self):
        kwargs = super(UniversityIDView, self).get_form_kwargs()
        instance = self.get_instance()
        if instance:
            kwargs['instance'] = instance

        return kwargs

    def get_initial(self):
        user_profile = UserProfile.objects.get(user=self.request.user)

        return {
            'full_name': user_profile.name,
        }

    def get_instance(self):
        try:
            return UniversityID.objects.get(
                user=self.request.user,
                course_key=CourseLocator.from_string(self.kwargs['course_id']),
            )
        except UniversityID.DoesNotExist:
            return None

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.course_key = self.get_course().id
        instance.save()

        return super(UniversityIDView, self).form_valid(form)

    def get_success_url(self):
        return reverse('edraak_university_id_success', kwargs={
            'course_id': self.kwargs['course_id'],
        })

    def get_course(self):
        course_key = CourseLocator.from_string(self.kwargs['course_id'])
        return modulestore().get_course(course_key)

    def get_context_data(self, **kwargs):
        return {
            'course': self.get_course(),
            'form': self.get_form(),
            'has_valid_information': bool(self.get_instance()),
        }


# Comply with the openedx.course_tab functionality
university_id = UniversityIDView.as_view()


class UniversityIDSuccessView(TemplateView):
    template_name = 'edraak_university/university_id_success.html'

    def get_context_data(self, **kwargs):
        course_key = CourseLocator.from_string(self.kwargs['course_id'])

        return {
            'course': modulestore().get_course(course_key),
        }
