"""
Defines the URL routes for this app.

NOTE: These views are deprecated.  These routes are superseded by
``/api/user/v1/accounts/{username}/image``, found in
``openedx.core.djangoapps.user_api.urls``.
"""

from django.conf.urls import patterns, url

from .views import ProfileImageUploadView, ProfileImageRemoveView

USERNAME_PATTERN = r'(?P<username>[\w.+-]+)'
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
