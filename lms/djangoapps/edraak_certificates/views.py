import logging
import os

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.decorators import login_required
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys import InvalidKeyError
from courseware.courses import get_course_with_access
from courseware.access import has_access
from courseware.grades import grade

from wand.image import Image
from .utils import generate_certificate

logger = logging.getLogger(__name__)


# TODO: Convert to decorator
def is_passing_student(user, request, course_id):
    """
    Only staff and passed students are allowed to issue certificates.
    """

    user = request.user
    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_with_access(user, 'load', course_key)

    # if not is_certificate_allowed(user, course):  # TODO: Merge with both functions
        # return False

    if has_access(user, 'staff', course):
        return True

    return bool(grade(user, request, course)['grade'])


@csrf_exempt
@login_required
def issue(request):
    course_id = request.POST['certificate_course_id']
    user = request.user

    # Only staff and passed students are allowed to issue certificates
    if not is_passing_student(user, request, course_id):
        return redirect(reverse('dashboard'))

    course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_with_access(user, 'load', course_key)

    return render_to_response('edraak_certificates/issue.html', {
        'user': user,
        'course': course,
    })


@login_required
def download(request, course_id):
    if not is_passing_student(request.user, request, course_id):
        return redirect(reverse('dashboard'))

    pdf_file = generate_certificate(request, course_id)
    wrapper = FileWrapper(pdf_file)

    # `application/octet-stream` is to force download
    response = HttpResponse(wrapper, content_type='application/octet-stream')

    response['Content-Length'] = os.path.getsize(pdf_file.name)
    response['Content-Disposition'] = "attachment; filename=Edraak-Certificate.pdf"

    return response


@login_required
def preview(request, course_id):
    if not is_passing_student(request.user, request, course_id):
        return redirect(reverse('dashboard'))

    pdf_file = generate_certificate(request, course_id)
    image_file = NamedTemporaryFile(suffix='-cert.png')

    with Image(filename=pdf_file.name) as img:
        with img.clone() as i:
            i.resize(445, 315)
            i.save(filename=image_file.name)

    wrapper = FileWrapper(image_file)
    response = HttpResponse(wrapper, content_type='image/png')
    response['Content-Length'] = os.path.getsize(image_file.name)

    return response