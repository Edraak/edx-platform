"""Admin interface for the util app. """

from ratelimitbackend import admin
from util.models import RateLimitConfiguration
from util.models import StudentAccountLock, IPLock

from edraak_ratelimit.admin import RateLimitedIPAdmin
from student.admin import LoginFailuresAdmin

# Adding these models here instead of their actual apps so it's easy to find in the admin panel.
admin.site.register(RateLimitConfiguration)

# Edraak: Unlock student-specific account locks
admin.site.register(StudentAccountLock, LoginFailuresAdmin)

# Edraak: Unlock IP-specific locks
admin.site.register(IPLock, RateLimitedIPAdmin)
