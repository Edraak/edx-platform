from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import Resource


class ProfileObject(object):
    name = 'Fred W'
    username = 'freddy'
    email = 'fred@edx.org'
    courses = [{'course_id': 'edX/Welding/2013',
                'name': 'Power Welding!',
                'description': 'This is Power Welding.',
                'image_url': 'https://www.edx.org/static/content-berkeley-cs191x~2013_Spring/images/course_image.jpg',
                'is_running': True}]


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

    def obj_get(self, request=None, **kwargs):
        # return RiakObject(initial={'name': 'bar'})
        pk = kwargs['pk']
        result = ProfileObject()
        result.name = pk
        return result
