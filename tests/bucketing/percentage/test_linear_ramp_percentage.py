import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from flipper.bucketing import LinearRampPercentage


class TestGetType(unittest.TestCase):
    def test_is_correct_value(self):
        percentage = LinearRampPercentage()
        self.assertEqual("LinearRampPercentage", percentage.get_type())


class TestValue(unittest.TestCase):
    def test_matches_initial_value_when_there_is_no_ramp_delta(self):
        value = 0.8
        percentage = LinearRampPercentage(initial_value=value, final_value=value)
        self.assertEqual(value, percentage.value)

    def test_matches_final_value_when_there_is_no_ramp_duration(self):
        initial_value = 0.2
        final_value = 0.6
        percentage = LinearRampPercentage(
            initial_value=initial_value, final_value=final_value, ramp_duration=0
        )
        self.assertEqual(final_value, percentage.value)

    @patch("flipper.bucketing.percentage.linear_ramp_percentage.datetime")
    def test_returns_a_value_that_is_linearly_interpolated_between_initial_and_final_value_by_time(  # noqa: E501
        self, mock_datetime
    ):
        now = datetime(2018, 1, 1)

        mock_datetime.now.return_value = now
        mock_datetime.fromtimestamp = datetime.fromtimestamp

        initial_value = 0.2
        final_value = 0.6
        ramp_duration = 60
        expected_percentage = 0.5

        dt = timedelta(seconds=ramp_duration * expected_percentage)
        initial_time = int((now - dt).timestamp())

        percentage = LinearRampPercentage(
            initial_value=initial_value,
            final_value=final_value,
            ramp_duration=ramp_duration,
            initial_time=initial_time,
        )

        value_delta = final_value - initial_value
        expected = value_delta * expected_percentage + initial_value

        self.assertEqual(expected, percentage.value)


class TestToDict(unittest.TestCase):
    def test_returns_correct_values(self):
        initial_value = 0.2
        final_value = 0.6
        ramp_duration = 60
        initial_time = int(datetime(2018, 1, 1).timestamp())

        percentage = LinearRampPercentage(
            initial_value=initial_value,
            final_value=final_value,
            ramp_duration=ramp_duration,
            initial_time=initial_time,
        )
        expected = {
            "type": LinearRampPercentage.get_type(),
            "initial_value": initial_value,
            "final_value": final_value,
            "ramp_duration": ramp_duration,
            "initial_time": initial_time,
        }
        self.assertEqual(expected, percentage.to_dict())


class TestFromDict(unittest.TestCase):
    def test_sets_correct_data(self):
        initial_value = 0.2
        final_value = 0.6
        ramp_duration = 60
        initial_time = int(datetime(2018, 1, 1).timestamp())

        data = {
            "type": LinearRampPercentage.get_type(),
            "initial_value": initial_value,
            "final_value": final_value,
            "ramp_duration": ramp_duration,
            "initial_time": initial_time,
        }
        percentage = LinearRampPercentage.from_dict(data)
        self.assertEqual(data, percentage.to_dict())
