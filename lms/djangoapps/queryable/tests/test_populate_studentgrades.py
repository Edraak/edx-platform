from django.test import TestCase

from queryable.models import CourseGrade, AssignmentTypeGrade, AssignmentGrade
from queryable.management.commands import populate_studentgrades

class TestPopulateStudentGradesUpdateCourseGrade(TestCase):

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
