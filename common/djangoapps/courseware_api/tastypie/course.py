from tastypie import fields
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound
from tastypie.resources import Resource
from xmodule.modulestore.django import modulestore
from xmodule.course_module import CourseDescriptor

from .utils import get_xblock_summary

# Only return a subset of the data
METADATA_WHITELIST = ['display_name']


class CourseObject(object):
    def __init__(self):
        self.id = None
        self.root = None
        self.blocks = {}


class CourseResource(Resource):
    id = fields.CharField(attribute='id')
    root = fields.CharField(attribute='root')
    blocks = fields.DictField(attribute='blocks')

    class Meta:
        resource_name = 'course'
        object_class = CourseObject
        authentication = BasicAuthentication()
        authorization = Authorization()
        include_resource_uri = False
        allowed_methods = ['get']

    def obj_get(self, request=None, **kwargs):
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
            # TODO: check that the user has access, ideally without
            # thousands of queries to the DB.
            summary = get_xblock_summary(module, METADATA_WHITELIST)

            result.blocks[module.location.url()] = summary
            for child in module.get_children():
                add_xblock_summary(child, result)

        add_xblock_summary(course, result)

        result.id = id
        result.root = course_loc
        return result

