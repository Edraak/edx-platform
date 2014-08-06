from .test import *
from uuid import uuid4
import os


THIS_UUID = uuid4().hex[:5]
MONGO_PORT_NUM = os.environ.get('EDXAPP_TEST_MONGO_PORT', '27017')

for k in CACHES:
    CACHES[k]['KEY_PREFIX'] = "{}{}".format(CACHES[k].get('KEY_PREFIX', ''), THIS_UUID)

update_module_store_settings(
    MODULESTORE,
    doc_store_settings={
        'port': int(MONGO_PORT_NUM),
        'db': 'test_xmodule{0}'.format(THIS_UUID),
        'collection': 'test_modulestore{0}'.format(THIS_UUID),
    },
)

CONTENTSTORE['DOC_STORE_CONFIG']['db'] = 'test_xcontent{0}'.format(THIS_UUID)
CONTENTSTORE['DOC_STORE_CONFIG']['port'] = int(MONGO_PORT_NUM)

MONGODB_LOG = {
    'host': 'localhost',
    'port': int(MONGO_PORT_NUM),
    'user': '',
    'password': '',
    'db': 'xlog',
}
