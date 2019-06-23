import json

from xmodule.modulestore.django import modulestore

from contentstore.views.certificates import CertificateManager

from student.roles import CourseInstructorRole

from student.models import UserProfile

from xmodule.modulestore.exceptions import ItemNotFoundError
from lms.djangoapps.courseware.courses import get_course_about_section
from lms.djangoapps.instructor.utils import DummyRequest
from openedx.core.djangoapps.models.course_details import CourseDetails

all_courses = modulestore().get_courses()

def get_main_instractor_name(course):
    instructor_name = ''
    role = CourseInstructorRole(course.id)
    if role.users_with_role():
        instructor_user = role.users_with_role()[0]
        instructor_name = UserProfile.objects.get(user=instructor_user).name
    return instructor_name



def create_cert(course):
    if course.certificates.get('certificates') is None:
        desc = ""
        try:
            desc = CourseDetails.fetch(course.id).short_description
        except:
            pass
        course.certificates['certificates'] = []
        body = {"editing":True,
         "course_title": course.display_name,
         "name":"Name of the certificate",
         "description": desc,
         "version":1,
         "is_active":True,
         "signatories":
         [{
            "certificate":None,
            "name": get_main_instractor_name(course),
            "title": "",
            "organization": course.org.lower(),
            "signature_image_path": "/c4x/AUB/CZN100/asset/trans.png"}]}
        # print body
        new_certificate = CertificateManager.deserialize_certificate(course, json.dumps(body))
        if course.certificates.get('certificates') is None:
            course.certificates['certificates'] = []
        course.certificates['certificates'].append(new_certificate.certificate_data)
        modulestore().update_item(course, 27533)
        # print 'created', {
        #     'course_id': unicode(course.id),
        #     'configuration_id': new_certificate.id
        # }


for c in all_courses:
    c.certificates['certificates'] = None
    try:
        create_cert(c)
    except ItemNotFoundError as e:
        print "==========================================|>", e, unicode(c.id)
