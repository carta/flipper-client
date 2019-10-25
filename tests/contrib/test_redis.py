import datetime
import unittest
from uuid import uuid4

import fakeredis

from flipper import RedisFeatureFlagStore
from flipper.contrib.interface import FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis(singleton=False)
        self.store = RedisFeatureFlagStore(self.redis)

    def txt(self):
        return uuid4().hex

    def date(self):
        return int(datetime.datetime(2018, 1, 1).timestamp())


class TestCreate(BaseTest):
    def test_is_enabled_is_true_when_created_with_is_enabled_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        self.assertTrue(self.store.get(feature_name).is_enabled())

    def test_is_enabled_is_true_when_created_with_default_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_is_enabled_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_sets_correct_value_in_redis_with_is_enabled_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        key = "/".join([self.store.base_key, feature_name])

        self.assertTrue(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_in_redis_with_is_enabled_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        key = "/".join([self.store.base_key, feature_name])

        self.assertFalse(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_in_redis_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        key = "/".join([self.store.base_key, feature_name])

        self.assertFalse(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )


class TestGet(BaseTest):
    pass


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

    def test_sets_correct_value_in_redis_when_true(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, True)

        key = "/".join([self.store.base_key, feature_name])

        self.assertTrue(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_in_redis_when_false(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, False)

        key = "/".join([self.store.base_key, feature_name])

        self.assertFalse(
            FeatureFlagStoreItem.deserialize(self.redis.get(key)).is_enabled()
        )

    def test_sets_correct_value_when_not_created(self):
        feature_name = self.txt()

        self.store.set(feature_name, True)

        self.assertTrue(self.store.get(feature_name).is_enabled())


class TestDelete(BaseTest):
    def test_returns_false_after_delete(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)
        self.store.delete(feature_name)

        self.assertIsNone(self.store.get(feature_name))

    def test_does_not_raise_when_deleting_key_that_does_not_exist(self):
        feature_name = self.txt()

        self.store.delete(feature_name)

        self.assertIsNone(self.store.get(feature_name))

    def test_deletes_value_from_redis(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.delete(feature_name)

        key = "/".join([self.store.base_key, feature_name])

        self.assertIsNone(self.redis.get(key))


class TestList(BaseTest):
    def test_returns_all_features(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        results = self.store.list()

        expected = sorted(feature_names)
        actual = sorted([item.feature_name for item in results])

        self.assertEqual(expected, actual)

    def test_returns_features_subject_to_offset(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        offset = 3

        results = self.store.list(offset=offset)

        actual = [item.feature_name for item in results]

        self.assertEqual(len(feature_names) - offset, len(actual))
        for feature_name in actual:
            self.assertTrue(feature_name in feature_names)

    def test_returns_features_subject_to_limit(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        limit = 3

        results = self.store.list(limit=limit)

        actual = [item.feature_name for item in results]

        self.assertEqual(limit, len(actual))
        for feature_name in actual:
            self.assertTrue(feature_name in feature_names)

    def test_returns_features_subject_to_offset_and_limit(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.store.create(name)

        offset = 2
        limit = 3

        results = self.store.list(limit=limit, offset=offset)

        actual = [item.feature_name for item in results]

        self.assertEqual(limit, len(actual))
        for feature_name in actual:
            self.assertTrue(feature_name in feature_names)

    def test_when_batch_size_is_set_to_a_value_smaller_than_number_of_keys_still_returns_everything(  # noqa: E501
        self
    ):
        feature_names = [self.txt() for _ in range(10)]

        store = RedisFeatureFlagStore(self.redis, list_method_batch_size=3)

        for name in feature_names:
            store.create(name)

        results = store.list()
        actual = [item.feature_name for item in results]

        self.assertEqual(len(feature_names), len(actual))
        for feature_name in actual:
            self.assertTrue(feature_name in feature_names)


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
