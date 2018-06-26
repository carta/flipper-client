"""
   isort:skip_file
   See: https://github.com/ambv/black/issues/250
"""
import unittest

from flipper.conditions.operators.less_than_or_equal_to_operator import (
    LessThanOrEqualToOperator
)


class TestCompare(unittest.TestCase):
    def test_returns_true_when_expected_is_less_than_actual(self):
        operator = LessThanOrEqualToOperator()

        self.assertTrue(operator.compare(1, 2))

    def test_returns_false_when_expected_is_greater_than_actual(self):
        operator = LessThanOrEqualToOperator()

        self.assertFalse(operator.compare(2, 1))

    def test_returns_true_when_values_are_equal(self):
        operator = LessThanOrEqualToOperator()

        self.assertTrue(operator.compare(1, 1))
