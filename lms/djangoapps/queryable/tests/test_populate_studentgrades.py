from django.test import TestCase

from student.tests.factories import UserFactory as StudentUserFactory
from courseware.tests.factories import StudentModuleFactory

from queryable.models import CourseGrade, AssignmentTypeGrade, AssignmentGrade
from queryable.management.commands import populate_studentgrades

class TestPopulateStudentGradesUpdateCourseGrade(TestCase):
    """
    Tests the helper fuction update_course_grade in the populate_studentgrades custom command
    """

    def setUp(self):
        self.course_grade = CourseGrade(percent=0.9, grade='A')
        self.gradeset = {'percent' : 0.9, 'grade' : 'A'}


    def test_no_update(self):
        """
        Values are the same, so no update
        """
        self.assertFalse(populate_studentgrades.update_course_grade(self.course_grade, self.gradeset))


    def test_percents_not_equal(self):
        """
        Update because the percents don't equal
        """
        self.course_grade.percent = 1.0

        self.assertTrue(populate_studentgrades.update_course_grade(self.course_grade, self.gradeset))


    def test_different_grade(self):
        """
        Update because the grade is different
        """
        self.course_grade.grade = 'Foo'

        self.assertTrue(populate_studentgrades.update_course_grade(self.course_grade, self.gradeset))


    def test_grade_as_null(self):
        """
        Percent is the same and grade are both null, so no update
        """
        self.course_grade.grade = None
        self.gradeset['grade'] = None

        self.assertFalse(populate_studentgrades.update_course_grade(self.course_grade, self.gradeset))


class TestPopulateStudentGradesGetAssignmentIndex(TestCase):
    """
    Tests the helper fuction get_assignment_index in the populate_studentgrades custom command
    """

    def test_simple(self):
        """
        Simple test if returns correct index.
        """

        self.assertEquals(populate_studentgrades.get_assignment_index("HW 3"),2)
        self.assertEquals(populate_studentgrades.get_assignment_index("HW 02"),1)
        self.assertEquals(populate_studentgrades.get_assignment_index("HW 11"),10)
        self.assertEquals(populate_studentgrades.get_assignment_index("HW 001"),0)


    def test_no_index(self):
        """
        Test if returns -1 for badly formed input
        """

        self.assertEquals(populate_studentgrades.get_assignment_index("HW Avg"),-1)
        self.assertEquals(populate_studentgrades.get_assignment_index("HW"),-1)
        self.assertEquals(populate_studentgrades.get_assignment_index("HW "),-1)


class TestPopulateStudentGradesGetStudentProblems(TestCase):
    """
    Tests the helper fuction get_student_problems in the populate_studentgrades custom command
    """

    def setUp(self):
        self.student_module = StudentModuleFactory(
            module_type='problem',
            module_state_key='one',
            grade=1,
            max_grade=1,
            )

    def test_single_problem(self):
        """
        Test returns a single problem
        """

        problem_set = populate_studentgrades.get_student_problems(
            self.student_module.course_id,
            self.student_module.student,
        )

        self.assertEquals(len(problem_set),1)
        self.assertEquals(problem_set[0], self.student_module.module_state_key)


    def test_problem_with_no_submission(self):
        """
        Test to make sure only returns the problems with a submission.
        """

        student_module_no_submission = StudentModuleFactory(
            course_id=self.student_module.course_id,
            student=self.student_module.student,
            module_type='problem',
            module_state_key='no_submission',
            grade=None,
            max_grade=None,
        )

        problem_set = populate_studentgrades.get_student_problems(
            self.student_module.course_id,
            self.student_module.student,
        )

        self.assertEquals(len(problem_set),1)
        self.assertEquals(problem_set[0], self.student_module.module_state_key)


class TestPopulateStudentGradesAssignmentExistsAndHasProblems(TestCase):
    """
    Tests the helper fuction assignment_exists_and_has_problems in the populate_studentgrades custom command
    """

    def setUp(self):
        self.category = 'HW'
        self.assignment_problems_map = {
            self.category : [
                ['cat_1_problem_id_1'],
            ]
        }


    def test_simple(self):
        """
        Test where assignment does exist and has problems
        """

        self.assertTrue(populate_studentgrades.assignment_exists_and_has_problems(
                self.assignment_problems_map,
                self.category,
                len(self.assignment_problems_map[self.category])-1,
            ))


    def test_assignment_exist_no_problems(self):
        """
        Test where assignment exists but has no problems
        """

        self.assignment_problems_map['Final'] = [[]]
        
        self.assertFalse(populate_studentgrades.assignment_exists_and_has_problems(
                self.assignment_problems_map, 'Final', 0
            ))


    def test_negative_index(self):
        """
        Test handles negative indexes well by returning False
        """

        self.assertFalse(populate_studentgrades.assignment_exists_and_has_problems({},"",-1))
        self.assertFalse(populate_studentgrades.assignment_exists_and_has_problems({},"",-5))


    def test_non_existing_category(self):
        """
        Test handled a category that doesn't actually exist by returning False
        """

        self.assertFalse(populate_studentgrades.assignment_exists_and_has_problems({},"Foo",0))
        self.assertFalse(populate_studentgrades.assignment_exists_and_has_problems(self.assignment_problems_map,"Foo",0))


    def test_index_too_high(self):
        """
        Test that if the index is higher than the actual number of assignments
        """

        self.assertFalse(populate_studentgrades.assignment_exists_and_has_problems(
                self.assignment_problems_map, self.category, len(self.assignment_problems_map[self.category])
            ))


class TestPopulateStudentGradesStudentDidProblems(TestCase):
    """
    Tests the helper fuction student_did_problems in the populate_studentgrades custom command
    """

    def setUp(self):
        self.student_problems = ['cat_1_problem_1']

    def test_student_did_do_problems(self):
        """
        Test where student did do some of the problems
        """

        self.assertTrue(populate_studentgrades.student_did_problems(self.student_problems, self.student_problems))

        problem_set = list(self.student_problems)
        problem_set.append('cat_2_problem_1')
        self.assertTrue(populate_studentgrades.student_did_problems(self.student_problems, problem_set))


    def test_student_did_not_do_problems(self):
        """
        Test where student didn't do any problems in the list
        """

        self.assertFalse(populate_studentgrades.student_did_problems(self.student_problems, []))
        self.assertFalse(populate_studentgrades.student_did_problems([],self.student_problems))

        problem_set = ['cat_1_problem_2']
        self.assertFalse(populate_studentgrades.student_did_problems(self.student_problems, problem_set))


class TestPopulateStudentGradesStoreAssignmentGradeIfNeed(TestCase):
    """
    Tests the helper fuction store_assignment_grade_if_need in the populate_studentgrades custom command
    """

    def setUp(self):
        self.student = StudentUserFactory()
        self.course_id = 'test/test/test'
        self.label = 'HW 01'
        self.percent = 1.0
        self.assignment_grade = AssignmentGrade(
            user=self.student,
            course_id=self.course_id,
            label=self.label,
            percent=self.percent,
        )
        self.assignment_grade.save()


    def test_new_assignment_grade_store(self):
        """
        Test the function both stores the new assignment grade and returns True meaning that it had
        """

        self.assertEqual(len(AssignmentGrade.objects.filter(course_id__exact=self.course_id)),1)
        return_value = populate_studentgrades.store_assignment_grade_if_need(
            self.student, self.course_id, 'Foo 01', 1.0
        )
        
        self.assertTrue(return_value)
        self.assertEqual(len(AssignmentGrade.objects.filter(course_id__exact=self.course_id)),2)


    def test_difference_percent_store(self):
        """
        Test updates the percent value when it is different
        """

        new_percent = self.percent-0.1
        return_value = populate_studentgrades.store_assignment_grade_if_need(
            self.student, self.course_id, self.label, new_percent
        )
        
        self.assertTrue(return_value)

        assignment_grades = AssignmentGrade.objects.filter(
            course_id__exact=self.course_id,
            user=self.student,
            label=self.label,
        )
        self.assertEqual(len(assignment_grades),1)
        self.assertEqual(assignment_grades[0].percent, new_percent)


    def test_same_percent_no_store(self):
        """
        Test does not touch row if the row exists and the precent is not different
        """
        updated_time = self.assignment_grade.updated

        return_value = populate_studentgrades.store_assignment_grade_if_need(
            self.student, self.course_id, self.label, self.percent
        )

        self.assertFalse(return_value)

        assignment_grades = AssignmentGrade.objects.filter(
            course_id__exact=self.course_id,
            user=self.student,
            label=self.label,
        )
        self.assertEqual(len(assignment_grades),1)
        self.assertEqual(assignment_grades[0].percent, self.percent)
        self.assertEqual(assignment_grades[0].updated, updated_time)

