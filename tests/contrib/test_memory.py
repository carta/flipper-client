import datetime
import unittest
from uuid import uuid4

from flipper import MemoryFeatureFlagStore
from flipper.contrib.interface import FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.store = MemoryFeatureFlagStore()

    def txt(self):
        return uuid4().hex

    def date(self):
        return int(datetime.datetime(2018, 1, 1).timestamp())


class TestCreate(BaseTest):
    def test_is_enabled_is_true_when_created_with_is_enabled_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        self.assertTrue(self.store.get(feature_name).is_enabled())

    def test_is_enabled_is_true_when_created_with_is_enabled_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_is_enabled_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_returns_instance_of_feature_flag(self):
        feature_name = self.txt()

        ff = self.store.create(feature_name)

        self.assertTrue(isinstance(ff, FeatureFlagStoreItem))


class TestGet(BaseTest):
    def test_returns_instance_of_feature_flag(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertTrue(isinstance(self.store.get(feature_name), FeatureFlagStoreItem))


class TestSet(BaseTest):
    def test_sets_correct_value_when_true(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)

        self.assertTrue(self.store.get(feature_name).is_enabled())

    def test_sets_correct_value_when_false(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, False)

        self.assertFalse(self.store.get(feature_name).is_enabled())


class TestDelete(BaseTest):
    def test_get_returns_none_after_delete(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)
        self.store.delete(feature_name)

        self.assertIsNone(self.store.get(feature_name))

    def test_does_not_raise_when_deleting_key_that_does_not_exist(self):
        feature_name = self.txt()

        self.store.delete(feature_name)

        self.assertIsNone(self.store.get(feature_name))


class TestList(BaseTest):
    def test_returns_all_features_in_sorted_order(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        results = self.store.list()

        expected = sorted(feature_names)
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)

    def test_returns_features_subject_to_offset(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        offset = 3

        results = self.store.list(offset=offset)

        expected = sorted(feature_names)[offset:]
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)

    def test_returns_features_subject_to_limit(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        limit = 3

        results = self.store.list(limit=limit)

        expected = sorted(feature_names)[:limit]
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)

    def test_returns_features_subject_to_offset_and_limit(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        offset = 2
        limit = 3

        results = self.store.list(limit=limit, offset=offset)

        expected = sorted(feature_names)[offset : offset + limit]
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)


class TestSetMeta(BaseTest):
    def test_sets_client_data_correctly(self):
        feature_name = self.txt()
        self.store.create(feature_name)

        client_data = {self.txt(): self.txt()}
        meta = FeatureFlagStoreMeta(self.date(), client_data)

        self.store.set_meta(feature_name, meta)

        item = self.store.get(feature_name)

        self.assertEqual(client_data, item.meta["client_data"])

    def test_sets_created_date_correctly(self):
        feature_name = self.txt()
        self.store.create(feature_name)

        client_data = {self.txt(): self.txt()}
        created_date = self.date()
        meta = FeatureFlagStoreMeta(self.date(), client_data)

        self.store.set_meta(feature_name, meta)

        item = self.store.get(feature_name)

        self.assertEqual(created_date, item.meta["created_date"])

    def test_raises_exception_for_nonexistent_flag(self):
        feature_name = self.txt()
        with self.assertRaises(FlagDoesNotExistError):
            self.store.set_meta(feature_name, {"a": self.txt()})
