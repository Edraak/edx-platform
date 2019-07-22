"""Admin interface for the util app. """

from ratelimitbackend import admin
from util.models import (
    RateLimitConfiguration,
    CourseSponsor,
    OrganizationDetail,
)


admin.site.register(RateLimitConfiguration)
admin.site.register(CourseSponsor)
admin.site.register(OrganizationDetail)
