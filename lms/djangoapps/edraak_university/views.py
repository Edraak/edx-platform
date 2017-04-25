from django.core.urlresolvers import reverse
from django.views import generic
from django.shortcuts import Http404, redirect

from openedx.core.djangoapps.user_api.accounts.api import update_account_settings

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from util.views import ensure_valid_course_key
from opaque_keys.edx.locator import CourseLocator
from courseware.courses import get_course_with_access

from courseware.access import has_access
from student.models import UserProfile, CourseEnrollment

from forms import UniversityIDForm
from models import UniversityID
from helpers import get_university_id, has_valid_university_id


class CourseContextMixin(object):
    def get_course_key(self):
        return CourseLocator.from_string(self.kwargs['course_id'])

    def get_course(self):
        course_key = self.get_course_key()
        return get_course_with_access(self.request.user, 'load', course_key)

    def require_staff_access(self):
        course = self.get_course()
        if not has_access(self.request.user, 'staff', course):
            raise Http404('Course does not exists, or user does not have permission.')

    def get_context_data(self, **kwargs):
        data = super(CourseContextMixin, self).get_context_data(**kwargs)
        data['course'] = self.get_course()
        return data


class UniversityIDView(CourseContextMixin, generic.FormView):
    template_name = 'edraak_university/university_id.html'
    form_class = UniversityIDForm

    def get(self, *args, **kwargs):
        course = self.get_course()

        if has_access(self.request.user, 'staff', course):
            return redirect('edraak_university_id_list', course_id=course.id)
        else:
            return super(UniversityIDView, self).get(*args, **kwargs)

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
        instance.course_key = self.get_course_key()
        instance.save()

        update_account_settings(self.request.user, {
            'name': form.cleaned_data['full_name'],
        })

        return super(UniversityIDView, self).form_valid(form)

    def get_success_url(self):
        return reverse('edraak_university_id_success', kwargs={
            'course_id': self.kwargs['course_id'],
        })

    def get_context_data(self, **kwargs):
        data = super(UniversityIDView, self).get_context_data(**kwargs)
        show_enroll_banner = self.request.user.is_authenticated() and not CourseEnrollment.is_enrolled(self.user, self.get_course_key())

        data.update({
            'form': self.get_form(),
            'has_valid_information': has_valid_university_id(self.request.user, self.kwargs['course_id']),
            'show_enroll_banner': show_enroll_banner
        })

        return data

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):

        return super(UniversityIDView, self).dispatch(*args, **kwargs)


# Comply with the openedx.course_tab functionality
university_id = UniversityIDView.as_view()


class UniversityIDSuccessView(CourseContextMixin, generic.TemplateView):
    template_name = 'edraak_university/university_id_success.html'

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        return super(UniversityIDSuccessView, self).dispatch(*args, **kwargs)


class UniversityIDListView(CourseContextMixin, generic.ListView):
    model = UniversityID
    template_name = 'edraak_university/instructor/list.html'

    def get_queryset(self):
        return UniversityID.get_marked_university_ids(course_key=self.get_course_key())

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        self.require_staff_access()
        return super(UniversityIDListView, self).dispatch(*args, **kwargs)


class UniversityIDUpdateView(CourseContextMixin, generic.UpdateView):
    model = UniversityID
    template_name = 'edraak_university/instructor/update.html'

    # The email and full_name fields are written directly in the `update.html` file.
    fields = ('university_id', 'section_number',)

    def get_success_url(self):
        return reverse('edraak_university_id_list', kwargs={
            'course_id': self.get_course_key(),
        })

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        self.require_staff_access()
        return super(UniversityIDUpdateView, self).dispatch(*args, **kwargs)


class UniversityIDDeleteView(CourseContextMixin, generic.DeleteView):
    model = UniversityID
    template_name = 'edraak_university/instructor/delete.html'

    def get_success_url(self):
        return reverse('edraak_university_id_list', kwargs={
            'course_id': self.get_course_key(),
        })

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        self.require_staff_access()
        return super(UniversityIDDeleteView, self).dispatch(*args, **kwargs)
