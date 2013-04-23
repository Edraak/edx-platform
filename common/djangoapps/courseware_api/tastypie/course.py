import time
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound
from tastypie.resources import Resource
from django.contrib.auth.models import User
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.contentstore.content import StaticContent
from xmodule.course_module import CourseDescriptor

from xblock.core import Scope

from student.models import CourseEnrollment

# Only return a subset of the data
METADATA_WHITELIST = ['display_name']


class CourseObject(object):
    def __init__(self):
        self.id = ''
        self.blocks = {}

class CourseResource(Resource):
    id = fields.CharField(attribute='id')
    blocks = fields.DictField(attribute='blocks')


    class Meta:
        resource_name = 'course'
        object_class = CourseObject
        authentication = Authentication()
        authorization = Authorization()
        include_resource_uri = False
        allowed_methods = ['get']

    def obj_get(self, request=None, **kwargs):
        # return RiakObject(initial={'name': 'bar'})
        id = kwargs['pk']

        store = modulestore()
        course_loc = CourseDescriptor.id_to_location(id)
        try:
            course = store.get_instance(id, course_loc, depth=4)
        except:
            raise NotFound

        # @TODO: Check for authorization

        result = CourseObject()
        # crawl through the course and create the course outline document
        def add_xblock_summary(module, result):
            metadata = {}
            for field in module.fields + module.lms.fields:
                if field.name not in METADATA_WHITELIST:
                    continue
                # Only save metadata that wasn't inherited
                if field.scope != Scope.settings:
                    continue

                try:
                    metadata[field.name] = module._model_data[field.name]
                except KeyError:
                    # Ignore any missing keys in _model_data
                    pass

            summary = {
                'category': module.location.category,
                'metadata': metadata,
                'children': getattr(module, 'children', []),
                'definition': module.location.url()
            }
            result.blocks[module.location.url()] = summary
            for child in module.get_children():
                add_xblock_summary(child, result)

        add_xblock_summary(course, result)

        result.id = id
        return result

