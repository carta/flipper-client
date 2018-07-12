import unittest
from uuid import uuid4

from flipper import MemoryFeatureFlagStore
from flipper.contrib.storage import FeatureFlagStoreItem


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.store = MemoryFeatureFlagStore()

    def txt(self):
        return uuid4().hex


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

        self.assertTrue(
            isinstance(self.store.get(feature_name), FeatureFlagStoreItem)
        )


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
