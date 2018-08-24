import unittest
from unittest.mock import MagicMock

from flipper.bucketing import Percentage, NoOpBucketer


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self):
        bucketer = NoOpBucketer()
        self.assertEqual('NoOpBucketer', bucketer.get_type())


class TestCheck(unittest.TestCase):
    def test_always_returns_true_with_no_checks(self):
        bucketer = NoOpBucketer()
        self.assertTrue(bucketer.check())

    def test_always_returns_true_with_checks(self):
        bucketer = NoOpBucketer()
        self.assertTrue(bucketer.check(foo=1))


class TestToJSON(unittest.TestCase):
    def test_returns_correct_data(self):
        bucketer = NoOpBucketer()
        expected = {
            'type': NoOpBucketer.get_type(),
        }
        self.assertEqual(expected, bucketer.toJSON())


class TestFromJSON(unittest.TestCase):
    def test_sets_correct_data(self):
        data = {
            'type': NoOpBucketer.get_type(),
        }
        bucketer = NoOpBucketer.fromJSON(data)
        self.assertEqual(data, bucketer.toJSON())
