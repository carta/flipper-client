from unittest import TestCase

from flipper.bucketing import Percentage


class TestLessThanOrEqualTo(TestCase):
    def test_when_comparison_is_greater_than_value_it_returns_false(self):
        percentage = Percentage(0.5)

        self.assertFalse(0.6 <= percentage)

    def test_when_comparison_is_equal_to_value_it_returns_true(self):
        percentage = Percentage(0.5)

        self.assertTrue(0.5 <= percentage)

    def test_when_comparison_is_less_then_value_it_returns_true(self):
        percentage = Percentage(0.5)

        self.assertTrue(0.4 <= percentage)
