import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import MemoryFeatureFlagStore
from flipper.flag import FeatureFlag, FlagDoesNotExistError


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.name = self.txt()
        self.store = MemoryFeatureFlagStore()
        self.flag = FeatureFlag(self.name, self.store)

    def txt(self):
        return uuid4().hex


class TestName(BaseTest):
    def test_name_gets_set(self):
        self.assertEqual(self.name, self.flag.name)


class TestIsEnabled(BaseTest):
    def test_returns_true_when_feature_enabled(self):
        self.store.create(self.name)

        self.flag.enable()

        self.assertTrue(self.flag.is_enabled())

    def test_returns_false_when_feature_disabled(self):
        self.store.create(self.name)

        self.flag.enable()
        self.flag.disable()

        self.assertFalse(self.flag.is_enabled())

    def test_returns_false_when_flag_does_not_exist(self):
        self.assertFalse(self.flag.is_enabled())


class TestDestroy(BaseTest):
    def test_object_remains_instance_of_flag_class(self):
        self.store.create(self.name)

        self.flag.destroy()

        self.assertTrue(isinstance(self.flag, FeatureFlag))

    def test_status_switches_to_disabled(self):
        self.store.create(self.name)

        self.flag.enable()
        self.flag.destroy()

        self.assertFalse(self.flag.is_enabled())

    def test_store_is_called_with_correct_args(self):
        store = MagicMock()
        store.delete = MagicMock()
        flag = FeatureFlag(self.name, store)
        self.store.create(self.name)
        flag.destroy()

        store.delete.assert_called_once_with(self.name)

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.flag.destroy()


class TestEnable(BaseTest):
    def test_is_enabled_will_be_true(self):
        self.store.create(self.name)

        self.flag.enable()

        self.assertTrue(self.flag.is_enabled())

    def test_is_enabled_will_be_true_if_disable_was_called_earlier(self):
        self.store.create(self.name)

        self.flag.disable()
        self.flag.enable()

        self.assertTrue(self.flag.is_enabled())

    def test_store_is_called_with_correct_args(self):
        store = MagicMock()
        store.set = MagicMock()
        self.store.create(self.name)
        flag = FeatureFlag(self.name, store)
        flag.enable()

        store.set.assert_called_once_with(self.name, True)

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.flag.enable()


class TestDisable(BaseTest):
    def test_is_enabled_will_be_false(self):
        self.store.create(self.name, True)
        self.flag.disable()

        self.assertFalse(self.flag.is_enabled())

    def test_is_enabled_will_be_false_if_enable_was_called_earlier(self):
        self.store.create(self.name)
        self.flag.enable()
        self.flag.disable()

        self.assertFalse(self.flag.is_enabled())

    def test_store_is_called_with_correct_args(self):
        self.store.create(self.name)
        store = MagicMock()
        store.set = MagicMock()
        flag = FeatureFlag(self.name, store)
        flag.disable()

        store.set.assert_called_once_with(self.name, False)

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.flag.disable()
