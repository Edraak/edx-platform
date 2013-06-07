from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from tastypie.http import HttpUnauthorized, HttpForbidden, HttpNotFound
from tastypie.exceptions import ImmediateHttpResponse
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie.resources import Resource
from tastypie.exceptions import NotFound
from tastypie import fields
from .utils import get_user_from_token, get_user_from_request

from .utils import get_user_from_token
import Queue
import logging
import datetime

# this is a hack for hackathon, ultimately we want this persisted and not in-mem
USER_TO_MOBILE_TOKEN_MAP = {1: "1234"}
MOBILE_NOTIFICATION_QUEUE = {}


class MobileResource(Resource):
    token = fields.CharField(attribute='token')
    payload = fields.CharField(attribute='payload')

    class Meta:
        allowed_methods = ['get', 'post']
        resource_name = 'mobile'
        include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/register%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('register'), name="mobile_register"),
            url(r'^(?P<resource_name>%s)/(?P<mobile_token>[\w\d:/_.-]+)/poll%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('poll'), name='mobile_poll'),
        ]

    def register(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))

        user_token = data.get('user_token', '')
        user = get_user_from_token(user_token)

        mobile_token = data.get('mobile_token', '')

        USER_TO_MOBILE_TOKEN_MAP[user_id] = mobile_token

    def poll(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        user = get_user_from_request(request)
        user_id = user.user_id if user else 1

        if not user_id:
            raise HttpForbidden

        mobile_token = kwargs['mobile_token']

        if mobile_token in MOBILE_NOTIFICATION_QUEUE:
            try:
                item = MOBILE_NOTIFICATION_QUEUE[mobile_tokenmobile_token].get(timeout=0)
                return self.create_response(request, item)
            except Queue.Empty:
                pass

        return self.create_response(request, None, response_class=HttpNotFound)

    def add_to_queue(self, user_id, payload):
        user_id = 1

        mobile_token = USER_TO_MOBILE_TOKEN_MAP.get(user_id, None)

        if not token:
            return

        if token not in MOBILE_NOTIFICATION_QUEUE:
            MOBILE_NOTIFICATION_QUEUE[token] = Queue.Queue()

        MOBILE_NOTIFICATION_QUEUE[token].put({'mobile_token': token, 'payload': payload})
