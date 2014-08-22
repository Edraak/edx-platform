import json

from django.test.client import RequestFactory
from django.test.utils import override_settings
from factory import post_generation, Sequence
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User
from course_groups.models import CourseUserGroup
from courseware.tests.tests import TEST_DATA_MIXED_MODULESTORE
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from course_groups.views import (
    list_cohorts,
    add_cohort,
    users_in_cohort,
    add_users_to_cohort,
    remove_user_from_cohort
)

class CohortFactory(DjangoModelFactory):
    FACTORY_FOR = CourseUserGroup

    name = Sequence("cohort{}".format)
    course_id = "dummy_id"
    group_type = CourseUserGroup.COHORT

    @post_generation
    def users(self, create, extracted, **kwargs):  # pylint: disable=W0613
        self.users.add(*extracted)


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class CohortViewsTestCase(ModuleStoreTestCase):
    """
    Base class which sets up a course and a staff user.
    """
    def setUp(self):
        self.course = CourseFactory.create()
        self.staff_user = UserFactory.create(is_staff=True)

    def create_cohorts(self):
        """Creates cohorts for testing"""
        self.cohort1_users = [UserFactory.create() for _ in range(3)]
        self.cohort2_users = [UserFactory.create() for _ in range(2)]
        self.cohort3_users = [UserFactory.create() for _ in range(2)]
        self.cohortless_users = [UserFactory.create() for _ in range(3)]
        self.cohort1 = CohortFactory.create(course_id=self.course.id, users=self.cohort1_users)
        self.cohort2 = CohortFactory.create(course_id=self.course.id, users=self.cohort2_users)
        self.cohort3 = CohortFactory.create(course_id=self.course.id, users=self.cohort3_users)

    def _cohort_in_course(self, cohort_name, course):
        """
        Returns true iff `course` contains a cohort with the name `cohort_name`.
        """
        try:
            CourseUserGroup.objects.get(
                course_id=course.id,
                group_type=CourseUserGroup.COHORT,
                name=cohort_name
            )
        except CourseUserGroup.DoesNotExist:
            return False
        else:
            return True

    def _user_in_cohort(self, username, cohort):
        """
        Return true iff a user with `username` exists in `cohort`.
        """
        return username in map(lambda user: user.username, cohort.users.all())

    def _user_exists(self, username):
        """
        Return true iff a user with `username` exists at all.
        """
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return False
        else:
            return True


class ListCohortsTestCase(CohortViewsTestCase):
    def check_list_cohorts(self, expected_cohorts):
        """
        Check that list_cohorts returns the expected list of cohorts for a given course.

        expected_cohorts is the list of cohorts we expect to see in the response.
        """
        request = RequestFactory().get("dummy_url")
        request.user = self.staff_user
        response = list_cohorts(request, self.course.id.to_deprecated_string())
        self.assertEqual(response.status_code, 200)
        response_dict = json.loads(response.content)
        self.assertTrue(response_dict.get("success"))
        self.assertItemsEqual(
            response_dict.get("cohorts"),
            [
                {"name": cohort.name, "id": cohort.id}
                for cohort in expected_cohorts
            ]
        )
        # verify that the returned cohorts actually belong to the course
        self.assertTrue(
            all([self._cohort_in_course(cohort.get("name"), self.course) for cohort in response_dict.get("cohorts")])
        )

    def test_no_cohorts(self):
        """
        Verify that no cohorts are in response for a course with no cohorts.
        """
        self.check_list_cohorts([])

    def test_some_cohorts(self):
        """
        Verify that cohorts are in response for a course with some cohorts.
        """
        self.create_cohorts()
        expected_cohorts = CourseUserGroup.objects.filter(
            course_id=self.course.id,
            group_type=CourseUserGroup.COHORT
        )
        self.check_list_cohorts(expected_cohorts)


class AddCohortTestCase(CohortViewsTestCase):
    def check_add_cohort(self, cohort_name, expected_error_msg=None):
        """
        Check that add_cohort correctly returns the newly added cohort (or error) in the response.
        Also verify that the cohort was actually created.

        cohort_name is the name of the cohort which should be created.
        """
        if cohort_name is not None:
            request = RequestFactory().post("dummy_url", {"name": cohort_name})
        else:
            request = RequestFactory().post("dummy_url", {"name": ""})
        request.user = self.staff_user

        cohort_existed_previously = self._cohort_in_course(cohort_name, self.course)
        response = add_cohort(request, self.course.id.to_deprecated_string())
        self.assertEqual(response.status_code, 200)
        response_dict = json.loads(response.content)

        if cohort_name is None or cohort_existed_previously:
            self.assertFalse(response_dict.get("success"))
            self.assertEqual(
                response_dict.get("msg"),
                expected_error_msg
            )
            self.assertEqual(
                self._cohort_in_course(cohort_name, self.course),
                True if cohort_existed_previously else False
            )
        else:
            self.assertTrue(response_dict.get("success"))
            self.assertEqual(
                response_dict.get("cohort").get("name"),
                cohort_name
            )
            self.assertTrue(self._cohort_in_course(cohort_name, self.course))

    def test_new_cohort(self):
        """
        Verify that we can add a new cohort.
        """
        self.check_add_cohort("New Cohort")

    def test_no_cohort(self):
        """
        Verify that we cannot explicitly add no cohort.
        """
        self.check_add_cohort(cohort_name=None, expected_error_msg="No name specified")

    def test_existing_cohort(self):
        """
        Verify that we cannot add a cohort with the same name as an existing cohort.
        """
        self.create_cohorts()
        self.check_add_cohort(self.cohort1.name, "Can't create two cohorts with the same name")


class UsersInCohortTestCase(CohortViewsTestCase):
    def check_users_in_cohort(
            self,
            cohort,
            requested_page,
            expected_page=None,
            expected_num_pages=None,
            expected_users=None,
            should_return_bad_request=False
    ):
        """
        Check that users_in_cohort returns the expected list of users in a given course and cohort.
        Also verify that the returned users are actually in the given cohort.

        cohort is the cohort from which users will be returned
        requested_page is the requested pagination level
        expected_users is the list of users we expect to see in the response.
        expected_num_pages is the expected number of pages
        """
        request = RequestFactory().get("dummy_url", {"page": requested_page})
        request.user = self.staff_user
        response = users_in_cohort(request, self.course.id.to_deprecated_string(), cohort.id)

        if should_return_bad_request:
            self.assertEqual(response.status_code, 400)
            return

        self.assertEqual(response.status_code, 200)
        response_dict = json.loads(response.content)

        self.assertTrue(response_dict.get("success"))
        self.assertEqual(response_dict.get("page"), expected_page)
        self.assertEqual(
            response_dict.get("num_pages"),
            expected_num_pages
        )
        self.assertItemsEqual(
            response_dict.get("users"),
            [
                {"username": user.username, "name": user.profile.name, "email": user.email}
                for user in expected_users
            ]
        )
        # verify that the returned users actually belong to the requested cohort
        returned_users = [User.objects.get(username=user.get("username")) for user in response_dict.get("users")]
        self.assertTrue(set(returned_users).issubset(cohort.users.all()))

    def test_no_users(self):
        """
        Verify that we don't get back any users for a cohort with no users.
        """
        cohort = CohortFactory.create(course_id=self.course.id, users=[])
        self.check_users_in_cohort(
            cohort,
            requested_page=1,
            expected_page=1,
            expected_num_pages=1,
            expected_users=[]
        )

    def test_few_users(self):
        """
        Verify that we get back all users for a cohort when the cohort has <=100 users.
        """
        users = [UserFactory.create() for _ in range(5)]
        cohort = CohortFactory.create(course_id=self.course.id, users=users)
        self.check_users_in_cohort(
            cohort,
            requested_page=1,
            expected_page=1,
            expected_num_pages=1,
            expected_users=users
        )

    def test_many_users(self):
        """
        Verify that pagination works correctly for cohorts with >100 users.
        """
        users = [UserFactory.create() for _ in range(101)]
        cohort = CohortFactory.create(course_id=self.course.id, users=users)
        self.check_users_in_cohort(
            cohort,
            requested_page=1,
            expected_page=1,
            expected_num_pages=2,
            expected_users=users[:100]
        )
        self.check_users_in_cohort(
            cohort,
            requested_page=2,
            expected_page=2,
            expected_num_pages=2,
            expected_users=users[100:]
        )

    def test_out_of_range(self):
        """
        Verify we get the proper responses when asking for pages which don't exist.

        Expect a HttpResponseBadRequest when requesting a negative page.
        Expect a blank page of users when requesting a page which is greater than the actual number of pages.
        """
        users = [UserFactory.create() for _ in range(101)]
        cohort = CohortFactory.create(course_id=self.course.id, users=users)
        self.check_users_in_cohort(
            cohort,
            requested_page=-1,
            should_return_bad_request=True
        )
        self.check_users_in_cohort(
            cohort,
            requested_page=3,
            expected_page=3,
            expected_num_pages=2,
            expected_users=[]
        )

    def test_non_numeric_page(self):
        """
        Verify that we get back the first page of users when the page we request isn't a valid integer.
        """
        users = [UserFactory.create() for _ in range(5)]
        cohort = CohortFactory.create(course_id=self.course.id, users=users)
        self.check_users_in_cohort(
            cohort,
            requested_page="invalid",
            should_return_bad_request=True
        )


class AddUsersToCohortTestCase(CohortViewsTestCase):
    def setUp(self):
        super(AddUsersToCohortTestCase, self).setUp()
        self.create_cohorts()

    def check_add_users_to_cohort(
            self,
            users_string,
            expected_added=None,
            expected_changed=None,
            expected_present=None,
            expected_unknown=None
    ):
        """
        Check that add_users_to_cohort returns the expected result and has the
        expected side effects. The given users will be added to cohort1.

        users_string is the string input entered by the client

        expected_added is a list of users

        expected_changed is a list of (user, previous_cohort) tuples

        expected_present is a list of (user, email/username) tuples where
        email/username corresponds to the input

        expected_unknown is a list of strings corresponding to the input
        """
        expected_added = expected_added or []
        expected_changed = expected_changed or []
        expected_present = expected_present or []
        expected_unknown = expected_unknown or []
        request = RequestFactory().post("dummy_url", {"users": users_string})
        request.user = self.staff_user
        response = add_users_to_cohort(request, self.course.id.to_deprecated_string(), self.cohort1.id)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertTrue(result.get("success"))
        self.assertItemsEqual(
            result.get("added"),
            [
                {"username": user.username, "name": user.profile.name, "email": user.email}
                for user in expected_added
            ]
        )
        self.assertItemsEqual(
            result.get("changed"),
            [
                {
                    "username": user.username,
                    "name": user.profile.name,
                    "email": user.email,
                    "previous_cohort": previous_cohort
                }
                for (user, previous_cohort) in expected_changed
            ]
        )
        self.assertItemsEqual(
            result.get("present"),
            [username_or_email for (_, username_or_email) in expected_present]
        )
        self.assertItemsEqual(result.get("unknown"), expected_unknown)
        for user in expected_added + [user for (user, _) in expected_changed + expected_present]:
            self.assertEqual(
                CourseUserGroup.objects.get(
                    course_id=self.course.id,
                    group_type=CourseUserGroup.COHORT,
                    users__id=user.id
                ),
                self.cohort1
            )

    def test_empty(self):
        self.check_add_users_to_cohort("")

    def test_only_added(self):
        self.check_add_users_to_cohort(
            ",".join([user.username for user in self.cohortless_users]),
            expected_added=self.cohortless_users
        )

    def test_only_changed(self):
        self.check_add_users_to_cohort(
            ",".join([user.username for user in self.cohort2_users + self.cohort3_users]),
            expected_changed=(
                [(user, self.cohort2.name) for user in self.cohort2_users] +
                [(user, self.cohort3.name) for user in self.cohort3_users]
            )
        )

    def test_only_present(self):
        usernames = [user.username for user in self.cohort1_users]
        self.check_add_users_to_cohort(
            ",".join(usernames),
            expected_present=[(user, user.username) for user in self.cohort1_users]
        )

    def test_only_unknown(self):
        usernames = ["unknown_user{}".format(i) for i in range(3)]
        self.check_add_users_to_cohort(
            ",".join(usernames),
            expected_unknown=usernames
        )

    def test_all(self):
        unknowns = ["unknown_user{}".format(i) for i in range(3)]
        self.check_add_users_to_cohort(
            ",".join(
                unknowns +
                [
                    user.username
                    for user in self.cohortless_users + self.cohort1_users + self.cohort2_users + self.cohort3_users
                ]
            ),
            self.cohortless_users,
            (
                [(user, self.cohort2.name) for user in self.cohort2_users] +
                [(user, self.cohort3.name) for user in self.cohort3_users]
            ),
            [(user, user.username) for user in self.cohort1_users],
            unknowns
        )

    def test_emails(self):
        unknown = "unknown_user@example.com"
        self.check_add_users_to_cohort(
            ",".join([
                self.cohort1_users[0].email,
                self.cohort2_users[0].email,
                self.cohortless_users[0].email,
                unknown
            ]),
            [self.cohortless_users[0]],
            [(self.cohort2_users[0], self.cohort2.name)],
            [(self.cohort1_users[0], self.cohort1_users[0].email)],
            [unknown]
        )

    def test_delimiters(self):
        unknown = "unknown_user"
        self.check_add_users_to_cohort(
            " {} {}\t{}, \r\n{}".format(
                unknown,
                self.cohort1_users[0].username,
                self.cohort2_users[0].username,
                self.cohortless_users[0].username
            ),
            [self.cohortless_users[0]],
            [(self.cohort2_users[0], self.cohort2.name)],
            [(self.cohort1_users[0], self.cohort1_users[0].username)],
            [unknown]
        )


class RemoveUserFromCohortTestCase(CohortViewsTestCase):
    def check_remove_user_from_cohort(self, username, cohort, expected_error_msg=None):
        """
        Check that remove_user_from_cohort properly removes a user from a cohort and returns appropriate success.
        If the removal should fail, verify that the returned error message matches the expected one.
        """
        if username is not None:
            request = RequestFactory().post("dummy_url", {"username": username})
        else:
            request = RequestFactory().post("dummy_url")
        request.user = self.staff_user
        response = remove_user_from_cohort(request, self.course.id.to_deprecated_string(), cohort.id)
        response_dict = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        if username is None or not self._user_exists(username):
            self.assertFalse(response_dict.get("success"))
            self.assertEqual(response_dict.get("msg"), expected_error_msg)
        else:
            self.assertTrue(response_dict.get("success"))
            self.assertIsNone(response_dict.get("msg"))
            self.assertFalse(self._user_in_cohort(username, cohort))

    def test_no_username_given(self):
        """
        Verify that we get an error message when omitting a username.
        """
        cohort = CohortFactory.create(course_id=self.course.id, users=[])
        self.check_remove_user_from_cohort(None, cohort, expected_error_msg='No username specified')

    def test_user_does_not_exist(self):
        """
        Verify that we get an error message when the requested user to remove does not exist.
        """
        username = "bogus"
        cohort = CohortFactory.create(course_id=self.course.id, users=[])
        self.check_remove_user_from_cohort(
            username,
            cohort,
            expected_error_msg='No user \'{0}\''.format(username)
        )

    def test_can_remove_user_not_in_cohort(self):
        """
        Verify that we can "remove" a user from a cohort even if they are not a member of that cohort.
        """
        user = UserFactory.create()
        cohort = CohortFactory.create(course_id=self.course.id, users=[])
        self.check_remove_user_from_cohort(user.username, cohort)

    def test_can_remove_user_from_cohort(self):
        """
        Verify that we can remove a user from a cohort.
        """
        user = UserFactory.create()
        cohort = CohortFactory.create(course_id=self.course.id, users=[user])
        self.check_remove_user_from_cohort(user.username, cohort)
