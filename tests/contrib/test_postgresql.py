import unittest
from typing import Iterable

import testing.postgresql

from flipper import PostgreSQLFeatureFlagStore
from flipper.contrib.interface import FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreMeta
from flipper.contrib.util.date import now

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)


def tearDownModule(self):
    Postgresql.clear_cache()


class BaseTest(unittest.TestCase):
    def setUp(self):
        self._db = Postgresql()
        self.store = PostgreSQLFeatureFlagStore(self._db.url())

    def tearDown(self):
        self._db.stop()


class TestRunMigration(unittest.TestCase):
    def test_run_migration_creates_table(self):
        db = Postgresql()
        store = PostgreSQLFeatureFlagStore(db.url(), run_migrations=False)

        store.run_migrations()

        self.assertIsNone(store.get(""))


class TestCreate(BaseTest):
    def test_feature_flag_exists_when_created(self):
        feature_name = "test"

        item = self.store.create(feature_name)

        self.assertIsNotNone(item)

    def test_create_overrides_when_existing_feature_flag(self):
        feature_name = "test"

        self.store.create(feature_name)
        new_item = self.store.create(feature_name, client_data={"test": "data"})

        self.assertEqual(new_item.meta, self.store.get(feature_name).meta)

    def test_is_enabled_is_false_when_created_with_default(self):
        item = self.store.create("test")

        self.assertFalse(item.is_enabled())

    def test_is_enabled_is_true_when_created_with_is_enabled(self):
        item = self.store.create("test", is_enabled=True)

        self.assertTrue(item.is_enabled())

    def test_is_enabled_is_false_when_created_with_not_is_enabled(self):
        item = self.store.create("test", is_enabled=False)

        self.assertFalse(item.is_enabled())

    def test_client_data_is_persisted_when_created_with_client_data(self):
        client_data = {"test": "data"}

        item = self.store.create("test", client_data=client_data)

        self.assertEqual(item.meta["client_data"], client_data)


class TestGet(BaseTest):
    def test_returns_none_when_no_such_feature_flag(self):
        item = self.store.get("test")

        self.assertIsNone(item)


class TestList(BaseTest):
    def _create_several(self, names: Iterable[str]):
        for name in names:
            self.store.create(name)

    def test_returns_empty_iterator_when_no_feature_flags(self):
        items = list(self.store.list())

        self.assertEqual(len(items), 0)

    def test_returns_feature_flags(self):
        expected_names = {"test1", "test2"}
        self._create_several(expected_names)

        names = {x.feature_name for x in self.store.list()}

        self.assertSetEqual(names, expected_names)

    def test_limits_return_items_when_limit_is_given(self):
        self._create_several({"test1", "test2"})

        items = list(self.store.list(limit=1))

        self.assertEqual(len(items), 1)

    def test_starts_with_offset_when_offset_is_given(self):
        self._create_several({"test1", "test2"})

        items = list(self.store.list(offset=1))

        self.assertEqual(len(items), 1)


class TestSetMeta(BaseTest):
    def test_raises_exception_for_nonexistent_flag(self):
        meta = FeatureFlagStoreMeta(now())

        with self.assertRaises(FlagDoesNotExistError):
            self.store.set_meta("test", meta)

    def test_updated_meta(self):
        self.store.create("test")
        expected_meta = FeatureFlagStoreMeta(now(), client_data={"test": "date"})

        self.store.set_meta("test", expected_meta)

        meta = self.store.get("test").meta
        self.assertEqual(meta, expected_meta.to_dict())


class TestDelete(BaseTest):
    def test_does_not_raise_exception_when_no_existing_flag(self):
        item = self.store.get("test")

        self.assertIsNone(item)

        self.store.delete("test")

    def test_deletes_existing_flag(self):
        self.store.create("test")

        self.store.delete("test")

        item = self.store.get("test")
        self.assertIsNone(item)
