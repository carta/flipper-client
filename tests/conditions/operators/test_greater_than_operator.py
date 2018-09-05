import unittest

from flipper.conditions.operators.greater_than_operator import GreaterThanOperator


class TestCompare(unittest.TestCase):
    def test_returns_true_when_expected_is_greater_than_actual(self):
        operator = GreaterThanOperator()

        self.assertTrue(operator.compare(2, 1))

    def test_returns_false_when_expected_is_less_than_actual(self):
        operator = GreaterThanOperator()

        self.assertFalse(operator.compare(1, 2))

    def test_returns_false_when_values_are_equal(self):
        operator = GreaterThanOperator()

        self.assertFalse(operator.compare(1, 1))
