import logging

from courseware.courses import get_course_about_section
from opaque_keys.edx import locator
from xmodule.modulestore.django import modulestore
from .edraakcertificate import EdraakCertificate

logger = logging.getLogger(__name__)


def generate_certificate(request, course_id):
    course_key = locator.CourseLocator.from_string(course_id)

    path_builder = request.build_absolute_uri
    course = modulestore().get_course(course_key)
    course_short_desc = get_course_about_section(
        request, course, 'short_description')

    preview_mode = request.GET.get('preview', None)
    cert = EdraakCertificate(course=course,
                             user=request.user,
                             course_desc=course_short_desc,
                             preview_mode=preview_mode,
                             path_builder=path_builder)

    cert.generate_and_save()
    return cert.temp_file
