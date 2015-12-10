from .dev import *

FEATURES['AUTH_USE_CERTIFICATES'] = False

VIRTUAL_UNIVERSITIES = ['edge']
META_UNIVERSITIES = {}

PIPELINE_ENABLED = False


SESSION_COOKIE_DOMAIN = '.local.edx.org'
CSRF_COOKIE_DOMAIN = '.local.edx.org'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'mysql',
        'NAME': 'edxapp',
        'PASSWORD': 'password',
        'USER': 'root'
    }
}



CONTENTSTORE = {
    'ADDITIONAL_OPTIONS': {},
    'DOC_STORE_CONFIG': {
        'collection': 'modulestore',
        'db': 'edxapp',
        'host': [
            'mongo'
        ],
    },
    'ENGINE': 'xmodule.contentstore.mongo.MongoContentStore',
    'OPTIONS': {
        'db': 'edxapp',
        'host': [
            'mongo'
        ],
    }
}

MODULESTORE = {
    'default': {
        'ENGINE': 'xmodule.modulestore.mixed.MixedModuleStore',
        'OPTIONS': {
            'mappings': {},
            'stores': [{
                'DOC_STORE_CONFIG': {
                    'collection': 'modulestore',
                    'db': 'edxapp',
                    'host': [
                        'mongo'
                    ]
                },
                'ENGINE': 'xmodule.modulestore.mongo.DraftMongoModuleStore',
                'NAME': 'draft',
                'OPTIONS': {
                    'default_class': 'xmodule.hidden_module.HiddenDescriptor',
                    'fs_root': '/edx/var/edxapp/data',
                    'render_template': 'edxmako.shortcuts.render_to_string'
                }
            }, {
                'ENGINE': 'xmodule.modulestore.xml.XMLModuleStore',
                'NAME': 'xml',
                'OPTIONS': {
                    'data_dir': '/edx/var/edxapp/data',
                    'default_class': 'xmodule.hidden_module.HiddenDescriptor'
                }
            }, {
                'DOC_STORE_CONFIG': {
                    'collection': 'modulestore',
                    'db': 'edxapp',
                    'host': [
                        'mongo'
                    ],
                },
                'ENGINE': 'xmodule.modulestore.split_mongo.split_draft.DraftVersioningModuleStore',
                'NAME': 'split',
                'OPTIONS': {
                    'default_class': 'xmodule.hidden_module.HiddenDescriptor',
                    'fs_root': '/edx/var/edxapp/data',
                    'render_template': 'edxmako.shortcuts.render_to_string'
                }
            }]
        }
    }
}

CACHES = {
    'celery': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_FUNCTION': 'util.memcache.safe_key',
        'KEY_PREFIX': 'celery',
        'LOCATION': [
            'memcached:11211'
        ],
        'TIMEOUT': '7200'
    },
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_FUNCTION': 'util.memcache.safe_key',
        'KEY_PREFIX': 'default',
        'LOCATION': [
            'memcached:11211'
        ]
    },
    'general': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_FUNCTION': 'util.memcache.safe_key',
        'KEY_PREFIX': 'general',
        'LOCATION': [
            'memcached:11211'
        ]
    },
    'mongo_metadata_inheritance': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'KEY_FUNCTION': 'util.memcache.safe_key',
        'KEY_PREFIX': 'mongo_metadata_inheritance',
        'LOCATION': [
            'memcached:11211'
        ],
        'TIMEOUT': '300'
    },
    "staticfiles": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "util.memcache.safe_key",
        "KEY_PREFIX": "staticfiles",
        "LOCATION": [
            'memcached:11211'
        ]
    }
}
