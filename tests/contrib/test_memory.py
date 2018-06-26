import unittest
from uuid import uuid4

from flipper import MemoryFeatureFlagStore


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.store = MemoryFeatureFlagStore()

    def txt(self):
        return uuid4().hex


class TestCreate(BaseTest):
    def test_value_is_true_when_created_with_default_true(self):
        feature_name = self.txt()

        self.store.create(feature_name, default=True)

        self.assertTrue(self.store.get(feature_name))

    def test_value_is_true_when_created_with_default_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, default=False)

        self.assertFalse(self.store.get(feature_name))

    def test_value_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertFalse(self.store.get(feature_name))


class TestGet(BaseTest):
    pass


class TestSet(BaseTest):
    def test_sets_correct_value_when_true(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)

        self.assertTrue(self.store.get(feature_name))

    def test_sets_correct_value_when_false(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, False)

        self.assertFalse(self.store.get(feature_name))


class TestDelete(BaseTest):
    def test_returns_false_after_delete(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.store.set(feature_name, True)
        self.store.delete(feature_name)

        self.assertFalse(self.store.get(feature_name))

    def test_does_not_raise_when_deleting_key_that_does_not_exist(self):
        feature_name = self.txt()

        self.store.delete(feature_name)

        self.assertFalse(self.store.get(feature_name))
