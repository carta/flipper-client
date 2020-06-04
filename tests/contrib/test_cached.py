import unittest
from datetime import datetime
from time import sleep
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import CachedFeatureFlagStore, Condition, MemoryFeatureFlagStore
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.slow = MemoryFeatureFlagStore()
        self.fast = CachedFeatureFlagStore(self.slow)

    def txt(self):
        return uuid4().hex


class TestCreate(BaseTest):
    def test_is_enabled_is_true_when_created_with_is_enabled_true(self):
        feature_name = self.txt()

        self.fast.create(feature_name, is_enabled=True)

        self.assertTrue(self.fast.get(feature_name).is_enabled())

    def test_is_enabled_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.fast.create(feature_name)

        self.assertFalse(self.fast.get(feature_name).is_enabled())

    def test_is_enabled_in_fast_matches_value_in_slow_default(self):
        feature_name = self.txt()

        self.fast.create(feature_name)

        self.assertEqual(self.fast.get(feature_name), self.slow.get(feature_name))

    def test_value_in_fast_matches_value_in_slow_when_feature_enabled(self):
        feature_name = self.txt()

        self.fast.create(feature_name, is_enabled=True)

        self.assertEqual(self.fast.get(feature_name), self.slow.get(feature_name))


class TestGet(BaseTest):
    def test_returns_instance_of_feature_flag(self):
        feature_name = self.txt()

        self.fast.create(feature_name)

        self.assertTrue(isinstance(self.fast.get(feature_name), FeatureFlagStoreItem))

    def test_returns_true_when_value_in_slow_store_is_true(self):
        feature_name = self.txt()

        self.slow.create(feature_name, is_enabled=True)

        self.assertTrue(self.fast.get(feature_name).is_enabled())

    def test_returns_false_when_value_in_slow_store_is_false(self):
        feature_name = self.txt()

        self.slow.create(feature_name)

        self.assertFalse(self.fast.get(feature_name).is_enabled())

    def test_returns_cached_value_when_ttl_not_expired(self):
        fast = CachedFeatureFlagStore(self.slow, ttl=100)

        feature_name = self.txt()

        self.slow.create(feature_name)

        fast.get(feature_name)

        self.slow.set(feature_name, True)

        self.assertFalse(fast.get(feature_name).is_enabled())

    def test_does_not_call_slow_store_when_ttl_not_expired(self):
        feature_name = self.txt()

        self.slow.get = MagicMock()

        fast = CachedFeatureFlagStore(self.slow, ttl=100)

        fast.create(feature_name, is_enabled=True)

        fast.get(feature_name)

        self.slow.get.assert_not_called()

    def test_does_will_call_slow_store_after_ttl_expired(self):
        feature_name = self.txt()

        fast = CachedFeatureFlagStore(self.slow, ttl=-10)

        fast.create(feature_name, is_enabled=True)
        fast.get(feature_name)

        self.slow.set(feature_name, False)

        self.assertFalse(self.fast.get(feature_name).is_enabled())

    def test_avoids_race_condition_where_cache_can_return_none_at_end_of_ttl(self):
        feature_name = self.txt()

        fast = CachedFeatureFlagStore(self.slow, ttl=0.01)

        fast.create(feature_name)

        class CacheWrapper:
            def __init__(self, wrapped):
                self.wrapped = wrapped

            def __contains__(self, key):
                result = key in self.wrapped
                sleep(0.02)
                return result

            def __getitem__(self, key):
                return self.wrapped[key]

            def __setitem__(self, key, value):
                self.wrapped[key] = value

        cache = fast._cache
        fast._cache = CacheWrapper(cache)

        fast.set(feature_name, 1)

        self.assertIsNotNone(fast.get(feature_name))

    def test_it_should_be_able_to_cache_flags_that_do_not_exist(self):
        slow = MagicMock()
        fast = CachedFeatureFlagStore(slow)

        slow.get.return_value = None

        feature_name = self.txt()

        fast.get(feature_name)
        fast.get(feature_name)
        fast.get(feature_name)
        fast.get(feature_name)

        slow.get.assert_called_once_with(feature_name)


class TestSet(BaseTest):
    def test_sets_value_correctly(self):
        feature_name = self.txt()

        self.fast.create(feature_name)
        self.fast.set(feature_name, True)

        self.assertTrue(self.fast.get(feature_name))

    def test_sets_value_in_slow_store(self):
        feature_name = self.txt()

        self.fast.create(feature_name)
        self.fast.set(feature_name, True)

        self.assertTrue(self.slow.get(feature_name))

    def test_when_instantiated_with_size_does_not_fail(self):
        feature_name = self.txt()

        slow = MemoryFeatureFlagStore()
        fast = CachedFeatureFlagStore(slow, size=10)

        fast.set(feature_name, True)

        self.assertTrue(slow.get(feature_name))


class TestDelete(BaseTest):
    def test_sets_value_to_false(self):
        feature_name = self.txt()

        self.fast.create(feature_name)
        self.fast.set(feature_name, True)
        self.fast.delete(feature_name)

        self.assertFalse(self.fast.get(feature_name))

    def test_sets_value_in_slow_store_to_false(self):
        feature_name = self.txt()

        self.fast.create(feature_name)
        self.fast.set(feature_name, True)
        self.fast.delete(feature_name)

        self.assertFalse(self.slow.get(feature_name))


class TestList(BaseTest):
    def test_returns_all_features_in_sorted_order(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.fast.create(name)

        results = self.fast.list()

        expected = sorted(feature_names)
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)

    def test_returns_features_subject_to_offset(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.fast.create(name)

        offset = 3

        results = self.fast.list(offset=offset)

        expected = sorted(feature_names)[offset:]
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)

    def test_returns_features_subject_to_limit(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.fast.create(name)

        limit = 3

        results = self.fast.list(limit=limit)

        expected = sorted(feature_names)[:limit]
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)

    def test_returns_features_subject_to_offset_and_limit(self):
        feature_names = [self.txt() for _ in range(10)]

        for name in feature_names:
            self.fast.create(name)

        offset = 2
        limit = 3

        results = self.fast.list(limit=limit, offset=offset)

        expected = sorted(feature_names)[offset : offset + limit]
        actual = [item.feature_name for item in results]

        self.assertEqual(expected, actual)


class TestSetMeta(BaseTest):
    def test_sets_created_date_correctly(self):
        feature_name = self.txt()

        self.fast.create(feature_name)

        meta = FeatureFlagStoreMeta(int(datetime.now().timestamp()))

        self.fast.set_meta(feature_name, meta)

        self.assertEqual(
            meta.created_date, self.fast.get(feature_name).meta["created_date"]
        )

    def test_sets_client_data_correctly(self):
        feature_name = self.txt()

        self.fast.create(feature_name)

        meta = FeatureFlagStoreMeta(
            int(datetime.now().timestamp()), client_data={self.txt(): self.txt}
        )

        self.fast.set_meta(feature_name, meta)

        self.assertEqual(
            meta.client_data, self.fast.get(feature_name).meta["client_data"]
        )

    def test_sets_conditions_correctly(self):
        feature_name = self.txt()

        self.fast.create(feature_name)

        condition = Condition(**{self.txt(): self.txt()})
        meta = FeatureFlagStoreMeta(
            int(datetime.now().timestamp()), conditions=[condition]
        )

        self.fast.set_meta(feature_name, meta)

        self.assertEqual(
            condition.to_dict(), self.fast.get(feature_name).meta["conditions"][0]
        )
