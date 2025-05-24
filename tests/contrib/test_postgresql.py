from typing import Iterable

import pytest
from pytest_postgresql.factories import postgresql_noproc

from flipper import PostgreSQLFeatureFlagStore
from flipper.contrib.interface import FlagDoesNotExistError
from flipper.contrib.storage import FeatureFlagStoreMeta
from flipper.contrib.util.date import now

# Create a PostgreSQL fixture
postgresql = postgresql_noproc(port=None)


@pytest.fixture
def postgresql_db(postgresql):
    """Return a PostgreSQL database instance."""
    return postgresql


@pytest.fixture
def store(postgresql):
    """Return a PostgreSQLFeatureFlagStore instance."""
    return PostgreSQLFeatureFlagStore(postgresql.url())


class TestRunMigration:
    def test_run_migration_creates_table(self, postgresql):
        store = PostgreSQLFeatureFlagStore(postgresql.url(), run_migrations=False)
        store.run_migrations()
        assert store.get("") is None


class TestCreate:
    def test_feature_flag_exists_when_created(self, store):
        feature_name = "test"
        item = store.create(feature_name)
        assert item is not None

    def test_create_overrides_when_existing_feature_flag(self, store):
        feature_name = "test"
        store.create(feature_name)
        new_item = store.create(feature_name, client_data={"test": "data"})
        assert new_item.meta == store.get(feature_name).meta

    def test_is_enabled_is_false_when_created_with_default(self, store):
        item = store.create("test")
        assert not item.is_enabled()

    def test_is_enabled_is_true_when_created_with_is_enabled(self, store):
        item = store.create("test", is_enabled=True)
        assert item.is_enabled()

    def test_is_enabled_is_false_when_created_with_not_is_enabled(self, store):
        item = store.create("test", is_enabled=False)
        assert not item.is_enabled()

    def test_client_data_is_persisted_when_created_with_client_data(self, store):
        client_data = {"test": "data"}
        item = store.create("test", client_data=client_data)
        assert item.meta["client_data"] == client_data


class TestGet:
    def test_returns_none_when_no_such_feature_flag(self, store):
        item = store.get("test")
        assert item is None


class TestList:
    def _create_several(self, store, names: Iterable[str]):
        for name in names:
            store.create(name)

    def test_returns_empty_iterator_when_no_feature_flags(self, store):
        items = list(store.list())
        assert len(items) == 0

    def test_returns_feature_flags(self, store):
        expected_names = {"test1", "test2"}
        self._create_several(store, expected_names)
        names = {x.feature_name for x in store.list()}
        assert names == expected_names

    def test_limits_return_items_when_limit_is_given(self, store):
        self._create_several(store, {"test1", "test2"})
        items = list(store.list(limit=1))
        assert len(items) == 1

    def test_starts_with_offset_when_offset_is_given(self, store):
        self._create_several(store, {"test1", "test2"})
        items = list(store.list(offset=1))
        assert len(items) == 1


class TestSetMeta:
    def test_raises_exception_for_nonexistent_flag(self, store):
        meta = FeatureFlagStoreMeta(now())
        with pytest.raises(FlagDoesNotExistError):
            store.set_meta("test", meta)

    def test_updated_meta(self, store):
        store.create("test")
        expected_meta = FeatureFlagStoreMeta(now(), client_data={"test": "date"})
        store.set_meta("test", expected_meta)
        meta = store.get("test").meta
        assert meta == expected_meta.to_dict()


class TestDelete:
    def test_does_not_raise_exception_when_no_existing_flag(self, store):
        item = store.get("test")
        assert item is None
        store.delete("test")

    def test_deletes_existing_flag(self, store):
        store.create("test")
        store.delete("test")
        item = store.get("test")
        assert item is None
