"""
A collection of translation utils.

Copyright 2016 Edraak.org.
"""

from django.utils.translation import ugettext


def force_translate(source, *translatables):
    """
    This function helps to translate strings in LMS that should be translatable
    but due to bad design it's being moved from the CMS and printed directly.

    The function expects a hardcoded string, and multiple translations for
    possible values. The translation should be passed as `ugettext_noop` calls
    explicitly, in order to function.

    Looks for examples for usages around the platform to get a feel of how
    the feature works.

    Generally a simple usage would be like the following:

    exam_format = force_translate(
        exam_format,
        ugettext_noop('Timed Exam'),
        ugettext_noop('Entrance Exam')
    )

    Args:
        source: The source string that is wanted to be translated.
        *translatables: Multiple ugettext_noop values to be passed.

    Returns: The translated string.

    """

    for translatable in translatables:
        if source.strip() == translatable.strip():
            return ugettext(translatable)

    return source

