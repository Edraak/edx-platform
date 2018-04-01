# -*- coding: utf-8 -*-
"""
Certificates are created for a student and an offering of a course.

When a certificate is generated, a unique ID is generated so that
the certificate can be verified later. The ID is a UUID4, so that
it can't be easily guessed and so that it is unique.

Certificates are generated in batches by a cron job, when a
certificate is available for download the GeneratedCertificate
table is updated with information that will be displayed
on the course overview page.


State diagram:

[deleted,error,unavailable] [error,downloadable]
            +                +             +
            |                |             |
            |                |             |
         add_cert       regen_cert     del_cert
            |                |             |
            v                v             v
       [generating]    [regenerating]  [deleting]
            +                +             +
            |                |             |
       certificate      certificate    certificate
         created       removed,created   deleted
            +----------------+-------------+------->[error]
            |                |             |
            |                |             |
            v                v             v
      [downloadable]   [downloadable]  [deleted]


Eligibility:

    Students are eligible for a certificate if they pass the course
    with the following exceptions:

       If the student has allow_certificate set to False in the student profile
       he will never be issued a certificate.

       If the user and course is present in the certificate whitelist table
       then the student will be issued a certificate regardless of his grade,
       unless he has allow_certificate set to False.
"""
import json
import logging
import uuid
import os

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.fields.json import JSONField
from model_utils import Choices
from model_utils.models import TimeStampedModel
from xmodule.modulestore.django import modulestore
from config_models.models import ConfigurationModel
from xmodule_django.models import CourseKeyField, NoneToEmptyManager
from util.milestones_helpers import fulfill_course_milestone, is_prerequisite_courses_enabled
from course_modes.models import CourseMode
from instructor_task.models import InstructorTask

LOGGER = logging.getLogger(__name__)


class CertificateStatuses(object):
    """
    Enum for certificate statuses
    """
    deleted = 'deleted'
    deleting = 'deleting'
    downloadable = 'downloadable'
    error = 'error'
    generating = 'generating'
    notpassing = 'notpassing'
    regenerating = 'regenerating'
    restricted = 'restricted'
    unavailable = 'unavailable'
    auditing = 'auditing'

    readable_statuses = {
        downloadable: "already received",
        notpassing: "didn't receive",
        error: "error states"
    }


class CertificateSocialNetworks(object):
    """
    Enum for certificate social networks
    """
    linkedin = 'LinkedIn'
    facebook = 'Facebook'
    twitter = 'Twitter'


class CertificateWhitelist(models.Model):
    """
    Tracks students who are whitelisted, all users
    in this table will always qualify for a certificate
    regardless of their grade unless they are on the
    embargoed country restriction list
    (allow_certificate set to False in userprofile).
    """
    class Meta(object):
        app_label = "certificates"

    objects = NoneToEmptyManager()

    user = models.ForeignKey(User)
    course_id = CourseKeyField(max_length=255, blank=True, default=None)
    whitelist = models.BooleanField(default=0)
    created = CreationDateTimeField(_('created'))
    notes = models.TextField(default=None, null=True)

    @classmethod
    def get_certificate_white_list(cls, course_id, student=None):
        """
        Return certificate white list for the given course as dict object,
        returned dictionary will have the following key-value pairs

        [{
            id:         'id (pk) of CertificateWhitelist item'
            user_id:    'User Id of the student'
            user_name:  'name of the student'
            user_email: 'email of the student'
            course_id:  'Course key of the course to whom certificate exception belongs'
            created:    'Creation date of the certificate exception'
            notes:      'Additional notes for the certificate exception'
        }, {...}, ...]

        """
        white_list = cls.objects.filter(course_id=course_id, whitelist=True)
        if student:
            white_list = white_list.filter(user=student)
        result = []
        generated_certificates = GeneratedCertificate.objects.filter(
            course_id=course_id,
            user__in=[exception.user for exception in white_list],
            status=CertificateStatuses.downloadable
        )
        generated_certificates = {
            certificate['user']: certificate['created_date']
            for certificate in generated_certificates.values('user', 'created_date')
        }

        for item in white_list:
            certificate_generated = generated_certificates.get(item.user.id, '')
            result.append({
                'id': item.id,
                'user_id': item.user.id,
                'user_name': unicode(item.user.username),
                'user_email': unicode(item.user.email),
                'course_id': unicode(item.course_id),
                'created': item.created.strftime("%B %d, %Y"),
                'certificate_generated': certificate_generated and certificate_generated.strftime("%B %d, %Y"),
                'notes': unicode(item.notes or ''),
            })
        return result


class GeneratedCertificate(models.Model):
    """
    Base model for generated certificates
    """

    MODES = Choices('verified', 'honor', 'audit', 'professional', 'no-id-professional')

    VERIFIED_CERTS_MODES = [CourseMode.VERIFIED, CourseMode.CREDIT_MODE]

    user = models.ForeignKey(User)
    course_id = CourseKeyField(max_length=255, blank=True, default=None)
    verify_uuid = models.CharField(max_length=32, blank=True, default='', db_index=True)
    download_uuid = models.CharField(max_length=32, blank=True, default='')
    download_url = models.CharField(max_length=128, blank=True, default='')
    grade = models.CharField(max_length=5, blank=True, default='')
    key = models.CharField(max_length=32, blank=True, default='')
    distinction = models.BooleanField(default=False)
    status = models.CharField(max_length=32, default='unavailable')
    mode = models.CharField(max_length=32, choices=MODES, default=MODES.honor)
    name = models.CharField(blank=True, max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    error_reason = models.CharField(max_length=512, blank=True, default='')

    class Meta(object):
        unique_together = (('user', 'course_id'),)
        app_label = "certificates"

    @classmethod
    def certificate_for_student(cls, student, course_id):
        """
        This returns the certificate for a student for a particular course
        or None if no such certificate exits.
        """
        try:
            return cls.objects.get(user=student, course_id=course_id)
        except cls.DoesNotExist:
            pass

        return None

    @classmethod
    def get_unique_statuses(cls, course_key=None, flat=False):
        """
        1 - Return unique statuses as a list of dictionaries containing the following key value pairs
            [
            {'status': 'status value from db', 'count': 'occurrence count of the status'},
            {...},
            ..., ]

        2 - if flat is 'True' then return unique statuses as a list
        3 - if course_key is given then return unique statuses associated with the given course

        :param course_key: Course Key identifier
        :param flat: boolean showing whether to return statuses as a list of values or a list of dictionaries.
        """
        query = cls.objects

        if course_key:
            query = query.filter(course_id=course_key)

        if flat:
            return query.values_list('status', flat=True).distinct()
        else:
            return query.values('status').annotate(count=Count('status'))

    def invalidate(self):
        """
        Invalidate Generated Certificate by  marking it 'unavailable'.

        Following is the list of fields with their defaults
            1 - verify_uuid = '',
            2 - download_uuid = '',
            3 - download_url = '',
            4 - grade = ''
            5 - status = 'unavailable'
        """
        self.verify_uuid = ''
        self.download_uuid = ''
        self.download_url = ''
        self.grade = ''
        self.status = CertificateStatuses.unavailable

        self.save()


class CertificateGenerationHistory(TimeStampedModel):
    """
    Model for storing Certificate Generation History.
    """

    course_id = CourseKeyField(max_length=255)
    generated_by = models.ForeignKey(User)
    instructor_task = models.ForeignKey(InstructorTask)
    is_regeneration = models.BooleanField(default=False)

    def get_task_name(self):
        """
        Return "regenerated" if record corresponds to Certificate Regeneration task, otherwise returns 'generated'
        """
        return "regenerated" if self.is_regeneration else "generated"

    def get_certificate_generation_candidates(self):
        """
        Return the candidates for certificate generation task. It could either be students or certificate statuses
        depending upon the nature of certificate generation task. Returned value could be one of the following,

        1. "All learners" Certificate Generation task was initiated for all learners of the given course.
        2. Comma separated list of certificate statuses, This usually happens when instructor regenerates certificates.
        3. "for exceptions", This is the case when instructor generates certificates for white-listed
            students.
        """
        task_input = self.instructor_task.task_input
        try:
            task_input_json = json.loads(task_input)
        except ValueError:
            # if task input is empty, it means certificates were generated for all learners
            return "All learners"

        # get statuses_to_regenerate from task_input convert statuses to human readable strings and return
        statuses = task_input_json.get('statuses_to_regenerate', None)
        if statuses:
            return ", ".join(
                [CertificateStatuses.readable_statuses.get(status, "") for status in statuses]
            )

        # If statuses_to_regenerate is not present in task_input then, certificate generation task was run to
        # generate certificates for white listed students
        return "for exceptions"

    class Meta(object):
        app_label = "certificates"

    def __unicode__(self):
        return u"certificates %s by %s on %s for %s" % \
               ("regenerated" if self.is_regeneration else "generated", self.generated_by, self.created, self.course_id)


@receiver(post_save, sender=GeneratedCertificate)
def handle_post_cert_generated(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Handles post_save signal of GeneratedCertificate, and mark user collected
    course milestone entry if user has passed the course.
    User is assumed to have passed the course if certificate status is either 'generating' or 'downloadable'.
    """
    allowed_cert_states = [CertificateStatuses.generating, CertificateStatuses.downloadable]
    if is_prerequisite_courses_enabled() and instance.status in allowed_cert_states:
        fulfill_course_milestone(instance.course_id, instance.user)


def certificate_status_for_student(student, course_id):
    '''
    This returns a dictionary with a key for status, and other information.
    The status is one of the following:

    unavailable  - No entry for this student--if they are actually in
                   the course, they probably have not been graded for
                   certificate generation yet.
    generating   - A request has been made to generate a certificate,
                   but it has not been generated yet.
    regenerating - A request has been made to regenerate a certificate,
                   but it has not been generated yet.
    deleting     - A request has been made to delete a certificate.

    deleted      - The certificate has been deleted.
    downloadable - The certificate is available for download.
    notpassing   - The student was graded but is not passing
    restricted   - The student is on the restricted embargo list and
                   should not be issued a certificate. This will
                   be set if allow_certificate is set to False in
                   the userprofile table

    If the status is "downloadable", the dictionary also contains
    "download_url".

    If the student has been graded, the dictionary also contains their
    grade for the course with the key "grade".
    '''

    try:
        generated_certificate = GeneratedCertificate.objects.get(
            user=student, course_id=course_id)
        cert_status = {
            'status': generated_certificate.status,
            'mode': generated_certificate.mode,
            'uuid': generated_certificate.verify_uuid,
        }
        if generated_certificate.grade:
            cert_status['grade'] = generated_certificate.grade

        if generated_certificate.mode == 'audit':
            course_mode_slugs = [mode.slug for mode in CourseMode.modes_for_course(course_id)]
            # Short term fix to make sure old audit users with certs still see their certs
            # only do this if there if no honor mode
            if 'honor' not in course_mode_slugs:
                cert_status['status'] = CertificateStatuses.auditing
                return cert_status

        if generated_certificate.status == CertificateStatuses.downloadable:
            cert_status['download_url'] = generated_certificate.download_url

        return cert_status

    except GeneratedCertificate.DoesNotExist:
        pass
    return {'status': CertificateStatuses.unavailable, 'mode': GeneratedCertificate.MODES.honor, 'uuid': None}


def certificate_info_for_user(user, course_id, grade, user_is_whitelisted=None):
    """
    Returns the certificate info for a user for grade report.
    """
    if user_is_whitelisted is None:
        user_is_whitelisted = CertificateWhitelist.objects.filter(
            user=user, course_id=course_id, whitelist=True
        ).exists()

    certificate_is_delivered = 'N'
    certificate_type = 'N/A'
    eligible_for_certificate = 'Y' if (user_is_whitelisted or grade is not None) and user.profile.allow_certificate \
        else 'N'

    certificate_status = certificate_status_for_student(user, course_id)
    certificate_generated = certificate_status['status'] == CertificateStatuses.downloadable
    if certificate_generated:
        certificate_is_delivered = 'Y'
        certificate_type = certificate_status['mode']

    return [eligible_for_certificate, certificate_is_delivered, certificate_type]


class ExampleCertificateSet(TimeStampedModel):
    """A set of example certificates.

    Example certificates are used to verify that certificate
    generation is working for a particular course.

    A particular course may have several kinds of certificates
    (e.g. honor and verified), in which case we generate
    multiple example certificates for the course.

    """
    course_key = CourseKeyField(max_length=255, db_index=True)

    class Meta(object):
        get_latest_by = 'created'
        app_label = "certificates"

    @classmethod
    @transaction.atomic
    def create_example_set(cls, course_key):
        """Create a set of example certificates for a course.

        Arguments:
            course_key (CourseKey)

        Returns:
            ExampleCertificateSet

        """
        cert_set = cls.objects.create(course_key=course_key)

        ExampleCertificate.objects.bulk_create([
            ExampleCertificate(
                example_cert_set=cert_set,
                description=mode.slug,
                template=cls._template_for_mode(mode.slug, course_key)
            )
            for mode in CourseMode.modes_for_course(course_key)
        ])

        return cert_set

    @classmethod
    def latest_status(cls, course_key):
        """Summarize the latest status of example certificates for a course.

        Arguments:
            course_key (CourseKey)

        Returns:
            list: List of status dictionaries.  If no example certificates
                have been started yet, returns None.

        """
        try:
            latest = cls.objects.filter(course_key=course_key).latest()
        except cls.DoesNotExist:
            return None

        queryset = ExampleCertificate.objects.filter(example_cert_set=latest).order_by('-created')
        return [cert.status_dict for cert in queryset]

    def __iter__(self):
        """Iterate through example certificates in the set.

        Yields:
            ExampleCertificate

        """
        queryset = (ExampleCertificate.objects).select_related('example_cert_set').filter(example_cert_set=self)
        for cert in queryset:
            yield cert

    @staticmethod
    def _template_for_mode(mode_slug, course_key):
        """Calculate the template PDF based on the course mode. """
        return (
            u"certificate-template-{key.org}-{key.course}-verified.pdf".format(key=course_key)
            if mode_slug == 'verified'
            else u"certificate-template-{key.org}-{key.course}.pdf".format(key=course_key)
        )


def _make_uuid():
    """Return a 32-character UUID. """
    return uuid.uuid4().hex


class ExampleCertificate(TimeStampedModel):
    """Example certificate.

    Example certificates are used to verify that certificate
    generation is working for a particular course.

    An example certificate is similar to an ordinary certificate,
    except that:

    1) Example certificates are not associated with a particular user,
        and are never displayed to students.

    2) We store the "inputs" for generating the example certificate
        to make it easier to debug when certificate generation fails.

    3) We use dummy values.

    """
    class Meta(object):
        app_label = "certificates"

    # Statuses
    STATUS_STARTED = 'started'
    STATUS_SUCCESS = 'success'
    STATUS_ERROR = 'error'

    # Dummy full name for the generated certificate
    EXAMPLE_FULL_NAME = u'John Doë'

    example_cert_set = models.ForeignKey(ExampleCertificateSet)

    description = models.CharField(
        max_length=255,
        help_text=_(
            u"A human-readable description of the example certificate.  "
            u"For example, 'verified' or 'honor' to differentiate between "
            u"two types of certificates."
        )
    )

    # Inputs to certificate generation
    # We store this for auditing purposes if certificate
    # generation fails.
    uuid = models.CharField(
        max_length=255,
        default=_make_uuid,
        db_index=True,
        unique=True,
        help_text=_(
            u"A unique identifier for the example certificate.  "
            u"This is used when we receive a response from the queue "
            u"to determine which example certificate was processed."
        )
    )

    access_key = models.CharField(
        max_length=255,
        default=_make_uuid,
        db_index=True,
        help_text=_(
            u"An access key for the example certificate.  "
            u"This is used when we receive a response from the queue "
            u"to validate that the sender is the same entity we asked "
            u"to generate the certificate."
        )
    )

    full_name = models.CharField(
        max_length=255,
        default=EXAMPLE_FULL_NAME,
        help_text=_(u"The full name that will appear on the certificate.")
    )

    template = models.CharField(
        max_length=255,
        help_text=_(u"The template file to use when generating the certificate.")
    )

    # Outputs from certificate generation
    status = models.CharField(
        max_length=255,
        default=STATUS_STARTED,
        choices=(
            (STATUS_STARTED, 'Started'),
            (STATUS_SUCCESS, 'Success'),
            (STATUS_ERROR, 'Error')
        ),
        help_text=_(u"The status of the example certificate.")
    )

    error_reason = models.TextField(
        null=True,
        default=None,
        help_text=_(u"The reason an error occurred during certificate generation.")
    )

    download_url = models.CharField(
        max_length=255,
        null=True,
        default=None,
        help_text=_(u"The download URL for the generated certificate.")
    )

    def update_status(self, status, error_reason=None, download_url=None):
        """Update the status of the example certificate.

        This will usually be called either:
        1) When an error occurs adding the certificate to the queue.
        2) When we receieve a response from the queue (either error or success).

        If an error occurs, we store the error message;
        if certificate generation is successful, we store the URL
        for the generated certificate.

        Arguments:
            status (str): Either `STATUS_SUCCESS` or `STATUS_ERROR`

        Keyword Arguments:
            error_reason (unicode): A description of the error that occurred.
            download_url (unicode): The URL for the generated certificate.

        Raises:
            ValueError: The status is not a valid value.

        """
        if status not in [self.STATUS_SUCCESS, self.STATUS_ERROR]:
            msg = u"Invalid status: must be either '{success}' or '{error}'.".format(
                success=self.STATUS_SUCCESS,
                error=self.STATUS_ERROR
            )
            raise ValueError(msg)

        self.status = status

        if status == self.STATUS_ERROR and error_reason:
            self.error_reason = error_reason

        if status == self.STATUS_SUCCESS and download_url:
            self.download_url = download_url

        self.save()

    @property
    def status_dict(self):
        """Summarize the status of the example certificate.

        Returns:
            dict

        """
        result = {
            'description': self.description,
            'status': self.status,
        }

        if self.error_reason:
            result['error_reason'] = self.error_reason

        if self.download_url:
            result['download_url'] = self.download_url

        return result

    @property
    def course_key(self):
        """The course key associated with the example certificate. """
        return self.example_cert_set.course_key


class CertificateGenerationCourseSetting(TimeStampedModel):
    """Enable or disable certificate generation for a particular course.

    This controls whether students are allowed to "self-generate"
    certificates for a course.  It does NOT prevent us from
    batch-generating certificates for a course using management
    commands.

    In general, we should only enable self-generated certificates
    for a course once we successfully generate example certificates
    for the course.  This is enforced in the UI layer, but
    not in the data layer.

    """
    course_key = CourseKeyField(max_length=255, db_index=True)
    enabled = models.BooleanField(default=False)

    class Meta(object):
        get_latest_by = 'created'
        app_label = "certificates"

    @classmethod
    def is_enabled_for_course(cls, course_key):
        """Check whether self-generated certificates are enabled for a course.

        Arguments:
            course_key (CourseKey): The identifier for the course.

        Returns:
            boolean

        """
        try:
            latest = cls.objects.filter(course_key=course_key).latest()
        except cls.DoesNotExist:
            return False
        else:
            return latest.enabled

    @classmethod
    def set_enabled_for_course(cls, course_key, is_enabled):
        """Enable or disable self-generated certificates for a course.

        Arguments:
            course_key (CourseKey): The identifier for the course.
            is_enabled (boolean): Whether to enable or disable self-generated certificates.

        """
        CertificateGenerationCourseSetting.objects.create(
            course_key=course_key,
            enabled=is_enabled
        )


class CertificateGenerationConfiguration(ConfigurationModel):
    """Configure certificate generation.

    Enable or disable the self-generated certificates feature.
    When this flag is disabled, the "generate certificate" button
    will be hidden on the progress page.

    When the feature is enabled, the "generate certificate" button
    will appear for courses that have enabled self-generated
    certificates.

    """
    class Meta(ConfigurationModel.Meta):
        app_label = "certificates"


class CertificateHtmlViewConfiguration(ConfigurationModel):
    """
    Static values for certificate HTML view context parameters.
    Default values will be applied across all certificate types (course modes)
    Matching 'mode' overrides will be used instead of defaults, where applicable
    Example configuration :
        {
            "default": {
                "url": "http://www.edx.org",
                "logo_src": "http://www.edx.org/static/images/logo.png"
            },
            "honor": {
                "logo_src": "http://www.edx.org/static/images/honor-logo.png"
            }
        }
    """
    class Meta(ConfigurationModel.Meta):
        app_label = "certificates"

    configuration = models.TextField(
        help_text="Certificate HTML View Parameters (JSON)"
    )

    def clean(self):
        """
        Ensures configuration field contains valid JSON.
        """
        try:
            json.loads(self.configuration)
        except ValueError:
            raise ValidationError('Must be valid JSON string.')

    @classmethod
    def get_config(cls):
        """
        Retrieves the configuration field value from the database
        """
        instance = cls.current()
        json_data = json.loads(instance.configuration) if instance.enabled else {}
        return json_data


class BadgeAssertion(models.Model):
    """
    Tracks badges on our side of the badge baking transaction
    """
    user = models.ForeignKey(User)
    course_id = CourseKeyField(max_length=255, blank=True, default=None)
    # Mode a badge was awarded for.
    mode = models.CharField(max_length=100)
    data = JSONField()

    @property
    def image_url(self):
        """
        Get the image for this assertion.
        """

        return self.data['image']

    @property
    def assertion_url(self):
        """
        Get the public URL for the assertion.
        """
        return self.data['json']['id']

    class Meta(object):
        unique_together = (('course_id', 'user', 'mode'),)
        app_label = "certificates"


def validate_badge_image(image):
    """
    Validates that a particular image is small enough, of the right type, and square to be a badge.
    """
    if image.width != image.height:
        raise ValidationError(_(u"The badge image must be square."))
    if not image.size < (250 * 1024):
        raise ValidationError(_(u"The badge image file size must be less than 250KB."))


class BadgeImageConfiguration(models.Model):
    """
    Contains the configuration for badges for a specific mode. The mode
    """
    class Meta(object):
        app_label = "certificates"

    mode = models.CharField(
        max_length=125,
        help_text=_(u'The course mode for this badge image. For example, "verified" or "honor".'),
        unique=True,
    )
    icon = models.ImageField(
        # Actual max is 256KB, but need overhead for badge baking. This should be more than enough.
        help_text=_(
            u"Badge images must be square PNG files. The file size should be under 250KB."
        ),
        upload_to='badges',
        validators=[validate_badge_image]
    )
    default = models.BooleanField(
        default=False,
        help_text=_(
            u"Set this value to True if you want this image to be the default image for any course modes "
            u"that do not have a specified badge image. You can have only one default image."
        )
    )

    def clean(self):
        """
        Make sure there's not more than one default.
        """
        if self.default and BadgeImageConfiguration.objects.filter(default=True).exclude(id=self.id):
            raise ValidationError(_(u"There can be only one default image."))

    @classmethod
    def image_for_mode(cls, mode):
        """
        Get the image for a particular mode.
        """
        try:
            return cls.objects.get(mode=mode).icon
        except cls.DoesNotExist:
            # Fall back to default, if there is one.
            return cls.objects.get(default=True).icon


class CertificateTemplate(TimeStampedModel):
    """A set of custom web certificate templates.

    Web certificate templates are Django web templates
    to replace PDF certificate.

    A particular course may have several kinds of certificate templates
    (e.g. honor and verified).

    """
    name = models.CharField(
        max_length=255,
        help_text=_(u'Name of template.'),
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_(u'Description and/or admin notes.'),
    )
    template = models.TextField(
        help_text=_(u'Django template HTML.'),
    )
    organization_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_(u'Organization of template.'),
    )
    course_key = CourseKeyField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    mode = models.CharField(
        max_length=125,
        choices=GeneratedCertificate.MODES,
        default=GeneratedCertificate.MODES.honor,
        null=True,
        blank=True,
        help_text=_(u'The course mode for this template.'),
    )
    is_active = models.BooleanField(
        help_text=_(u'On/Off switch.'),
        default=False,
    )

    def __unicode__(self):
        return u'%s' % (self.name, )

    class Meta(object):
        get_latest_by = 'created'
        unique_together = (('organization_id', 'course_key', 'mode'),)
        app_label = "certificates"


def template_assets_path(instance, filename):
    """
    Delete the file if it already exist and returns the certificate template asset file path.

    :param instance: CertificateTemplateAsset object
    :param filename: file to upload
    :return path: path of asset file e.g. certificate_template_assets/1/filename
    """
    name = os.path.join('certificate_template_assets', str(instance.id), filename)
    fullname = os.path.join(settings.MEDIA_ROOT, name)
    if os.path.exists(fullname):
        os.remove(fullname)
    return name


class CertificateTemplateAsset(TimeStampedModel):
    """A set of assets to be used in custom web certificate templates.

    This model stores assets used in custom web certificate templates
    such as image, css files.

    """
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_(u'Description of the asset.'),
    )
    asset = models.FileField(
        max_length=255,
        upload_to=template_assets_path,
        help_text=_(u'Asset file. It could be an image or css file.'),
    )

    def save(self, *args, **kwargs):
        """save the certificate template asset """
        if self.pk is None:
            asset_image = self.asset
            self.asset = None
            super(CertificateTemplateAsset, self).save(*args, **kwargs)
            self.asset = asset_image

        super(CertificateTemplateAsset, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (self.asset.url, )

    class Meta(object):
        get_latest_by = 'created'
        app_label = "certificates"


@receiver(post_save, sender=GeneratedCertificate)
#pylint: disable=unused-argument
def create_badge(sender, instance, **kwargs):
    """
    Standard signal hook to create badges when a certificate has been generated.
    """
    if not settings.FEATURES.get('ENABLE_OPENBADGES', False):
        return
    if not modulestore().get_course(instance.course_id).issue_badges:
        LOGGER.info("Course is not configured to issue badges.")
        return
    if BadgeAssertion.objects.filter(user=instance.user, course_id=instance.course_id):
        LOGGER.info("Badge already exists for this user on this course.")
        # Badge already exists. Skip.
        return
    # Don't bake a badge until the certificate is available. Prevents user-facing requests from being paused for this
    # by making sure it only gets run on the callback during normal workflow.
    if not instance.status == CertificateStatuses.downloadable:
        return
    from .badge_handler import BadgeHandler
    handler = BadgeHandler(instance.course_id)
    handler.award(instance.user)
