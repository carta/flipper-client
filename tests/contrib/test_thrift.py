import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import Condition, ThriftRPCFeatureFlagStore
from flipper.bucketing import ConsistentHashPercentageBucketer, LinearRampPercentage
from flipper.contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from flipper.contrib.util.date import now
from flipper_thrift.python.feature_flag_store.ttypes import (
    ConditionCheck as TConditionCheck,
    ConditionOperator as TConditionOperator,
    FeatureFlagStoreItem as TFeatureFlagStoreItem,
    FeatureFlagStoreMeta as TFeatureFlagStoreMeta,
)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.meta = TFeatureFlagStoreMeta(
            created_date=now(),
            client_data='{"foo": 30}',
            conditions=[
                {
                    "foo": [
                        TConditionCheck(
                            variable="foo",
                            value="99",
                            operator=TConditionOperator(symbol="lte"),
                        )
                    ]
                }
            ],
            bucketer=json.dumps(
                ConsistentHashPercentageBucketer(
                    key_whitelist=["baz"], percentage=LinearRampPercentage()
                ).to_dict()
            ),
        )

        class FakeThriftClient:
            Create = MagicMock(
                return_value=TFeatureFlagStoreItem(
                    feature_name=self.txt(), is_enabled=False, meta=self.meta
                )
            )
            Delete = MagicMock()
            Get = MagicMock(
                return_value=TFeatureFlagStoreItem(
                    feature_name=self.txt(), is_enabled=False, meta=self.meta
                )
            )
            Set = MagicMock()
            SetMeta = MagicMock()
            List = MagicMock(
                return_value=[
                    TFeatureFlagStoreItem(
                        feature_name=self.txt(), is_enabled=False, meta=self.meta
                    ),
                    TFeatureFlagStoreItem(
                        feature_name=self.txt(), is_enabled=False, meta=self.meta
                    ),
                    TFeatureFlagStoreItem(
                        feature_name=self.txt(), is_enabled=False, meta=self.meta
                    ),
                ]
            )

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

        self.client.Create.assert_called_once_with(feature_name, True, "{}")

    def test_when_client_data_is_supplied_it_is_serialized_as_string(self):
        feature_name = self.txt()
        client_data = {"foo": "bar"}

        self.store.create(feature_name, is_enabled=False, client_data=client_data)

        self.client.Create.assert_called_once_with(
            feature_name, False, '{"foo": "bar"}'
        )


class TestGet(BaseTest):
    def test_calls_rpc_client_with_correct_args(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)
        self.store.get(feature_name)

        self.client.Get.assert_called_once_with(feature_name)

    def test_converts_metadata_properly(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        item = self.store.get(feature_name)

        expected = FeatureFlagStoreMeta(
            created_date=self.meta.created_date,
            client_data=json.loads(self.meta.client_data),
            conditions=[Condition(foo__lte=99)],
            bucketer=ConsistentHashPercentageBucketer(
                key_whitelist=["baz"],
                percentage=LinearRampPercentage(
                    initial_time=json.loads(self.meta.bucketer)["percentage"][
                        "initial_time"
                    ]
                ),
            ),
        )

        self.assertEqual(expected.to_dict(), item.meta)


class TestList(BaseTest):
    def test_every_item_is_instance_of_feature_flag_item(self):
        for i in range(10):
            self.store.create(str(i))

        self.assertTrue(
            all(isinstance(item, FeatureFlagStoreItem) for item in self.store.list())
        )


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

        meta = FeatureFlagStoreMeta(
            created_date,
            client_data,
            conditions=[Condition(foo__lte=99)],
            bucketer=ConsistentHashPercentageBucketer(
                key_whitelist=["baz"], percentage=LinearRampPercentage()
            ),
        )

        self.store.set_meta(feature_name, meta)

        self.client.SetMeta.assert_called_once_with(
            feature_name,
            TFeatureFlagStoreMeta(
                created_date=meta.created_date,
                client_data=json.dumps(client_data),
                conditions=[
                    {
                        "foo": [
                            TConditionCheck(
                                variable="foo",
                                value="99",
                                operator=TConditionOperator(symbol="lte"),
                            )
                        ]
                    }
                ],
                bucketer=json.dumps(meta.bucketer.to_dict()),
            ),
        )
