from .dev import *
from path import path
import os
from django.core.exceptions import ImproperlyConfigured
"""
A Django settings file for use on jenkins while running or checking
database migrations. It uses the dev settings as a base so that
so a full aws configueration is not required.
"""

LOGGING = get_logger_config(path("/var/tmp"),
                            logging_env="dev",
                            local_loglevel="DEBUG",
                            dev_env=True,
                            debug=True)
DB_OVERRIDES = dict(
    PASSWORD=os.environ.get('DB_MIGRATION_PASS', None),
    ENGINE=os.environ.get('DB_MIGRATION_ENGINE', 'django.db.backends.mysql'),
    USER=os.environ.get('DB_MIGRATION_USER', 'root'),
    NAME=os.environ.get('DB_MIGRATION_NAME', 'edxapp'),
    HOST=os.environ.get('DB_MIGRATION_HOST', '127.0.0.1'),
    PORT=os.environ.get('DB_MIGRATION_PORT', '3306'),
)

if DB_OVERRIDES['PASSWORD'] is None:
    raise ImproperlyConfigured("No database password was provided for running "
                               "migrations.  This is fatal.")
for override, value in DB_OVERRIDES.iteritems():
    DATABASES['default'][override] = value
