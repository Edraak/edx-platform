import pymongo

from xmodule.modulestore import Location
from xmodule.modulestore.locator import Locator
from test_split_modulestore import modulestore as split_store
from test_mongo import TestMongoModuleStore, TestMongoKeyValueStore
from test_xml import TestXMLModuleStore

HOST = 'localhost'
PORT = 27017
DB = 'test_mongo_%s' % uuid4().hex
COLLECTION = 'modulestore'
FS_ROOT = DATA_DIR

OPTIONS = {
    'mappings': {
        XML_COURSEID1: 'xml',
        XML_COURSEID2: 'xml',
        IMPORT_COURSEID: 'default'
    },
    'stores': {
        'xml': {
            'ENGINE': 'xmodule.modulestore.xml.XMLModuleStore',
            'OPTIONS': {
                'data_dir': DATA_DIR,
                'default_class': 'xmodule.hidden_module.HiddenDescriptor',
            }
        },

        'mongo': {
            'ENGINE': 'xmodule.modulestore.mongo.MongoModuleStore',
            'DOC_STORE_CONFIG': {
                'host': HOST,
                'db': DB,
                'collection': COLLECTION,
            },
            'OPTIONS': {
                'default_class': DEFAULT_CLASS,
                'fs_root': DATA_DIR,
                'render_template': RENDER_TEMPLATE,
            }
        }

        'split': {
            'ENGINE': 'xmodule.modulestore.split_mongo.SplitMongoModuleStore',
            'DOC_STORE_CONFIG': {         
                'host': 'localhost',
                'db': 'test_xmodule',
                'collection': 'modulestore{0}'.format(uuid.uuid4().hex),
            },
            'OPTIONS': {
                'default_class': 'xmodule.raw_module.RawDescriptor',
                'fs_root': '',
                'xblock_mixins': (InheritanceMixin, XModuleMixin)
            }
        }
    }
}

class TestHierarchyStore(object):
    @classmethod
    def setupClass(cls):
        """
        Set up the database for testing
        """
        cls.connection = pymongo.connection.Connection(HOST, PORT)
        cls.connection.drop_database(DB)
        cls.fake_location = Location(['i4x', 'foo', 'bar', 'vertical', 'baz'])
        cls.import_org, cls.import_course, cls.import_run = IMPORT_COURSEID.split('/')
        # NOTE: Creating a single db for all the tests to save time.  This
        # is ok only as long as none of the tests modify the db.
        # If (when!) that changes, need to either reload the db, or load
        # once and copy over to a tmp db for each test.
        cls.store = cls.initdb()

    @classmethod
    def teardownClass(cls):
        """
        Clear out database after test has completed
        """
        cls.destroy_db(cls.connection)

    @staticmethod
    def initdb():
        """
        Initialize the database and import one test course into it
        """
        # connect to the db
        _options = {}
        _options.update(OPTIONS)
        store = MixedModuleStore(**_options)

        import_from_xml(
            store._get_modulestore_for_courseid(IMPORT_COURSEID),
            DATA_DIR,
            ['toy'],
            target_location_namespace=Location(
                'i4x',
                TestMixedModuleStore.import_org,
                TestMixedModuleStore.import_course,
                'course',
                TestMixedModuleStore.import_run
            )
        )

        return store

    @staticmethod
    def destroy_db(connection):
        """
        Destroy the test db.
        """
        connection.drop_database(DB)

    def setUp(self):
        # make a copy for convenience
        self.connection = TestMixedModuleStore.connection

    def tearDown(self):
        pass