from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.modulestore.locator import CourseLocator
from xmodule.modulestore.mongo.draft import as_draft
from util.json_request import JsonResponse


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
    loc = course.location
    return {
        "id": loc.url(),
        "organization": loc.org,
        "number": loc.course,
        "run": loc.name,
        "branches": {
            "published": loc.url(),
            "draft": as_draft(loc).url(),
        }
    }


def list_indexes(request):
    courses = [serialize_course(c) for c in modulestore().get_courses()]
    return JsonResponse(courses)


def detail_index(request, index_id):
    loc = Location(index_id)
    course = modulestore().get_course(loc.course_id)
    return JsonResponse(serialize_course(course))
