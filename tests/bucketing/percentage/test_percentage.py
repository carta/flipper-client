import unittest

from flipper.bucketing import Percentage


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self):
        percentage = Percentage()
        self.assertEqual(
            'Percentage',
            percentage.get_type(),
        )


class TestValue(unittest.TestCase):
    def test_matches_value_provided_in_constructor(self):
        value = 0.8
        percentage = Percentage(value=value)
        self.assertEqual(value, percentage.value)

    def test_defaults_to_1_dot_0(self):
        percentage = Percentage()
        self.assertEqual(1.0, percentage.value)


class TestToJSON(unittest.TestCase):
    def test_returns_correct_values(self):
        value = 0.8
        percentage = Percentage(value=value)
        expected = {
            'value': value,
            'type': Percentage.get_type(),
        }
        self.assertEqual(expected, percentage.toJSON())


class TestFromJSON(unittest.TestCase):
    def test_sets_correct_data(self):
        data = {
            'value': 0.8,
            'type': Percentage.get_type(),
        }
        percentage = Percentage.fromJSON(data)
        self.assertEqual(data, percentage.toJSON())
