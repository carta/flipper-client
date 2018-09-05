import unittest

from flipper.conditions.operators.equality_operator import EqualityOperator


class TestCompare(unittest.TestCase):
    def test_returns_true_when_values_are_equal(self):
        operator = EqualityOperator()

        self.assertTrue(operator.compare(1, 1))

    def test_returns_false_when_values_are_not_equal(self):
        operator = EqualityOperator()

        self.assertFalse(operator.compare(1, 2))
