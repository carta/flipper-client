import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import ThriftRPCFeatureFlagStore


class BaseTest(unittest.TestCase):
    def setUp(self):
        class FakeThriftClient:
            Create = MagicMock()
            Delete = MagicMock()
            Get = MagicMock(return_value=False)
            Set = MagicMock()

        self.client = FakeThriftClient()
        self.store = ThriftRPCFeatureFlagStore(self.client)

    def txt(self):
        return uuid4().hex

    def configure_mock(self, method, return_value):
        method.configure_mock(return_value=return_value)


class TestCreate(BaseTest):
    def test_value_is_true_when_created_with_is_enabled_true(self):
        self.configure_mock(self.client.Get, True)

        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        self.assertTrue(self.store.get(feature_name))

    def test_value_is_true_when_created_with_is_enabled_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        self.assertFalse(self.store.get(feature_name))

    def test_value_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertFalse(self.store.get(feature_name))

    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        self.client.Create.assert_called_once_with(feature_name, True)


class TestGet(BaseTest):
    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)
        self.store.get(feature_name, default=True)

        self.client.Get.assert_called_once_with(feature_name, True)


class TestSet(BaseTest):
    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.set(feature_name, True)

        self.client.Set.assert_called_once_with(feature_name, True)



class TestDelete(BaseTest):
    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()

        self.store.create(feature_name)
        self.store.delete(feature_name)

        self.client.Delete.assert_called_once_with(feature_name)
