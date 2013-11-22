from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.modulestore import Location
from xmodule.modulestore.locator import CourseLocator
from django.http import HttpResponseRedirect
from util.json_request import JsonResponse
from django.core.urlresolvers import reverse


def map_all_courses():
    for course in modulestore().get_courses():
        for published in (True, False):
            loc_mapper().translate_location(
                course.location.course_id,
                course.location,
                published,
                True
            )


def should_map_courses(course):
    location = loc_mapper().translate_locator_to_location(
        CourseLocator(course.location.course_id),
        get_course=True,
    )
    return not location


def serialize_course(course):
    m = loc_mapper()
    published_locator = CourseLocator(
        m.translate_location(course.location.course_id, course.location, True)
    )
    draft_locator = CourseLocator(
        m.translate_location(course.location.course_id, course.location, False)
    )
    return {
        "id": published_locator.course_id,
        "branches": {
            "published": published_locator.course_id
            # "draft": unicode(draft_locator),
        }
    }


def serialize_snapshot(course):
    m = loc_mapper()
    locator = CourseLocator(
        m.translate_location(course.location.course_id, course.location)
    )
    children_locations = [Location(url) for url in course.children]
    children_locators = [m.translate_location(course.location.course_id, l)
                         for l in children_locations]
    return {
        "id": locator.course_id,
        "xblocks": [l.usage_id for l in children_locators]
    }


def serialize_xblock(xblock):
    fields = {key: value.display_name for key, value in xblock.fields.items()}
    ret =  {
        "name": xblock.location.name,
        "type": xblock.module_class.js_module_name,
        "display": {
            "name": xblock.display_name
        },
        "fields": fields
    }
    return ret



def list_indexes(request):
    courses = [serialize_course(c) for c in modulestore().get_courses()]
    return JsonResponse(courses)


def detail_index(request, index_id):
    locator = CourseLocator(course_id=index_id)
    location = loc_mapper().translate_locator_to_location(
        locator, get_course=True,
    )
    if not location:
        # maybe it just isn't mapped to a locator?
        map_all_courses()
        location = loc_mapper().translate_locator_to_location(
            locator, get_course=True,
        )
    if not location:
        # doesn't exist
        return JsonResponse(status=404)

    course = modulestore().get_item(location)
    return JsonResponse(serialize_course(course))


def index_branches(request, index_id):
    locator = CourseLocator(course_id=index_id)
    location = loc_mapper().translate_locator_to_location(
        locator, get_course=True,
    )
    if not location:
        # maybe it just isn't mapped to a locator?
        map_all_courses()
        location = loc_mapper().translate_locator_to_location(
            locator, get_course=True,
        )
    if not location:
        # doesn't exist
        return JsonResponse(status=404)

    course = modulestore().get_item(location)
    return JsonResponse(serialize_course(course)["branches"])


def index_branch_redirect(request, index_id, branch="published"):
    # for now, we only support the "published" branch
    return HttpResponseRedirect(reverse("detail_snapshot", kwargs={"snapshot_id": index_id}))


def detail_snapshot(request, snapshot_id):
    # before split mongo, we don't have real, immutable snapshots -- so instead
    # of an ID, we'll use a locator string to indentify the snapshot. :(
    locator = CourseLocator(course_id=snapshot_id)
    if locator.branch == "draft":
        return JsonResponse({
            "error": "This API cannot display snapshots for draft courses at this time"
        }, status=501)
    location = loc_mapper().translate_locator_to_location(locator, get_course=True)
    if not location:
        # maybe it just isn't mapped to a locator?
        map_all_courses()
        location = loc_mapper().translate_locator_to_location(locator, get_course=True)
    if not location:
        # doesn't exist
        return JsonResponse(status=404)

    course = modulestore().get_item(location)
    return JsonResponse(serialize_snapshot(course))


def list_xblocks_in_snapshot(request, snapshot_id):
    # before split mongo, we don't have real, immutable snapshots -- so instead
    # of an ID, we'll use a locator string to indentify the snapshot. :(
    locator = CourseLocator(course_id=snapshot_id)
    if locator.branch == "draft":
        return JsonResponse({
            "error": "This API cannot display snapshots for draft courses at this time"
        }, status=501)
    location = loc_mapper().translate_locator_to_location(locator, get_course=True)
    if not location:
        # maybe it just isn't mapped to a locator?
        map_all_courses()
        location = loc_mapper().translate_locator_to_location(locator, get_course=True)
    if not location:
        # doesn't exist
        return JsonResponse(status=404)

    course = modulestore().get_item(location)
    children = [modulestore().get_item(Location(url)) for url in course.children]
    blocks = [serialize_xblock(child) for child in children]
    return JsonResponse(blocks)

def detail_xblock_in_snapshot(request, snapshot_id, xblock_name):
    # TODO


