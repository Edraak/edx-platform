from django.http import HttpResponsePermanentRedirect

def redirect_arabic_course(request, prefix, old_course_id, suffix, new_course_id):
    new_url = ur'/{prefix}{new_course_id}{suffix}'.format(
        prefix=prefix,
        new_course_id=new_course_id,
        suffix=suffix,
    )

    return HttpResponsePermanentRedirect(new_url)
