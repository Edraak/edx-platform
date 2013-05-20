# -*- coding: utf-8 -*-

import unittest


from ..draganddrop_helpers import PositionsCompare
from ..draganddrop_helpers import flatten_user_answer, clean_user_answer


class TestPositionsCompare(unittest.TestCase):
    def test_nested_list_and_list1(self):
        self.assertEqual(PositionsCompare([[1, 2], 40]), PositionsCompare([1, 3]))

    def test_nested_list_and_list2(self):
        self.assertNotEqual(PositionsCompare([1, 12]), PositionsCompare([1, 1]))

    def test_list_and_list1(self):
        self.assertNotEqual(PositionsCompare([[1, 2], 12]), PositionsCompare([1, 15]))

    def test_list_and_list2(self):
        self.assertEqual(PositionsCompare([1, 11]), PositionsCompare([1, 1]))

    def test_numerical_list_and_string_list(self):
        self.assertNotEqual(PositionsCompare([1, 2]), PositionsCompare(["1"]))

    def test_string_and_string_list1(self):
        self.assertEqual(PositionsCompare("1"), PositionsCompare(["1"]))

    def test_string_and_string_list2(self):
        self.assertEqual(PositionsCompare("abc"), PositionsCompare("abc"))

    def test_string_and_string_list3(self):
        self.assertNotEqual(PositionsCompare("abd"), PositionsCompare("abe"))

    def test_float_and_string(self):
        self.assertNotEqual(PositionsCompare([3.5, 5.7]), PositionsCompare(["1"]))

    def test_floats_and_ints(self):
        self.assertEqual(PositionsCompare([3.5, 4.5]), PositionsCompare([5, 7]))


class TestUserAnswerHelpers(unittest.TestCase):
    def test_flatten_user_answer_user_answer(self):
        user_answer = [
            {'up': {'first': {'p': 'p_l1'}}},
            {'down': {'first': {'p': 'p_l2'}}},
            {'left': '000'},
            {'right': {'first': {'p': {'second': {'s': 's_l'}}}}},
            {'up': 'target1'},
            {'up': 'target2'},
            {'up1': 'target3'},
            {'up2': 'target4'}
        ]

        expected_result = [
            {'up': 'p_l1[p][first]'},
            {'down': 'p_l2[p][first]'},
            {'left': '000'},
            {'right': 's_l[s][second][p][first]'},
            {'up': 'target1'},
            {'up': 'target2'},
            {'up1': 'target3'},
            {'up2': 'target4'}
        ]
        self.assertListEqual(flatten_user_answer(user_answer), expected_result)

    def test_clean_user_answer(self):
        user_answer = [
            {'up': 'p_l1[p][first]'},
            {'down': 'p_l2[p][first{3}{5}]'},
            {'left': '000'},
            {'right': 's_l[s][second][p][first{1}{1}]'},
            {'up': 'target1'},
            {'up': 'target2'},
            {'up1': 'target3'},
            {'up2': 'target4'}
        ]

        expected_result = [
            {'up': 'p_l1[p][first]'},
            {'down': 'p_l2[p][first]'},
            {'left': '000'},
            {'right': 's_l[s][second][p][first]'},
            {'up': 'target1'},
            {'up': 'target2'},
            {'up1': 'target3'},
            {'up2': 'target4'}
        ]
        self.assertListEqual(clean_user_answer(user_answer), expected_result)


def suite():
    testcases = [
        TestPositionsCompare,
        TestUserAnswerHelpers
    ]
    suites = []
    for testcase in testcases:
        suites.append(unittest.TestLoader().loadTestsFromTestCase(testcase))
    return unittest.TestSuite(suites)

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
