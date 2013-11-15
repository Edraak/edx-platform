from xmodule.modulestore.django import modulestore, loc_mapper
from xmodule.modulestore.locator import CourseLocator
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
    m = loc_mapper()
    published_locator = m.translate_location(course.location.course_id, course.location, True)
    draft_locator = m.translate_location(course.location.course_id, course.location, False)
    return {
        "id": published_locator.course_id,
        "branches": {
            "published": unicode(published_locator),
            "draft": unicode(draft_locator),
        }
    }


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
