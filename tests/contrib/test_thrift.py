import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import ThriftRPCFeatureFlagStore
from flipper.contrib.storage import FeatureFlagStoreMeta
from flipper.contrib.util.date import now
from flipper_thrift.python.feature_flag_store.ttypes import (
    FeatureFlagStoreItem as TFeatureFlagStoreItem,
    FeatureFlagStoreMeta as TFeatureFlagStoreMeta,
)


class BaseTest(unittest.TestCase):
    def setUp(self):
        class FakeThriftClient:
            Create = MagicMock()
            Delete = MagicMock()
            Get = MagicMock(
                return_value=TFeatureFlagStoreItem(
                    feature_name=self.txt(),
                    is_enabled=False,
                    meta=TFeatureFlagStoreMeta(created_date=now(), client_data="{}"),
                )
            )
            Set = MagicMock()
            SetMeta = MagicMock()

        self.client = FakeThriftClient()
        self.store = ThriftRPCFeatureFlagStore(self.client)

    def txt(self):
        return uuid4().hex

    def configure_mock(self, method, return_value):
        method.configure_mock(return_value=return_value)

    def date(self):
        return int(datetime(2018, 1, 1).timestamp())


class TestCreate(BaseTest):
    def test_value_is_true_when_created_with_is_enabled_true(self):
        feature_name = self.txt()

        self.configure_mock(
            self.client.Get,
            TFeatureFlagStoreItem(
                feature_name=feature_name,
                is_enabled=True,
                meta=TFeatureFlagStoreMeta(created_date=now(), client_data="{}"),
            ),
        )

        self.store.create(feature_name, is_enabled=True)

        self.assertTrue(self.store.get(feature_name).is_enabled())

    def test_value_is_false_when_created_with_is_enabled_false(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_value_is_false_when_created_with_default(self):
        feature_name = self.txt()

        self.store.create(feature_name)

        self.assertFalse(self.store.get(feature_name).is_enabled())

    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        self.client.Create.assert_called_once_with(feature_name, True, None)


class TestGet(BaseTest):
    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)
        self.store.get(feature_name)

        self.client.Get.assert_called_once_with(feature_name)


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


class TestSetMeta(BaseTest):
    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()
        client_data = {self.txt(): self.txt()}
        created_date = self.date()

        meta = FeatureFlagStoreMeta(created_date, client_data)

        self.store.set_meta(feature_name, meta)

        self.client.SetMeta.assert_called_once_with(
            feature_name, json.dumps(meta.to_dict())
        )
