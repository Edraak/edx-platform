"""
django admin page for the xblock registry table
"""

from xblock_registry.models import XBlockInfo
from xblock.core import XBlock

from django.contrib.auth.models import Permission

from ratelimitbackend import admin

from edxmako.shortcuts import render_to_string

import logging

log = logging.getLogger("studio.xblockregistry")


def refresh_registered_xblocks(modeladmin, request, queryset):
    xblock_names = set(name for name, class_ in XBlock.load_classes())
    for existing_entry in XBlockInfo.objects.all():
        if existing_entry.name not in xblock_names:
            existing_entry.delete()
    for name in xblock_names:
        if XBlockInfo.objects.filter(name=name).count() == 0:
            XBlockInfo.objects.create(name=name)

refresh_registered_xblocks.short_description = "Refresh registered xblocks"

def enable_selected_xblocks(modeladmin, request, queryset):
    queryset.update(state=XBlockInfo.APPROVED)

enable_selected_xblocks.short_description = "Approve selected xblocks"

class XBlockInfoAdmin(admin.ModelAdmin):
    """
    Admin for the course creator table.
    """

    # Fields to display on the overview page.
    list_display = ['name', 'state', 'screenshot', 'summary']
    readonly_fields = ['name']
    # Controls the order on the edit form (without this, read-only fields appear at the end).
    fieldsets = (
        (None, {
            'fields': ['name', 'state', 'screenshot', 'summary']
        }),
        )
    # Fields that filtering support
    list_filter = ['state']
    # Fields that search supports.
    search_fields = ['name', 'state', 'summary', 'screenshot']
    actions = [enable_selected_xblocks, refresh_registered_xblocks]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if user.is_staff:
            # I had a lot of trouble getting delete permissions to work.
            # I would hope this would not be necessary.
            if not user.has_perm('xblock_registry.delete_xblockinfo'):
                permission = Permission.objects.get(codename='delete_xblockinfo')
                user.user_permissions.add(permission)
                user.save()
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    # Hack to allow the refresh action to be called with no selected items.
    def changelist_view(self, request, extra_context=None):
        post = request.POST.copy()
        if admin.ACTION_CHECKBOX_NAME not in post:
            post.update({admin.ACTION_CHECKBOX_NAME:None})
            request._set_post(post)
        return super(XBlockInfoAdmin, self).changelist_view(request, extra_context)

admin.site.register(XBlockInfo, XBlockInfoAdmin)

# Hack to make sure that refresh action is added.
if len(XBlockInfo.objects.all()) == 0:
    XBlockInfo.objects.create(name="Dummy xblock entry")
