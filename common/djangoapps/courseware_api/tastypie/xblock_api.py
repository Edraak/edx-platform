"""
NOTE: named xblock_api to prevent name clashes with imports from xblock.
"""

import time
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie.http import HttpNotImplemented

from tastypie.resources import Resource
from django.conf.urls import patterns, url
from django.contrib.auth.models import User


from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.contentstore.content import StaticContent

from xmodule.course_module import CourseDescriptor


# Only return a subset of the data
METADATA_WHITELIST = ['display_name']


class XBlockObject(object):
    def __init__(self):
        self.id = ''
        self.blocks = {}

class XBlockResource(Resource):
    id = fields.CharField(attribute='id')
    blocks = fields.DictField(attribute='blocks')


    class Meta:
        resource_name = 'xblock'
        object_class = XBlockObject
        authentication = Authentication()
        authorization = Authorization()
        include_resource_uri = False
        allowed_methods = ['get']

    def prepend_urls(self):
        """
        The tastypie default url pattern don't like our locations, what with
        their strange chars (like ':').  Add another url pattern that looks
        similar, but is less restrictive.
        """
        return [
            url(r"^(?P<resource_name>{0})/(?P<pk>[\w\d:/_.-]+)/$".format(
                self._meta.resource_name),
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def obj_get(self, request=None, **kwargs):
        location = kwargs['pk']

        real_loc = Location(location)
        hack_list = ['video', 'html']
        if real_loc.category not in hack_list:
            raise ImmediateHttpResponse(HttpNotImplemented())

        import pudb; pudb.set_trace()

        store = modulestore()
        course_id = CourseDescriptor.location_to_id(location)
        try:
            xblock = store.get_instance(course_id, location)
        except:
            raise NotFound

        
        
        # @TODO: Check for authorization

        # TODO: make this a real thing
        result = XBlockObject()

        add_xblock_summary(xblock, result)

        result.id = id
        return result

