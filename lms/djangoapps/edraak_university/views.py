from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.shortcuts import Http404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required

from openedx.core.djangoapps.user_api.accounts.api import update_account_settings
from openedx.core.djangoapps.course_groups.cohorts import add_user_to_cohort, remove_user_from_cohort, get_cohort

from util.views import ensure_valid_course_key
from opaque_keys.edx.locator import CourseLocator
from courseware.courses import get_course_with_access
from courseware.views import course_about, marketing_link
from courseware.access import has_access
from student.models import UserProfile, CourseEnrollment

from forms import UniversityIDForm, UniversityIDSettingsForm
from models import UniversityID, UniversityIDSettings
from helpers import get_university_id, has_valid_university_id


class ContextMixin(object):
    def get_course_key(self):
        return CourseLocator.from_string(self.kwargs['course_id'])

    def get_course(self):
        course_key = self.get_course_key()
        return get_course_with_access(self.request.user, 'load', course_key)

    def require_staff_access(self):
        course = self.get_course()
        if not has_access(self.request.user, 'staff', course):
            raise Http404('Course does not exists, or user does not have permission.')

    def get_university_settings(self):
        try:
            key = self.get_course_key()
            return UniversityIDSettings.objects.get(course_key=key)
        except UniversityIDSettings.DoesNotExist:
            return None

    def get_student_uid(self):
        try:
            return UniversityID.objects.get(user=self.request.user,
                                            course_key=self.get_course_key())
        except UniversityID.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        data = super(ContextMixin, self).get_context_data(**kwargs)
        data['course'] = self.get_course()
        return data


class UniversityIDView(ContextMixin, generic.FormView):
    template_name = 'edraak_university/university_id.html'
    form_class = UniversityIDForm

    def get(self, *args, **kwargs):
        course = self.get_course()

        if has_access(self.request.user, 'staff', course):
            return redirect('edraak_university_id_staff', course_id=course.id)
        else:
            return super(UniversityIDView, self).get(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UniversityIDView, self).get_form_kwargs()
        kwargs['course_key'] = self.get_course_key()

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
        instance.cohort = form.cleaned_data['cohort']
        instance.save()

        update_account_settings(self.request.user, {
            'name': form.cleaned_data['full_name'],
        })

        try:
            add_user_to_cohort(instance.cohort, instance.user.email)
        except ValueError:
           # User already present in the cohort
           pass

        return super(UniversityIDView, self).form_valid(form)

    def get_success_url(self):
        return reverse('edraak_university_id_success', kwargs={
            'course_id': self.kwargs['course_id'],
        })

    def is_not_enrolled(self):
        return self.request.user.is_authenticated() and not CourseEnrollment.is_enrolled(self.request.user, self.get_course_key())

    def get_context_data(self, **kwargs):
        data = super(UniversityIDView, self).get_context_data(**kwargs)
        mktg_enabled = settings.FEATURES.get('ENABLE_MKTG_SITE')
        university_settings = self.get_university_settings()

        data.update({
            'form': self.get_form(),
            'has_valid_information': has_valid_university_id(self.request.user, self.kwargs['course_id']),
            'is_form_disabled': self.is_form_disabled(),
            'terms_conditions': university_settings.terms_and_conditions if university_settings else None,
            'show_enroll_banner': self.is_not_enrolled(),
            'registration_end': university_settings.registration_end_date if university_settings else None,
            'url_to_enroll': marketing_link('COURSES') if mktg_enabled else reverse(course_about,args=[self.get_course_key()]),
        })

        return data

    def is_form_disabled(self):
        """
        This method detects if the form should be disabled or 
        enabled. The form is should be disabled in the following cases:
            * If the instructor edited the student data.
            * The registration end date is not null and already passed.
            * The user is not enrolled in the course.
        :return: True if the form must be disabled, False otherwise 
        """
        student_uid = self.get_student_uid()
        if student_uid and not student_uid.can_edit:
            return True

        university_settings = self.get_university_settings()
        if university_settings:
            # The instructor already defined a settings for the course
            registration_end = university_settings.registration_end_date
            if registration_end:
                # The registration end date is not stored as null
                today = timezone.now().date()
                return registration_end <= today or self.is_not_enrolled()

        return self.is_not_enrolled()

    @method_decorator(transaction.non_atomic_requests)
    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        return super(UniversityIDView, self).dispatch(*args, **kwargs)


# Comply with the openedx.course_tab functionality
university_id = UniversityIDView.as_view()


class UniversityIDSuccessView(ContextMixin, generic.TemplateView):
    template_name = 'edraak_university/university_id_success.html'

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        return super(UniversityIDSuccessView, self).dispatch(*args, **kwargs)


class UniversityIDStaffView(ContextMixin, generic.FormView, generic.ListView):
    template_name = 'edraak_university/instructor/main.html'
    model = UniversityID
    form_class = UniversityIDSettingsForm

    def get_success_url(self):
        return reverse('edraak_university_id_success', kwargs={
            'course_id': self.kwargs['course_id'],
        })

    def get_queryset(self):
        return UniversityID.get_marked_university_ids(course_key=self.get_course_key())

    def get_initial(self):
        initial = {}
        inst = self.get_university_settings()

        if inst:
            initial = {
                'registration_end_date': inst.registration_end_date,
                'terms_and_conditions': inst.terms_and_conditions,
            }

        return initial

    def form_invalid(self, form):
        """
        When the form is invalid this method is rendering the response 
        directly without setting the object list which causes an error.
        :param form: The invalid form.
        :return: The super render to response.
        """
        self.object_list = self.get_queryset()
        return super(UniversityIDStaffView, self).form_invalid(form)

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        self.require_staff_access()
        return super(UniversityIDStaffView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UniversityIDStaffView,self).get_context_data()
        context['sections'] = [
            {
                'section_display_name': 'Students\' IDs List',
                'section_key': 'list'
            },
            {
                'section_display_name': 'University ID settings',
                'section_key': 'settings',
                'form': self.get_form()
            },
        ]

        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.course_key = self.get_course_key()
        instance.save()
        return super(UniversityIDStaffView, self).form_valid(form)


class UniversityIDUpdateView(ContextMixin, generic.UpdateView):
    model = UniversityID
    template_name = 'edraak_university/instructor/update.html'

    # The email and full_name fields are written directly in the `update.html` file.
    fields = ('university_id','cohort')

    def get_success_url(self):
        return reverse('edraak_university_id_staff', kwargs={
            'course_id': self.get_course_key(),
        })

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.cohort = form.cleaned_data['cohort']
        instance.can_edit = False
        instance.save()

        try:
            add_user_to_cohort(instance.cohort, instance.user.email)
        except ValueError:
           pass
        return super(UniversityIDUpdateView, self).form_valid(form)


    @method_decorator(transaction.non_atomic_requests)
    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        self.require_staff_access()
        return super(UniversityIDUpdateView, self).dispatch(*args, **kwargs)


class UniversityIDDeleteView(ContextMixin, generic.DeleteView):
    model = UniversityID
    template_name = 'edraak_university/instructor/delete.html'

    def get_success_url(self):
        return reverse('edraak_university_id_staff', kwargs={
            'course_id': self.get_course_key(),
        })

    def delete(self, request, *args, **kwargs):
        obj = self.get_object() # University ID object
        obj.can_edit = True
        obj.save()

        cohort = get_cohort(obj.user, obj.course_key, assign=False)
        try:
            remove_user_from_cohort(cohort, obj.user.username)
        except ValueError:
            # If user not already present in this cohort.
            pass

        return super(UniversityIDDeleteView, self).delete(request, *args, **kwargs)

    @method_decorator(login_required)
    @method_decorator(ensure_valid_course_key)
    def dispatch(self, *args, **kwargs):
        self.require_staff_access()
        return super(UniversityIDDeleteView, self).dispatch(*args, **kwargs)
