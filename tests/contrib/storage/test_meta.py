from datetime import datetime
import json
import unittest
from uuid import uuid4

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
