import unittest
from uuid import uuid4

from flipper.conditions.operators.negated_set_membership_operator import (
    NegatedSetMembershipOperator,
)


class TestCompare(unittest.TestCase):
    def test_returns_true_when_expected_is_not_in_actual(self):
        operator = NegatedSetMembershipOperator()

        self.assertTrue(operator.compare(4, [1, 2, 3]))

    def test_returns_false_when_expected_is_in_actual(self):
        operator = NegatedSetMembershipOperator()

        self.assertFalse(operator.compare(2, [2, 3, 4]))
