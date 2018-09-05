import unittest

from flipper.bucketing import (
    BucketerFactory,
    ConsistentHashPercentageBucketer,
    NoOpBucketer,
    Percentage,
    PercentageBucketer,
)


class TestCreate(unittest.TestCase):
    def test_creates_percentage_bucketer(self):
        bucketer = BucketerFactory.create({"type": PercentageBucketer.get_type()})
        self.assertIsInstance(bucketer, PercentageBucketer)

    def test_creates_consistent_hash_percentage_bucketer(self):
        bucketer = BucketerFactory.create(
            {"type": ConsistentHashPercentageBucketer.get_type()}
        )
        self.assertIsInstance(bucketer, ConsistentHashPercentageBucketer)

    def test_creates_noop_bucketer(self):
        bucketer = BucketerFactory.create({"type": NoOpBucketer.get_type()})
        self.assertIsInstance(bucketer, NoOpBucketer)

    def test_raises_exception_when_given_an_unrecognized_type(self):
        with self.assertRaises(BucketerFactory.InvalidBucketerTypeError):
            BucketerFactory.create({"type": "xyz"})

    def test_passes_arguments_through_to_created_bucketer(self):
        percentage = 0.21
        bucketer = BucketerFactory.create(
            {
                "type": PercentageBucketer.get_type(),
                "percentage": Percentage(value=percentage).to_dict(),
            }
        )
        self.assertEqual(percentage, bucketer.percentage)
