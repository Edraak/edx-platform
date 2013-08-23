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
