import logging
import time
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import Resource
from django.contrib.auth.models import User
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.contentstore.content import StaticContent
from xmodule.course_module import CourseDescriptor

from student.models import CourseEnrollment


log = logging.getLogger(__name__)


class ProfileObject(object):
    def __init__(self):
        self.name = ''
        self.username = ''
        self.email = ''
        self.courses = []


class ProfileResource(Resource):
    name = fields.CharField(attribute='name')
    username = fields.CharField(attribute='username')
    email = fields.CharField(attribute='email')
    courses = fields.ListField(attribute='courses')

    class Meta:
        resource_name = 'profile'
        object_class = ProfileObject
        authentication = Authentication()
        authorization = Authorization()
        include_resource_uri = False
        allowed_methods = ['get']

    def obj_get(self, request=None, **kwargs):
        # return RiakObject(initial={'name': 'bar'})
        username = kwargs['pk']

        # Get the User object from the passed in id
        user = User.objects.get(username=username)
        result = ProfileObject()
        result.name = ' '.join([user.first_name, user.last_name]).strip()
        result.username = user.username
        result.email = user.email

        # get all enrollments for this user
        enrollments = CourseEnrollment.objects.filter(user=user)

        # go through the content database and query for each course
        store = modulestore()
        for course_enrollment in enrollments:
            course_loc = CourseDescriptor.id_to_location(course_enrollment.course_id)
            try:
                course = store.get_instance(course_enrollment.course_id, course_loc)
            except:
                # this can happen when we delete courses - typical for dev environments
                log.debug("%r enrolled in non-existent course %r", user.username, course_loc)
                continue

            # get short_description
            short_description = ''
            try:
                short_description_location = course.location._replace(category='about', name='short_description')
                short_description_descriptor = store.get_item(short_description_location)
                short_description = short_description_descriptor.data
            except ItemNotFoundError:
                pass

            # compute course image url
            image_loc = course.location._replace(tag='c4x', category='asset', name='images_course_image.jpg')
            image_path = StaticContent.get_url_path_from_location(image_loc)

            course_dict = {
                'course_id': course.location.course_id,
                'name': course.display_name,
                'description': short_description,
                'image_url': image_path,
                'is_running': (time.gmtime() > course.start)
            }
            result.courses.append(course_dict)

        return result
