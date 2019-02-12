# -*- coding: utf-8 -*-
"""
This config file runs the simplest dev environment using sqlite, and db-based
sessions. Assumes structure:

/envroot/
        /db   # This is where it'll write the database file
        /edx-platform  # The location of this repo
        /log  # Where we're going to write log files
"""

# We intentionally define lots of variables that aren't used, and
# want to import all variables from base settings files
# pylint: disable=wildcard-import, unused-wildcard-import

# Pylint gets confused by path.py instances, which report themselves as class
# objects. As a result, pylint applies the wrong regex in validating names,
# and throws spurious errors. Therefore, we disable invalid-name checking.
# pylint: disable=invalid-name

from .common import *
import os
from path import Path as path
from uuid import uuid4
from warnings import filterwarnings, simplefilter

from openedx.core.lib.tempdir import mkdtemp_clean

# This patch disabes the commit_on_success decorator during tests
# in TestCase subclasses.
from util.testing import patch_testcase
patch_testcase()

# Silence noisy logs to make troubleshooting easier when tests fail.
import logging
LOG_OVERRIDES = [
    ('factory.generate', logging.ERROR),
    ('factory.containers', logging.ERROR),
]
for log_name, log_level in LOG_OVERRIDES:
    logging.getLogger(log_name).setLevel(log_level)


def suppress_test_debug_log():
    if os.environ.get('SUPPRESS_TEST_DEBUG_LOG'):
        logging.disable(logging.INFO)
        print 'SUPPRESS_TEST_DEBUG_LOG is set, suppressing debug messages.'

suppress_test_debug_log()

# mongo connection settings
MONGO_PORT_NUM = int(os.environ.get('EDXAPP_TEST_MONGO_PORT', '27017'))
MONGO_HOST = os.environ.get('EDXAPP_TEST_MONGO_HOST', 'localhost')

os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = 'localhost:8000-9000'

THIS_UUID = uuid4().hex[:5]

# can't test start dates with this True, but on the other hand,
# can test everything else :)
FEATURES['DISABLE_START_DATES'] = True

# Most tests don't use the discussion service, so we turn it off to speed them up.
# Tests that do can enable this flag, but must use the UrlResetMixin class to force urls.py
# to reload. For consistency in user-experience, keep the value of this setting in sync with
# the one in cms/envs/test.py
FEATURES['ENABLE_DISCUSSION_SERVICE'] = False

FEATURES['ENABLE_SERVICE_STATUS'] = True

FEATURES['ENABLE_HINTER_INSTRUCTOR_VIEW'] = True

FEATURES['ENABLE_INSTRUCTOR_LEGACY_DASHBOARD'] = True

FEATURES['ENABLE_SHOPPING_CART'] = True

FEATURES['ENABLE_VERIFIED_CERTIFICATES'] = True

# Enable this feature for course staff grade downloads, to enable acceptance tests
FEATURES['ENABLE_S3_GRADE_DOWNLOADS'] = True
FEATURES['ALLOW_COURSE_STAFF_GRADE_DOWNLOADS'] = True

# Toggles embargo on for testing
FEATURES['EMBARGO'] = True

FEATURES['ENABLE_COMBINED_LOGIN_REGISTRATION'] = True

# Need wiki for courseware views to work. TODO (vshnayder): shouldn't need it.
WIKI_ENABLED = True

# Enable a parental consent age limit for testing
PARENTAL_CONSENT_AGE_LIMIT = 13

# Makes the tests run much faster...
SOUTH_TESTS_MIGRATE = False  # To disable migrations and use syncdb instead

# Nose Test Runner
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

_SYSTEM = 'lms'

_REPORT_DIR = REPO_ROOT / 'reports' / _SYSTEM
_REPORT_DIR.makedirs_p()
_NOSEID_DIR = REPO_ROOT / '.testids' / _SYSTEM
_NOSEID_DIR.makedirs_p()

NOSE_ARGS = [
    '--id-file', _NOSEID_DIR / 'noseids',
    '--xunit-file', _REPORT_DIR / 'nosetests.xml',
]

# Local Directories
TEST_ROOT = path("test_root")
# Want static files in the same dir for running on jenkins.
STATIC_ROOT = TEST_ROOT / "staticfiles"

STATUS_MESSAGE_PATH = TEST_ROOT / "status_message.json"

COURSES_ROOT = TEST_ROOT / "data"
DATA_DIR = COURSES_ROOT

COMMON_TEST_DATA_ROOT = COMMON_ROOT / "test" / "data"
# Where the content data is checked out.  This may not exist on jenkins.
GITHUB_REPO_ROOT = ENV_ROOT / "data"

USE_I18N = True
LANGUAGE_CODE = 'en'  # tests assume they will get English.

XQUEUE_INTERFACE = {
    "url": "http://sandbox-xqueue.edx.org",
    "django_auth": {
        "username": "lms",
        "password": "***REMOVED***"
    },
    "basic_auth": ('anant', 'agarwal'),
}
XQUEUE_WAITTIME_BETWEEN_REQUESTS = 5  # seconds

# Don't rely on a real staff grading backend
MOCK_STAFF_GRADING = True
MOCK_PEER_GRADING = True

############################ STATIC FILES #############################

# TODO (cpennington): We need to figure out how envs/test.py can inject things
# into common.py so that we don't have to repeat this sort of thing
STATICFILES_DIRS = [
    COMMON_ROOT / "static",
    PROJECT_ROOT / "static",
]
STATICFILES_DIRS += [
    (course_dir, COMMON_TEST_DATA_ROOT / course_dir)
    for course_dir in os.listdir(COMMON_TEST_DATA_ROOT)
    if os.path.isdir(COMMON_TEST_DATA_ROOT / course_dir)
]

# Avoid having to run collectstatic before the unit test suite
# If we don't add these settings, then Django templates that can't
# find pipelined assets will raise a ValueError.
# http://stackoverflow.com/questions/12816941/unit-testing-with-django-pipeline
STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

# Don't use compression during tests
PIPELINE_JS_COMPRESSOR = None

update_module_store_settings(
    MODULESTORE,
    module_store_options={
        'fs_root': TEST_ROOT / "data",
    },
    xml_store_options={
        'data_dir': mkdtemp_clean(dir=TEST_ROOT),  # never inadvertently load all the XML courses
    },
    doc_store_settings={
        'host': MONGO_HOST,
        'port': MONGO_PORT_NUM,
        'db': 'test_xmodule',
        'collection': 'test_modulestore{0}'.format(THIS_UUID),
    },
)

CONTENTSTORE = {
    'ENGINE': 'xmodule.contentstore.mongo.MongoContentStore',
    'DOC_STORE_CONFIG': {
        'host': MONGO_HOST,
        'db': 'xcontent',
        'port': MONGO_PORT_NUM,
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': TEST_ROOT / 'db' / 'edx.db',
        'ATOMIC_REQUESTS': True,
    },

}

# This hack disables migrations during tests. We want to create tables directly from the models for speed.
# See https://groups.google.com/d/msg/django-developers/PWPj3etj3-U/kCl6pMsQYYoJ.
MIGRATION_MODULES = {app: "app.migrations_not_used_in_tests" for app in INSTALLED_APPS}

CACHES = {
    # This is the cache used for most things.
    # In staging/prod envs, the sessions also live here.
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'edx_loc_mem_cache',
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },

    # The general cache is what you get if you use our util.cache. It's used for
    # things like caching the course.xml file for different A/B test groups.
    # We set it to be a DummyCache to force reloading of course.xml in dev.
    # In staging environments, we would grab VERSION from data uploaded by the
    # push process.
    'general': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'KEY_PREFIX': 'general',
        'VERSION': 4,
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },

    'mongo_metadata_inheritance': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': os.path.join(tempfile.gettempdir(), 'mongo_metadata_inheritance'),
        'TIMEOUT': 300,
        'KEY_FUNCTION': 'util.memcache.safe_key',
    },
    'loc_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'edx_location_mem_cache',
    },
    'course_structure_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'block_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'edx_location_block_cache',
    },
    'lms.course_blocks': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'edx_location_course_blocks',
    },
}

# Dummy secret key for dev
SECRET_KEY = '85920908f28904ed733fe576320db18cabd7b6cd'

# hide ratelimit warnings while running tests
filterwarnings('ignore', message='No request passed to the backend, unable to rate-limit')

# Ignore deprecation warnings (so we don't clutter Jenkins builds/production)
# https://docs.python.org/2/library/warnings.html#the-warnings-filter
# Change to "default" to see the first instance of each hit
# or "error" to convert all into errors
simplefilter('ignore')

############################# SECURITY SETTINGS ################################
# Default to advanced security in common.py, so tests can reset here to use
# a simpler security model
FEATURES['ENFORCE_PASSWORD_POLICY'] = False
FEATURES['ENABLE_MAX_FAILED_LOGIN_ATTEMPTS'] = False
FEATURES['SQUELCH_PII_IN_LOGS'] = False
FEATURES['PREVENT_CONCURRENT_LOGINS'] = False
FEATURES['ADVANCED_SECURITY'] = False
PASSWORD_MIN_LENGTH = None
PASSWORD_COMPLEXITY = {}

######### Third-party auth ##########
FEATURES['ENABLE_THIRD_PARTY_AUTH'] = True

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'third_party_auth.dummy.DummyBackend',
    'third_party_auth.saml.SAMLAuthBackend',
    'third_party_auth.lti.LTIAuthBackend',
) + AUTHENTICATION_BACKENDS

THIRD_PARTY_AUTH_CUSTOM_AUTH_FORMS = {
    'custom1': {
        'secret_key': 'opensesame',
        'url': '/misc/my-custom-registration-form',
        'error_url': '/misc/my-custom-sso-error-page'
    },
}

################################## OPENID #####################################
FEATURES['AUTH_USE_OPENID'] = True
FEATURES['AUTH_USE_OPENID_PROVIDER'] = True

################################## SHIB #######################################
FEATURES['AUTH_USE_SHIB'] = True
FEATURES['SHIB_DISABLE_TOS'] = True
FEATURES['RESTRICT_ENROLL_BY_REG_METHOD'] = True

OPENID_CREATE_USERS = False
OPENID_UPDATE_DETAILS_FROM_SREG = True
OPENID_USE_AS_ADMIN_LOGIN = False
OPENID_PROVIDER_TRUSTED_ROOTS = ['*']

############################## OAUTH2 Provider ################################
FEATURES['ENABLE_OAUTH2_PROVIDER'] = True
# don't cache courses for testing
OIDC_COURSE_HANDLER_CACHE_TIMEOUT = 0

########################### External REST APIs #################################
FEATURES['ENABLE_MOBILE_REST_API'] = True
FEATURES['ENABLE_VIDEO_ABSTRACTION_LAYER_API'] = True
FEATURES['ENABLE_COURSE_BLOCKS_NAVIGATION_API'] = True

###################### Payment ##############################3
# Enable fake payment processing page
FEATURES['ENABLE_PAYMENT_FAKE'] = True

# Configure the payment processor to use the fake processing page
# Since both the fake payment page and the shoppingcart app are using
# the same settings, we can generate this randomly and guarantee
# that they are using the same secret.
from random import choice
from string import letters, digits, punctuation
RANDOM_SHARED_SECRET = ''.join(
    choice(letters + digits + punctuation)
    for x in range(250)
)

CC_PROCESSOR_NAME = 'CyberSource2'
CC_PROCESSOR['CyberSource2']['SECRET_KEY'] = RANDOM_SHARED_SECRET
CC_PROCESSOR['CyberSource2']['ACCESS_KEY'] = "0123456789012345678901"
CC_PROCESSOR['CyberSource2']['PROFILE_ID'] = "edx"
CC_PROCESSOR['CyberSource2']['PURCHASE_ENDPOINT'] = "/shoppingcart/payment_fake"

FEATURES['STORE_BILLING_INFO'] = True

########################### SYSADMIN DASHBOARD ################################
FEATURES['ENABLE_SYSADMIN_DASHBOARD'] = True
GIT_REPO_DIR = TEST_ROOT / "course_repos"

################################# CELERY ######################################

CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'djcelery.backends.cache:CacheBackend'

######################### MARKETING SITE ###############################

MKTG_URL_LINK_MAP = {
    'ABOUT': 'about',
    'CONTACT': 'contact',
    'HELP_CENTER': 'help-center',
    'COURSES': 'courses',
    'ROOT': 'root',
    'TOS': 'tos',
    'HONOR': 'honor',
    'PRIVACY': 'privacy',
    'CAREERS': 'careers',
    'NEWS': 'news',
    'PRESS': 'press',
    'BLOG': 'blog',
    'DONATE': 'donate',

    # Verified Certificates
    'WHAT_IS_VERIFIED_CERT': 'verified-certificate',
}

SUPPORT_SITE_LINK = 'https://support.example.com'

############################ STATIC FILES #############################
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = TEST_ROOT / "uploads"
MEDIA_URL = "/static/uploads/"
STATICFILES_DIRS.append(("uploads", MEDIA_ROOT))

_NEW_STATICFILES_DIRS = []
# Strip out any static files that aren't in the repository root
# so that the tests can run with only the edx-platform directory checked out
for static_dir in STATICFILES_DIRS:
    # Handle both tuples and non-tuple directory definitions
    try:
        _, data_dir = static_dir
    except ValueError:
        data_dir = static_dir

    if data_dir.startswith(REPO_ROOT):
        _NEW_STATICFILES_DIRS.append(static_dir)
STATICFILES_DIRS = _NEW_STATICFILES_DIRS

FILE_UPLOAD_TEMP_DIR = TEST_ROOT / "uploads"
FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

########################### Server Ports ###################################

# These ports are carefully chosen so that if the browser needs to
# access them, they will be available through the SauceLabs SSH tunnel
LETTUCE_SERVER_PORT = 8003
XQUEUE_PORT = 8040
YOUTUBE_PORT = 8031
LTI_PORT = 8765
VIDEO_SOURCE_PORT = 8777

################### Make tests faster

#http://slacy.com/blog/2012/04/make-your-tests-faster-in-django-1-4/
PASSWORD_HASHERS = (
    # 'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    # 'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    # 'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    # 'django.contrib.auth.hashers.CryptPasswordHasher',
)

### This enables the Metrics tab for the Instructor dashboard ###########
FEATURES['CLASS_DASHBOARD'] = True

################### Make tests quieter

# OpenID spews messages like this to stderr, we don't need to see them:
#   Generated checkid_setup request to http://testserver/openid/provider/login/ with assocication {HMAC-SHA1}{51d49995}{s/kRmA==}

import openid.oidutil
openid.oidutil.log = lambda message, level=0: None

PLATFORM_NAME = "edX"
SITE_NAME = "edx.org"

# set up some testing for microsites
MICROSITE_CONFIGURATION = {
    "test_microsite": {
        "domain_prefix": "testmicrosite",
        "university": "test_microsite",
        "platform_name": "Test Microsite",
        "logo_image_url": "test_microsite/images/header-logo.png",
        "email_from_address": "test_microsite@edx.org",
        "payment_support_email": "test_microsite@edx.org",
        "ENABLE_MKTG_SITE": False,
        "SITE_NAME": "test_microsite.localhost",
        "course_org_filter": "TestMicrositeX",
        "course_about_show_social_links": False,
        "css_overrides_file": "test_microsite/css/test_microsite.css",
        "show_partners": False,
        "show_homepage_promo_video": False,
        "course_index_overlay_text": "This is a Test Microsite Overlay Text.",
        "course_index_overlay_logo_file": "test_microsite/images/header-logo.png",
        "homepage_overlay_html": "<h1>This is a Test Microsite Overlay HTML</h1>",
        "ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER": False,
        "COURSE_CATALOG_VISIBILITY_PERMISSION": "see_in_catalog",
        "COURSE_ABOUT_VISIBILITY_PERMISSION": "see_about_page",
        "ENABLE_SHOPPING_CART": True,
        "ENABLE_PAID_COURSE_REGISTRATION": True,
        "SESSION_COOKIE_DOMAIN": "test_microsite.localhost",
    },
    "microsite_with_logistration": {
        "domain_prefix": "logistration",
        "university": "logistration",
        "platform_name": "Test logistration",
        "logo_image_url": "test_microsite/images/header-logo.png",
        "email_from_address": "test_microsite@edx.org",
        "payment_support_email": "test_microsite@edx.org",
        "ENABLE_MKTG_SITE": False,
        "ENABLE_COMBINED_LOGIN_REGISTRATION": True,
        "SITE_NAME": "test_microsite.localhost",
        "course_org_filter": "LogistrationX",
        "course_about_show_social_links": False,
        "css_overrides_file": "test_microsite/css/test_microsite.css",
        "show_partners": False,
        "show_homepage_promo_video": False,
        "course_index_overlay_text": "Logistration.",
        "course_index_overlay_logo_file": "test_microsite/images/header-logo.png",
        "homepage_overlay_html": "<h1>This is a Logistration HTML</h1>",
        "ALWAYS_REDIRECT_HOMEPAGE_TO_DASHBOARD_FOR_AUTHENTICATED_USER": False,
        "COURSE_CATALOG_VISIBILITY_PERMISSION": "see_in_catalog",
        "COURSE_ABOUT_VISIBILITY_PERMISSION": "see_about_page",
        "ENABLE_SHOPPING_CART": True,
        "ENABLE_PAID_COURSE_REGISTRATION": True,
        "SESSION_COOKIE_DOMAIN": "test_logistration.localhost",
    },
    "default": {
        "university": "default_university",
        "domain_prefix": "www",
    }
}
MICROSITE_ROOT_DIR = COMMON_ROOT / 'test' / 'test_microsites'
MICROSITE_TEST_HOSTNAME = 'testmicrosite.testserver'
MICROSITE_LOGISTRATION_HOSTNAME = 'logistration.testserver'

FEATURES['USE_MICROSITES'] = True

# add extra template directory for test-only templates
MAKO_TEMPLATES['main'].extend([
    COMMON_ROOT / 'test' / 'templates'
])


# Setting for the testing of Software Secure Result Callback
VERIFY_STUDENT["SOFTWARE_SECURE"] = {
    "API_ACCESS_KEY": "BBBBBBBBBBBBBBBBBBBB",
    "API_SECRET_KEY": "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
}

VIDEO_CDN_URL = {
    'CN': 'http://api.xuetangx.com/edx/video?s3_url='
}

######### dashboard git log settings #########
MONGODB_LOG = {
    'host': MONGO_HOST,
    'port': MONGO_PORT_NUM,
    'user': '',
    'password': '',
    'db': 'xlog',
}

# ForUs variables
FORUS_AUTH_SECRET_KEY = 'dummy_auth_secret_key'
FORUS_BASE_URL = 'http://forus.jo'

# Enable EdxNotes for tests.
FEATURES['ENABLE_EDXNOTES'] = True

# Enable teams feature for tests.
FEATURES['ENABLE_TEAMS'] = True

# Enable courseware search for tests
FEATURES['ENABLE_COURSEWARE_SEARCH'] = True

# Enable dashboard search for tests
FEATURES['ENABLE_DASHBOARD_SEARCH'] = True

# Use MockSearchEngine as the search engine for test scenario
SEARCH_ENGINE = "search.tests.mock_search_engine.MockSearchEngine"

FACEBOOK_APP_SECRET = "Test"
FACEBOOK_APP_ID = "Test"
FACEBOOK_API_VERSION = "v2.8"

######### custom courses #########
INSTALLED_APPS += ('lms.djangoapps.ccx',)
FEATURES['CUSTOM_COURSES_EDX'] = True

# Set dummy values for profile image settings.
PROFILE_IMAGE_BACKEND = {
    'class': 'storages.backends.overwrite.OverwriteStorage',
    'options': {
        'location': MEDIA_ROOT,
        'base_url': 'http://example-storage.com/profile-images/',
    },
}
PROFILE_IMAGE_DEFAULT_FILENAME = 'default'
PROFILE_IMAGE_DEFAULT_FILE_EXTENSION = 'png'
PROFILE_IMAGE_SECRET_KEY = 'secret'
PROFILE_IMAGE_MAX_BYTES = 1024 * 1024
PROFILE_IMAGE_MIN_BYTES = 100

# Enable the LTI provider feature for testing
FEATURES['ENABLE_LTI_PROVIDER'] = True
INSTALLED_APPS += ('lti_provider',)
AUTHENTICATION_BACKENDS += ('lti_provider.users.LtiBackend',)

# ORGANIZATIONS
FEATURES['ORGANIZATIONS_APP'] = True

# Financial assistance page
FEATURES['ENABLE_FINANCIAL_ASSISTANCE_FORM'] = True
