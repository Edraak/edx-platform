"""
unittests for xmodule

Run like this:

    rake test_common/lib/xmodule

Contains next classes:

    1. BaseTestXmodule provides course and users
    for testing Xmodules with mongo store.

    2. test_system constructs a test ModuleSystem instance.

    3. tests for calc that should be removed to another file. TODO.
"""

import unittest
import os

import numpy

import calc
import xmodule
from xmodule.x_module import ModuleSystem
from mock import Mock

from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from django.test.client import Client

from student.tests.factories import UserFactory, CourseEnrollmentFactory
from courseware.tests.tests import TEST_DATA_MONGO_MODULESTORE
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

open_ended_grading_interface = {
    'url': 'blah/',
    'username': 'incorrect_user',
    'password': 'incorrect_pass',
    'staff_grading': 'staff_grading',
    'peer_grading': 'peer_grading',
    'grading_controller': 'grading_controller'
}


def test_system():
    """
    Construct a test ModuleSystem instance.

    By default, the render_template() method simply returns the context it is
    passed as a string.  You can override this behavior by monkey patching::

        system = test_system()
        system.render_template = my_render_func

    where `my_render_func` is a function of the form my_render_func(template, context).

    """
    return ModuleSystem(
        ajax_url='courses/course_id/modx/a_location',
        track_function=Mock(),
        get_module=Mock(),
        render_template=lambda template, context: str(context),
        replace_urls=lambda html: str(html),
        user=Mock(is_staff=False),
        filestore=Mock(),
        debug=True,
        xqueue={
            'interface': None,
            'callback_url': '/',
            'default_queuename': 'testqueue',
            'waittime': 10,
            'construct_callback': Mock(side_effect="/")
        },
        node_path=os.environ.get("NODE_PATH", "/usr/local/lib/node_modules"),
        xblock_model_data=lambda descriptor: descriptor._model_data,
        anonymous_student_id='student',
        open_ended_grading_interface=open_ended_grading_interface
    )


@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class BaseTestXmodule(ModuleStoreTestCase):
    """Base class for testing Xmodules with mongo store.

    This class prepares course and users for tests:
        1. create test course
        2. create, enrol and login users for this course

    Any xmodule should overwrite only next parameters for test:
        1. TEMPLATE_NAME
        2. DATA
        3. COURSE_DATA and USER_COUNT if needed

    This class should not contain any tests, because TEMPLATE_NAME
    should be defined in child class.
    """
    USER_COUNT = 2
    COURSE_DATA = {}

    # Data from YAML common/lib/xmodule/xmodule/templates/NAME/default.yaml
    TEMPLATE_NAME = ""
    DATA = {}

    def setUp(self):

        self.course = CourseFactory.create(data=self.COURSE_DATA)

        # Turn off cache.
        modulestore().request_cache = None
        modulestore().metadata_inheritance_cache_subsystem = None

        chapter = ItemFactory.create(
            parent_location=self.course.location,
            template="i4x://edx/templates/sequential/Empty",
        )
        section = ItemFactory.create(
            parent_location=chapter.location,
            template="i4x://edx/templates/sequential/Empty"
        )

        # username = robot{0}, password = 'test'
        self.users = [
            UserFactory.create(username='robot%d' % i, email='robot+test+%d@edx.org' % i)
            for i in xrange(self.USER_COUNT)
        ]
        for user in self.users:
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

        item = ItemFactory.create(
            parent_location=section.location,
            template=self.TEMPLATE_NAME,
            data=self.DATA
        )
        self.item_url = Location(item.location).url()

        # login all users for acces to Xmodule
        self.clients = {user.username: Client() for user in self.users}
        self.login_statuses = [
            self.clients[user.username].login(
                username=user.username, password='test')
            for user in self.users
        ]

        self.assertTrue(all(self.login_statuses))

    def get_url(self, dispatch):
        """Return word cloud url with dispatch."""
        return reverse(
            'modx_dispatch',
            args=(self.course.id, self.item_url, dispatch)
        )

    def tearDown(self):
        for user in self.users:
            user.delete()


class ModelsTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_load_class(self):
        vc = xmodule.x_module.XModuleDescriptor.load_class('video')
        vc_str = "<class 'xmodule.video_module.VideoDescriptor'>"
        self.assertEqual(str(vc), vc_str)

    def test_calc(self):
        variables = {'R1': 2.0, 'R3': 4.0}
        functions = {'sin': numpy.sin, 'cos': numpy.cos}

        self.assertTrue(abs(calc.evaluator(variables, functions, "10000||sin(7+5)+0.5356")) < 0.01)
        self.assertEqual(calc.evaluator({'R1': 2.0, 'R3': 4.0}, {}, "13"), 13)
        self.assertEqual(calc.evaluator(variables, functions, "13"), 13)
        self.assertEqual(calc.evaluator({'a': 2.2997471478310274, 'k': 9, 'm': 8, 'x': 0.66009498411213041}, {}, "5"), 5)
        self.assertEqual(calc.evaluator({}, {}, "-1"), -1)
        self.assertEqual(calc.evaluator({}, {}, "-0.33"), -.33)
        self.assertEqual(calc.evaluator({}, {}, "-.33"), -.33)
        self.assertEqual(calc.evaluator(variables, functions, "R1*R3"), 8.0)
        self.assertTrue(abs(calc.evaluator(variables, functions, "sin(e)-0.41")) < 0.01)
        self.assertTrue(abs(calc.evaluator(variables, functions, "k*T/q-0.025")) < 0.001)
        self.assertTrue(abs(calc.evaluator(variables, functions, "e^(j*pi)") + 1) < 0.00001)
        self.assertTrue(abs(calc.evaluator(variables, functions, "j||1") - 0.5 - 0.5j) < 0.00001)
        variables['t'] = 1.0
        # Use self.assertAlmostEqual here...
        self.assertTrue(abs(calc.evaluator(variables, functions, "t") - 1.0) < 0.00001)
        self.assertTrue(abs(calc.evaluator(variables, functions, "T") - 1.0) < 0.00001)
        self.assertTrue(abs(calc.evaluator(variables, functions, "t", cs=True) - 1.0) < 0.00001)
        self.assertTrue(abs(calc.evaluator(variables, functions, "T", cs=True) - 298) < 0.2)
        # Use self.assertRaises here...
        exception_happened = False
        try:
            calc.evaluator({}, {}, "5+7 QWSEKO")
        except:
            exception_happened = True
        self.assertTrue(exception_happened)

        try:
            calc.evaluator({'r1': 5}, {}, "r1+r2")
        except calc.UndefinedVariable:
            pass

        self.assertEqual(calc.evaluator(variables, functions, "r1*r3"), 8.0)

        exception_happened = False
        try:
            calc.evaluator(variables, functions, "r1*r3", cs=True)
        except:
            exception_happened = True
        self.assertTrue(exception_happened)
