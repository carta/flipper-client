import unittest

from flipper.bucketing.percentage import (
    LinearRampPercentage,
    Percentage,
    PercentageFactory,
)


class TestCreate(unittest.TestCase):
    def test_creates_percentage_percentage(self):
        percentage = PercentageFactory.create({"type": Percentage.get_type()})
        self.assertIsInstance(percentage, Percentage)

    def test_creates_linear_ramp_percentage(self):
        percentage = PercentageFactory.create({"type": LinearRampPercentage.get_type()})
        self.assertIsInstance(percentage, LinearRampPercentage)

    def test_raises_exception_when_given_an_unrecognized_type(self):
        with self.assertRaises(PercentageFactory.InvalidPercentageTypeError):
            PercentageFactory.create({"type": "xyz"})

    def test_passes_arguments_through_to_created_percentage(self):
        value = 0.21
        percentage = PercentageFactory.create(
            {"type": Percentage.get_type(), "value": value}
        )
        self.assertEqual(value, percentage.value)
