from datetime import datetime
import json
import unittest
from uuid import uuid4

from flipper import Condition
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.now = int(datetime.now().timestamp())

    def txt(self):
        return uuid4().hex


class TestToJSON(BaseTest):
    def test_includes_correct_feature_name(self):
        name = self.txt()
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, True, meta)
        self.assertEqual(name, item.toJSON()['feature_name'])

    def test_includes_correct_is_enabled_when_true(self):
        is_enabled = True
        item = FeatureFlagStoreItem(
            self.txt(), is_enabled, FeatureFlagStoreMeta(self.now, {})
        )
        self.assertEqual(is_enabled, item.toJSON()['is_enabled'])

    def test_includes_correct_is_enabled_when_true(self):
        is_enabled = False
        item = FeatureFlagStoreItem(
            self.txt(), is_enabled, FeatureFlagStoreMeta(self.now, {})
        )
        self.assertEqual(is_enabled, item.toJSON()['is_enabled'])

    def test_includes_correct_meta(self):
        client_data = { 'foo': 'bar' }
        meta = FeatureFlagStoreMeta(self.now, client_data)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertEqual(meta.toJSON(), item.toJSON()['meta'])


class TestSerialize(BaseTest):
    def test_is_base_64_encoded(self):
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        self.assertTrue(isinstance(item.serialize().decode('utf-8'), str))

    def test_contains_all_fields_from_json(self):
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        self.assertEqual(
            json.dumps(item.toJSON()),
            item.serialize().decode('utf-8')
        )


class TestDeserialize(BaseTest):
    def test_returns_instance_of_class(self):
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        self.assertTrue(isinstance(deserialized, FeatureFlagStoreItem))

    def test_sets_correct_feature_name(self):
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        self.assertEqual(name, deserialized.toJSON()['feature_name'])

    def test_sets_correct_is_enabled(self):
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        self.assertEqual(is_enabled, deserialized.is_enabled())

    def test_sets_correct_client_data(self):
        name = self.txt()
        is_enabled = True
        client_data = { 'foo': 'bar' }
        meta = FeatureFlagStoreMeta(self.now, client_data)
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        self.assertEqual(
            client_data, deserialized.toJSON()['meta']['client_data']
        )


class TestIsEnabled(BaseTest):
    def test_is_enabled_is_true(self):
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertTrue(item.is_enabled())

    def test_is_enabled_is_false(self):
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(self.txt(), False, meta)
        self.assertFalse(item.is_enabled())

    def test_is_true_if_conditions_are_matched(self):
        meta = FeatureFlagStoreMeta(self.now, conditions=[Condition(foo=True)])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertTrue(item.is_enabled(foo=True))

    def test_is_false_if_conditions_are_not_matched(self):
        meta = FeatureFlagStoreMeta(self.now, conditions=[Condition(foo=True)])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertFalse(item.is_enabled(foo=False))

    def test_is_false_if_one_of_many_conditions_are_not_matched(self):
        conditions = [Condition(foo=True), Condition(x=9)]
        meta = FeatureFlagStoreMeta(self.now, conditions=conditions)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertFalse(item.is_enabled(foo=True, x=11))

    def test_is_true_if_all_of_many_conditions_are_matched(self):
        conditions = [Condition(foo=True), Condition(x=9)]
        meta = FeatureFlagStoreMeta(self.now, conditions=conditions)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertTrue(item.is_enabled(foo=True, x=9))
