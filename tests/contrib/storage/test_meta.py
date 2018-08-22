from datetime import datetime
import json
import unittest
from uuid import uuid4

from flipper import Condition
from flipper.bucketing import PercentageBucketer, Percentage
from flipper.contrib.storage import FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.now = int(datetime.now().timestamp())

    def txt(self):
        return uuid4().hex


class TestToJSON(BaseTest):
    def test_includes_correct_created_date(self):
        meta = FeatureFlagStoreMeta(self.now, {})
        self.assertEqual(self.now, meta.toJSON()['created_date'])

    def test_includes_correct_client_data(self):
        client_data = {
            'foo': 99,
            'bar': 'ajds'
        }
        meta = FeatureFlagStoreMeta(self.now, client_data)
        self.assertEqual(client_data, meta.toJSON()['client_data'])

    def test_includes_correct_conditions(self):
        conditions = [Condition(foo=1), Condition(bar='baz')]
        meta = FeatureFlagStoreMeta(self.now, conditions=conditions)
        serialized_conditions = [c.toJSON() for c in conditions]
        self.assertEqual(serialized_conditions, meta.toJSON()['conditions'])

    def test_includes_currect_bucketer(self):
        bucketer = PercentageBucketer(percentage=Percentage(0.3))
        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer)
        self.assertEqual(bucketer.toJSON(), meta.toJSON()['bucketer'])


class TestFromJSON(BaseTest):
    def test_will_not_crash_if_client_data_not_present(self):
        json = {
            'created_date': self.now,
            'conditions': [],
        }
        meta = FeatureFlagStoreMeta.fromJSON(json)
        self.assertEqual({}, meta.client_data)

    def test_will_not_crash_if_conditions_not_present(self):
        json = {
            'created_date': self.now,
            'client_data': {},
        }
        meta = FeatureFlagStoreMeta.fromJSON(json)
        self.assertEqual([], meta.conditions)

    def test_can_create_with_bucketer(self):
        bucketer = PercentageBucketer(percentage=Percentage(0.3))
        json = {
            'created_date': self.now,
            'bucketer': bucketer.toJSON(),
        }
        meta = FeatureFlagStoreMeta.fromJSON(json)
        print(meta.bucketer._percentage)
        self.assertEqual(bucketer.toJSON(), meta.bucketer.toJSON())


class TestUpdate(BaseTest):
    def test_updates_created_date(self):
        later = self.now + 1
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(created_date=later)
        self.assertEqual(later, meta.created_date)

    def test_updates_client_data(self):
        updated_client_data = { self.txt(): self.txt() }
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(client_data=updated_client_data)
        self.assertEqual(updated_client_data, meta.client_data)

    def test_merges_old_and_new_client_data(self):
        original_client_data = { 'a': 1, 'b': 2 }
        updated_client_data = { 'b': 3 }
        meta = FeatureFlagStoreMeta(self.now, original_client_data)
        meta.update(client_data=updated_client_data)
        self.assertEqual(
            {
                'a': original_client_data['a'],
                'b': updated_client_data['b'],
            },
            meta.client_data,
        )

    def test_updating_created_date_does_not_affect_client_data(self):
        later = self.now + 1
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(created_date=later)
        self.assertEqual({}, meta.client_data)

    def test_updating_client_data_does_not_affect_created_date(self):
        updated_client_data = { self.txt(): self.txt() }
        meta = FeatureFlagStoreMeta(self.now, {})
        meta.update(client_data=updated_client_data)
        self.assertEqual(self.now, meta.created_date)

    def test_sets_conditions(self):
        conditions = [Condition(foo=1)]
        meta = FeatureFlagStoreMeta(self.now)
        meta.update(conditions=conditions)
        self.assertEqual(conditions, meta.conditions)

    def test_replaces_conditions_entirely(self):
        conditions = [Condition(foo=1)]
        meta = FeatureFlagStoreMeta(self.now)
        meta.update(conditions=conditions)
        meta.update(conditions=conditions)
        self.assertEqual(conditions, meta.conditions)

    def test_sets_bucketer(self):
        percentage_value = 0.1
        bucketer = PercentageBucketer(percentage=Percentage(percentage_value))
        meta = FeatureFlagStoreMeta(self.now)
        meta.update(bucketer=bucketer)
        self.assertEqual(percentage_value, meta.bucketer.percentage)
