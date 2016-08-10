from models import UniversityID
from opaque_keys.edx.locator import CourseLocator


def get_university_id(user, course_id):
    try:
        return UniversityID.objects.get(
            user=user,
            course_key=CourseLocator.from_string(course_id),
        )
    except UniversityID.DoesNotExist:
        return None


def has_valid_university_id(user, course_id):
    return bool(get_university_id(user, course_id))


def university_id_is_required(user, course):
    if course.enable_university_id:
        if not has_valid_university_id(user, unicode(course.id)):
            return True

    return False
