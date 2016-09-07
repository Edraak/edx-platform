from django.core.urlresolvers import reverse
from django.views.generic import FormView, TemplateView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from util.views import ensure_valid_course_key
from opaque_keys.edx.locator import CourseLocator
from courseware.courses import get_course_with_access

from student.models import UserProfile

from forms import UniversityIDForm

from helpers import get_university_id, has_valid_university_id


class UniversityIDView(FormView):
    template_name = 'edraak_university/university_id.html'
    form_class = UniversityIDForm

    def get_form_kwargs(self):
        kwargs = super(UniversityIDView, self).get_form_kwargs()
        instance = get_university_id(self.request.user, self.kwargs['course_id'])
        if instance:
            kwargs['instance'] = instance

        return kwargs

    def get_initial(self):
        return {
            'full_name': self.get_user_profile().name,
        }

    def get_user_profile(self):
        return UserProfile.objects.get(user=self.request.user)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.course_key = self.get_course().id
        instance.save()

        user_profile = self.get_user_profile()
        user_profile.name = form.cleaned_data['full_name']
        user_profile.save()

        return super(UniversityIDView, self).form_valid(form)

    def get_success_url(self):
        return reverse('edraak_university_id_success', kwargs={
            'course_id': self.kwargs['course_id'],
        })

    def get_course(self):
        course_key = CourseLocator.from_string(self.kwargs['course_id'])
        return get_course_with_access(self.request.user, 'load', course_key, check_if_enrolled=True)

    def get_context_data(self, **kwargs):
        return {
            'course': self.get_course(),
            'form': self.get_form(),
            'has_valid_information': has_valid_university_id(self.request.user, self.kwargs['course_id']),
        }

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        return super(UniversityIDView, self).dispatch(*args, **kwargs)


# Comply with the openedx.course_tab functionality
university_id = UniversityIDView.as_view()


class UniversityIDSuccessView(TemplateView):
    template_name = 'edraak_university/university_id_success.html'

    def get_context_data(self, **kwargs):
        course_key = CourseLocator.from_string(self.kwargs['course_id'])

        return {
            'course': get_course_with_access(self.request.user, 'load', course_key, check_if_enrolled=True),
        }

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        return super(UniversityIDSuccessView, self).dispatch(*args, **kwargs)
