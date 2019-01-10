import unittest
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from flipper import MemoryFeatureFlagStore, ReplicatedFeatureFlagStore
from flipper.contrib.storage import FeatureFlagStoreMeta


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.primary = MemoryFeatureFlagStore()
        self.replicas = [
            MemoryFeatureFlagStore(),
            MemoryFeatureFlagStore(),
            MemoryFeatureFlagStore(),
        ]
        self.store = ReplicatedFeatureFlagStore(self.primary, *self.replicas)

    def txt(self):
        return uuid4().hex


class TestCreate(BaseTest):
    def test_forwards_all_arguments_to_stores(self):
        feature_name = self.txt()

        primary = MagicMock()
        replicas = [MagicMock(), MagicMock(), MagicMock()]
        store = ReplicatedFeatureFlagStore(primary, *replicas)

        args = (feature_name,)
        kwargs = {"is_enabled": True, "client_data": {"x": 10}}

        store.create(*args, **kwargs)

        primary.create.assert_called_once_with(*args, **kwargs)
        for replica in replicas:
            replica.create.assert_called_once_with(*args, **kwargs)


class TestGet(BaseTest):
    def test_reads_value_from_primary_store(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True)

        for replica in self.replicas:
            replica.set(feature_name, False)

        result = self.store.get(feature_name).is_enabled()

        self.assertTrue(result)

    def test_forwards_all_arguments_to_primary_store_only(self):
        feature_name = self.txt()

        primary = MagicMock()
        replicas = [MagicMock(), MagicMock(), MagicMock()]
        store = ReplicatedFeatureFlagStore(primary, *replicas)

        store.create(feature_name, asynch=False)

        args = (feature_name,)
        kwargs = {}

        store.get(*args, **kwargs)

        primary.get.assert_called_once_with(*args, **kwargs)
        for replica in replicas:
            replica.get.assert_not_called()


class TestSet(BaseTest):
    def test_when_asynch_is_false_sets_value_in_primary_and_replicas(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False, asynch=False)
        self.store.set(feature_name, True, asynch=False)

        self.assertTrue(
            all(
                [
                    self.primary.get(feature_name).is_enabled(),
                    *[
                        replica.get(feature_name).is_enabled()
                        for replica in self.replicas
                    ],
                ]
            )
        )

    def test_forwards_all_arguments_to_stores(self):
        feature_name = self.txt()

        primary = MagicMock()
        replicas = [MagicMock(), MagicMock(), MagicMock()]
        store = ReplicatedFeatureFlagStore(primary, *replicas)

        store.create(feature_name, asynch=False)

        args = (feature_name, True)
        kwargs = {}

        store.set(*args, **kwargs)

        primary.set.assert_called_once_with(*args, **kwargs)
        for replica in replicas:
            replica.set.assert_called_once_with(*args, **kwargs)


class TestDelete(BaseTest):
    def test_when_asynch_is_false_deletes_in_primary_and_replicas(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=False, asynch=False)
        self.store.delete(feature_name, asynch=False)

        self.assertFalse(
            any(
                [
                    self.primary.get(feature_name),
                    *[replica.get(feature_name) for replica in self.replicas],
                ]
            )
        )

    def test_forwards_all_arguments_to_stores(self):
        feature_name = self.txt()

        primary = MagicMock()
        replicas = [MagicMock(), MagicMock(), MagicMock()]
        store = ReplicatedFeatureFlagStore(primary, *replicas)

        store.create(feature_name, asynch=False)

        args = (feature_name,)
        kwargs = {}

        store.delete(*args, **kwargs)

        primary.delete.assert_called_once_with(*args, **kwargs)
        for replica in replicas:
            replica.delete.assert_called_once_with(*args, **kwargs)


class TestList(BaseTest):
    def test_reads_value_from_primary_store(self):
        feature_name = self.txt()

        self.store.create(feature_name, is_enabled=True, asynch=False)

        for replica in self.replicas:
            replica.delete(feature_name)

        result = list(self.store.list())

        self.assertEqual(1, len(result))

    def test_forwards_all_arguments_to_primary_store_only(self):
        feature_name = self.txt()

        primary = MagicMock()
        replicas = [MagicMock(), MagicMock(), MagicMock()]
        store = ReplicatedFeatureFlagStore(primary, *replicas)

        store.create(feature_name, asynch=False)

        args = ()
        kwargs = {"limit": 10, "offset": 0}

        store.list(*args, **kwargs)

        primary.list.assert_called_once_with(*args, **kwargs)
        for replica in replicas:
            replica.list.assert_not_called()


class TestSetMeta(BaseTest):
    def test_when_asynch_is_false_sets_meta_in_primary_and_replicas(self):
        feature_name = self.txt()

        meta = FeatureFlagStoreMeta(datetime(2018, 5, 4))

        self.store.create(feature_name, asynch=False)
        self.store.set_meta(feature_name, meta, asynch=False)

        self.assertTrue(
            all(
                [
                    self.primary.get(feature_name).meta == meta.to_dict(),
                    *[
                        replica.get(feature_name).meta == meta.to_dict()
                        for replica in self.replicas
                    ],
                ]
            )
        )

    def test_forwards_all_arguments_to_stores(self):
        feature_name = self.txt()

        meta = FeatureFlagStoreMeta(datetime(2018, 5, 4))

        primary = MagicMock()
        replicas = [MagicMock(), MagicMock(), MagicMock()]
        store = ReplicatedFeatureFlagStore(primary, *replicas)

        store.create(feature_name, asynch=False)

        args = (feature_name, meta)
        kwargs = {}

        store.set_meta(*args, **kwargs)

        primary.set_meta.assert_called_once_with(*args, **kwargs)
        for replica in replicas:
            replica.set_meta.assert_called_once_with(*args, **kwargs)
