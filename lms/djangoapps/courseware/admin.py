'''
django admin pages for courseware model
'''

from courseware.models import *
from django.contrib import admin
from django.contrib.auth.models import User

class StudentModuleAdmin(admin.ModelAdmin):
    search_fields = ['student__username', 'module_state_key', 'course_id', 'module_type']
    date_hierarchy = 'created'

admin.site.register(StudentModule, StudentModuleAdmin)

admin.site.register(OfflineComputedGrade)

admin.site.register(OfflineComputedGradeLog)

