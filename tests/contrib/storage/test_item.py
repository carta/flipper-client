import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import Condition
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.now = int(datetime.now().timestamp())

    def txt(self):
        return uuid4().hex


class TestToDict(BaseTest):
    def test_includes_correct_feature_name(self):
        name = self.txt()
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, True, meta)
        self.assertEqual(name, item.to_dict()["feature_name"])

    def test_includes_correct_is_enabled_when_true(self):
        is_enabled = True
        item = FeatureFlagStoreItem(
            self.txt(), is_enabled, FeatureFlagStoreMeta(self.now, {})
        )
        self.assertEqual(is_enabled, item.to_dict()["is_enabled"])

    def test_includes_correct_is_enabled_when_false(self):
        is_enabled = False
        item = FeatureFlagStoreItem(
            self.txt(), is_enabled, FeatureFlagStoreMeta(self.now, {})
        )
        self.assertEqual(is_enabled, item.to_dict()["is_enabled"])

    def test_includes_correct_meta(self):
        client_data = {"foo": "bar"}
        meta = FeatureFlagStoreMeta(self.now, client_data)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertEqual(meta.to_dict(), item.to_dict()["meta"])


class TestSerialize(BaseTest):
    def test_is_base_64_encoded(self):
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        self.assertTrue(isinstance(item.serialize().decode("utf-8"), str))

    def test_contains_all_fields_from_json(self):
        name = self.txt()
        is_enabled = True
        meta = FeatureFlagStoreMeta(self.now, {})
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        self.assertEqual(json.dumps(item.to_dict()), item.serialize().decode("utf-8"))


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
        self.assertEqual(name, deserialized.to_dict()["feature_name"])

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
        client_data = {"foo": "bar"}
        meta = FeatureFlagStoreMeta(self.now, client_data)
        item = FeatureFlagStoreItem(name, is_enabled, meta)
        serialized = item.serialize()
        deserialized = FeatureFlagStoreItem.deserialize(serialized)
        self.assertEqual(client_data, deserialized.to_dict()["meta"]["client_data"])


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

    def test_returns_false_if_bucketer_check_returns_false(self):
        bucketer = MagicMock()
        bucketer.check.return_value = False
        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertFalse(item.is_enabled())

    def test_returns_true_if_bucketer_check_returns_true(self):
        bucketer = MagicMock()
        bucketer.check.return_value = True
        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer)
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertTrue(item.is_enabled())

    def test_returns_false_when_bucketer_returns_false_and_conditions_not_specified(
        self
    ):  # noqa: E501
        # flag.is_enabled(user_id=2) # False
        bucketer = MagicMock()
        bucketer.check.return_value = False
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertFalse(item.is_enabled())

    def test_returns_true_when_bucketer_returns_false_and_conditions_return_true(
        self
    ):  # noqa: E501
        # flag.is_enabled(user_id=2, is_admin=True) # True
        bucketer = MagicMock()
        bucketer.check.return_value = False
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertTrue(item.is_enabled(is_admin=True))

    def test_returns_true_when_bucketer_returns_true_and_conditions_not_specified(
        self
    ):  # noqa: E501
        # flag.is_enabled(user_id=1) # True
        bucketer = MagicMock()
        bucketer.check.return_value = True
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertTrue(item.is_enabled())

    def test_returns_false_when_bucketer_returns_true_and_conditions_return_false(
        self
    ):  # noqa: E501
        # flag.is_enabled(user_id=1, is_admin=False) # False
        bucketer = MagicMock()
        bucketer.check.return_value = True
        condition = Condition(is_admin=True)

        meta = FeatureFlagStoreMeta(self.now, bucketer=bucketer, conditions=[condition])
        item = FeatureFlagStoreItem(self.txt(), True, meta)
        self.assertFalse(item.is_enabled(is_admin=False))
