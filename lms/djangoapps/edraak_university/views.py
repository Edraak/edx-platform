from django import forms
from django.utils.translation import ugettext_lazy as _

from edxmako.shortcuts import render_to_response

from opaque_keys.edx import locator
from xmodule.modulestore.django import modulestore


class UniversityIDForm(forms.Form):
    full_name = forms.CharField(
        label=_('Full Name *'),
        help_text=_(
            'Enter your full name that you use at the university (same as your profile page).'
        ),
        required=True,
        min_length=2,
    )

    university_id = forms.CharField(
        label=_('University ID *'),
        help_text=_('Enter the full university ID e.g. 201311318.'),
        required=True,
        min_length=4,
    )

    section_number = forms.CharField(
        label=_('Section Number *'),
        help_text=_('Enter the number/name of the section e.g. 1, 2 or A, B, C depending on your university structure.'),
        required=True,
        min_length=1,
    )

    def as_div(self):
        """
        Returns this form rendered as HTML <p>s.

        This is similar to Form.as_p() but puts the errors after the field.
        """
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(errors)s %(field)s %(help_text)s</div>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )


def university_id(request, course_id):
    course_key = locator.CourseLocator.from_string(course_id)
    course = modulestore().get_course(course_key)

    if request.method == 'POST':
        form = UniversityIDForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = UniversityIDForm()

    return render_to_response('edraak_university/university_id.html', {
        'course': course,
        'form': form,
        'has_valid_information': False,
    })
