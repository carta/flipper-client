import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import FeatureFlagClient, MemoryFeatureFlagStore
from flipper.flag import FeatureFlag, FlagDoesNotExistError


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.store = MemoryFeatureFlagStore()
        self.client = FeatureFlagClient(self.store)

    def txt(self):
        return uuid4().hex


class TestIsEnabled(BaseTest):
    def test_returns_true_when_feature_enabled(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_returns_false_when_feature_disabled(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.disable(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_returns_false_when_feature_does_not_exist(self):
        feature_name = self.txt()

        self.assertFalse(self.client.is_enabled(feature_name))


class TestCreate(BaseTest):
    def test_creates_and_returns_instance_of_feature_flag_class(self):
        feature_name = self.txt()

        flag = self.client.create(feature_name)

        self.assertTrue(isinstance(flag, FeatureFlag))

    def test_creates_flag_with_correct_name(self):
        feature_name = self.txt()

        flag = self.client.create(feature_name)

        self.assertEqual(feature_name, flag.name)

    def test_is_enabled_defaults_to_false(self):
        feature_name = self.txt()

        self.client.create(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_flag_can_be_enabled_on_create(self):
        feature_name = self.txt()

        self.client.create(feature_name, is_enabled=True)

        self.assertTrue(self.client.is_enabled(feature_name))


class TestGet(BaseTest):
    def test_returns_instance_of_feature_flag_class(self):
        feature_name = self.txt()

        self.client.create(feature_name)

        flag = self.client.get(feature_name)

        self.assertTrue(isinstance(flag, FeatureFlag))

    def test_returns_flag_with_correct_name(self):
        feature_name = self.txt()

        self.client.create(feature_name)

        flag = self.client.get(feature_name)

        self.assertEqual(feature_name, flag.name)


class TestDestroy(BaseTest):
    def test_get_will_return_instance_of_flag(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.destroy(feature_name)

        flag = self.client.get(feature_name)

        self.assertTrue(isinstance(flag, FeatureFlag))

    def test_status_switches_to_disabled(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)
        self.client.destroy(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.destroy(feature_name)


class TestEnable(BaseTest):
    def test_is_enabled_will_be_true(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_is_enabled_will_be_true_if_disable_was_called_earlier(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.disable(feature_name)
        self.client.enable(feature_name)

        self.assertTrue(self.client.is_enabled(feature_name))

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.enable(feature_name)


class TestDisable(BaseTest):
    def test_is_enabled_will_be_false(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.disable(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_is_enabled_will_be_false_if_enable_was_called_earlier(self):
        feature_name = self.txt()

        self.client.create(feature_name)
        self.client.enable(feature_name)
        self.client.disable(feature_name)

        self.assertFalse(self.client.is_enabled(feature_name))

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.disable(feature_name)


class TestSetClientData(BaseTest):
    def test_calls_backend_with_correct_args(self):
        self.store.set_client_data = MagicMock()

        feature_name = self.txt()
        client_data = { self.txt(): self.txt() }

        self.client.create(feature_name)
        self.client.set_client_data(feature_name, client_data)

        self.store.set_client_data.assert_called_once_with(
            feature_name, client_data
        )

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()
        client_data = { self.txt(): self.txt() }

        with self.assertRaises(FlagDoesNotExistError):
            self.client.set_client_data(feature_name, client_data)


class TestGetClientData(BaseTest):
    def test_gets_expected_key_value_pairs(self):
        feature_name = self.txt()
        client_data = { self.txt(): self.txt() }

        self.client.create(feature_name, client_data=client_data)

        result = self.client.get_client_data(feature_name)

        self.assertEqual(client_data, result)

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()
        client_data = { self.txt(): self.txt() }

        with self.assertRaises(FlagDoesNotExistError):
            self.client.get_client_data(feature_name)


class TestGetMeta(BaseTest):
    def test_includes_created_date(self):
        feature_name = self.txt()
        client_data = { self.txt(): self.txt() }

        self.client.create(feature_name, client_data=client_data)

        meta = self.client.get_meta(feature_name)

        self.assertTrue('created_date' in meta)

    def test_includes_client_data(self):
        feature_name = self.txt()
        client_data = { self.txt(): self.txt() }

        self.client.create(feature_name, client_data=client_data)

        meta = self.client.get_meta(feature_name)

        self.assertEqual(client_data, meta['client_data'])

    def test_raises_for_nonexistent_flag(self):
        feature_name = self.txt()

        with self.assertRaises(FlagDoesNotExistError):
            self.client.get_meta(feature_name)
