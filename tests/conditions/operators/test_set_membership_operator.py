import unittest

from flipper.conditions.operators.set_membership_operator import SetMembershipOperator


class TestCompare(unittest.TestCase):
    def test_returns_true_when_expected_is_in_actual(self):
        operator = SetMembershipOperator()

        self.assertTrue(operator.compare(1, [1, 2, 3]))

    def test_returns_false_when_expected_is_not_in_actual(self):
        operator = SetMembershipOperator()

        self.assertFalse(operator.compare(1, [2, 3, 4]))
