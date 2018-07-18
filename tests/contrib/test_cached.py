import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import CachedFeatureFlagStore, MemoryFeatureFlagStore
from flipper.contrib.storage import FeatureFlagStoreItem


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

        self.assertEqual(
            self.fast.get(feature_name),
            self.slow.get(feature_name)
        )

    def test_value_in_fast_matches_value_in_slow_when_feature_enabled(self):
        feature_name = self.txt()

        self.fast.create(feature_name, is_enabled=True)

        self.assertEqual(
            self.fast.get(feature_name),
            self.slow.get(feature_name)
        )


class TestGet(BaseTest):
    def test_returns_instance_of_feature_flag(self):
        feature_name = self.txt()

        self.fast.create(feature_name)

        self.assertTrue(
            isinstance(self.fast.get(feature_name), FeatureFlagStoreItem)
        )

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

        self.slow.get.asssert_not_called()

    def test_does_will_call_slow_store_after_ttl_expired(self):
        feature_name = self.txt()

        fast = CachedFeatureFlagStore(self.slow, ttl=-10)

        fast.create(feature_name, is_enabled=True)
        fast.get(feature_name)

        self.slow.set(feature_name, False)

        self.assertFalse(self.fast.get(feature_name).is_enabled())


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
