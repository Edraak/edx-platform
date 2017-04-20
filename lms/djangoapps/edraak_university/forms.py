import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from openedx.core.djangoapps.user_api.accounts import NAME_MIN_LENGTH
from openedx.core.djangoapps.course_groups.cohorts import get_cohort_names

from models import UniversityID


class UniversityIDForm(forms.ModelForm):
    full_name = forms.CharField(
        label=_('Full Name in Arabic *'),
        help_text=_('Enter your full name that you use at the university in Arabic.'),
        required=True,
        min_length=NAME_MIN_LENGTH,
        max_length=50,  # Just a basic sanity check
        error_messages={
            'min_length': _('The name you have entered is too short, please double check.'),
            'max_length': _('The student university ID you have entered is too long, please double check.'),
        },
    )

    university_id = forms.RegexField(
        regex=re.compile(r'^[0-9a-z-]+$', re.IGNORECASE),
        label=_('Student University ID *'),
        # TODO: Make ID format instruction course-variant, so coordinators can define it for each course.
        help_text=_('Enter the full student university ID e.g. 201311318.'),
        min_length=4,
        max_length=50,
        error_messages={
            'invalid': _('The student university ID must only consist of numbers, letters and dashes.'),
            'min_length': _('The student university ID you have entered is too short, please double check.'),
            'max_length': _('The student university ID you have entered is too long, please double check.'),
        },
    )

    cohort = forms.ChoiceField(
        label=_('Section Number *'),
        # TODO: Make ID format instruction course-variant, so coordinators can define it for each course.
        help_text=_('Select the cohort you are enrolled in.'),
    )

    def __init__(self,course=None, is_disabled=False, *args, **kwargs):
        super(UniversityIDForm,self).__init__(*args, **kwargs)
        if is_disabled:
            for field in self.fields.keys():
                self.fields[field].widget.attrs['readonly'] = True
            self.fields['cohort'].widget.attrs['disabled'] = True
        if course:
            cohorts = get_cohort_names(course)
            cohorts_choices = [(id, name) for id, name in cohorts.iteritems() ]
            self.fields['cohort'].choices = [('','----')] + cohorts_choices

    class Meta:
        model = UniversityID
        fields = ('full_name', 'university_id', 'cohort')

    def as_div(self):
        """
        Returns this form rendered as HTML <div>s.

        This is similar to Form.as_p() but puts the errors after the field.
        """
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(errors)s %(field)s %(help_text)s</div>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )

    def clean_full_name(self):
        return self.cleaned_data['full_name']

    def clean_university_id(self):
        return self.cleaned_data['university_id']

    def clean_cohort(self):
        return self.cleaned_data['cohort']

    def clean_terms_and_conditions_read(self):
        return self.cleaned_data['terms_and_conditions_read']
