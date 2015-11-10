from django.conf import settings
from django.core.urlresolvers import reverse


def get_mktg_enroll_success_redirect(course_id):
    """
    Provide a success page option after course enrollment in the marketing site.

    This provides an alternative to redirecting the user to the dashboard after successful enrollment.

    This function is enabled once `MKTG_URLS['ENROLL_SUCCESS']` is set in the settings.

    :param course_id: Course ID as string.
    :return (unicode) Redirect URL.
    """
    if settings.FEATURES.get('ENABLE_MKTG_SITE'):
        enroll_success_url = settings.MKTG_URLS.get('ENROLL_SUCCESS')

        if enroll_success_url:
            # TODO: Handle language-based URL e.g. /about/ vs. /en/about/
            return '{root}{path}'.format(
                root=settings.MKTG_URLS['ROOT'],
                path=enroll_success_url.format(
                    course_id=course_id,
                ),
            )

    return reverse('dashboard')
