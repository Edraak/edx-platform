"""Models for the util app. """
import cStringIO
import gzip
import logging

from django.db import models
from django.utils.text import compress_string
from django.utils.translation import ugettext_lazy as _

from config_models.models import ConfigurationModel
from organizations.models import OrganizationCourse

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class RateLimitConfiguration(ConfigurationModel):
    """Configuration flag to enable/disable rate limiting.

    Applies to Django Rest Framework views.

    This is useful for disabling rate limiting for performance tests.
    When enabled, it will disable rate limiting on any view decorated
    with the `can_disable_rate_limit` class decorator.
    """
    class Meta(ConfigurationModel.Meta):
        app_label = "util"


def decompress_string(value):
    """
    Helper function to reverse CompressedTextField.get_prep_value.
    """

    try:
        val = value.encode('utf').decode('base64')
        zbuf = cStringIO.StringIO(val)
        zfile = gzip.GzipFile(fileobj=zbuf)
        ret = zfile.read()
        zfile.close()
    except Exception as e:
        logger.error('String decompression failed. There may be corrupted data in the database: %s', e)
        ret = value
    return ret


class CompressedTextField(models.TextField):
    """ TextField that transparently compresses data when saving to the database, and decompresses the data
    when retrieving it from the database. """

    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        """ Compress the text data. """
        if value is not None:
            if isinstance(value, unicode):
                value = value.encode('utf8')
            value = compress_string(value)
            value = value.encode('base64').decode('utf8')
        return value

    def to_python(self, value):
        """ Decompresses the value from the database. """
        if isinstance(value, unicode):
            value = decompress_string(value)

        return value


class CourseSponsor(OrganizationCourse):
    class Meta(OrganizationCourse.Meta):
        """ Meta class for this Django model """
        verbose_name = _('Course Sponsor')
        verbose_name_plural = _('Link Course Sponsors')
