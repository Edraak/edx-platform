"""
Defines the URL routes for this app.
"""
from .views import ProfileImageUploadView, ProfileImageRemoveView

from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns(
    '',
    url(
        r'^v1/{}/upload$'.format(settings.USERNAME_PATTERN),
        ProfileImageUploadView.as_view(),
        name="profile_image_upload"
    ),
    url(
        r'^v1/{}/remove$'.format(settings.USERNAME_PATTERN),
        ProfileImageRemoveView.as_view(),
        name="profile_image_remove"
    ),
)
