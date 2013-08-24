from mock import Mock, patch

from django.test import TestCase

from class_dashboard import dashboard_data


class TestGetProblemGradeDistribution(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - test when a problem has two max_grade's, should just take the larger value
    """
    

class TestGetProblemAttemptDistrib(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - change max_attempts from default, make sure output correct
    """


class TestGetSequentialOpenDistrib(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
    """


class TestGetLastPopulate(TestCase):
    """
    Tests needed:
      - test when there is a log entry, return date
      - test when there is no log entry, return None
    """


class TestGetProblemSetGradeDistribution(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - test when a problem has two max_grade's, should just take the larger value
    """


class TestGetD3ProblemGradeDistribution(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - test it skips unit children that are not problems/only uses unit children that are cateogyr='problem'
      - handles when max_grade for a problem is zero
      - test xValue/label has correct values for the problems location
    """


class TestGetD3ProblemAttemptDistribution(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - test color label correct with max_attempts value
      - test xValue/label has correct values for the problems location
    """


class TestGetD3SequentialOpenDistribution(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - test xValue/label has correct value for the subsection location
    """


class TestGetD3SectionGradeDistribution(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - queries with the right problems from get_problem_set_grade_distribution
      - test does the right section
      - handles case where problem is in the section, but there is no data for it (because students done it)
    """


class TestGetSectionDisplayName(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
    """


class TestGetArraySectionHasProblem(TestCase):
    """
    Tests needed:
      - simple test, make sure output correct
      - test that it stops searching a section once it knows the section has a problem
    """
