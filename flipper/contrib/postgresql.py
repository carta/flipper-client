# Copyright 2018 eShares, Inc. dba Carta, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from contextlib import contextmanager
from typing import Iterator, Optional

from .interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now

POSTGRES_ENABLED = False
try:
    from psycopg import Connection, connect, sql

    POSTGRES_ENABLED = True
except ModuleNotFoundError:
    pass

CREATE_TABLE_SQL = (
    "CREATE TABLE IF NOT EXISTS {} ({} varchar(40) PRIMARY KEY, {} bytea NOT NULL)"
)
CREATE_ITEM_SQL = (
    "INSERT INTO {} ({}, {}) VALUES (%s, %s) ON CONFLICT({}) DO UPDATE SET {} = %s"
)
DELETE_ITEM_SQL = "DELETE FROM {} WHERE {} = %s"
LIST_ITEMS_SQL = "SELECT {} FROM {} LIMIT {} OFFSET {}"
SELECT_ITEM_SQL = "SELECT {} FROM {} WHERE {} = %s"
UPDATE_ITEM_SQL = "UPDATE {} SET {} = %s WHERE {} = %s"


class PostgresNotEnabled(Exception):
    def __init__(self):
        super().__init__(
            "Postgres is not enabled, please install extra dependency [postgres]"
        )


class PostgreSQLFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(
        self,
        conninfo: str,
        table_name: str = "feature_flags",
        name_column: str = "name",
        item_column: str = "item",
        run_migrations: bool = True,
    ) -> None:
        if not POSTGRES_ENABLED:
            raise PostgresNotEnabled()
        self._conninfo = conninfo
        self._table_name = sql.Identifier(table_name)
        self._name_column = sql.Identifier(name_column)
        self._item_column = sql.Identifier(item_column)
        if run_migrations:
            self.run_migrations()

    @contextmanager
    def _connection(self) -> "Connection":
        conn = connect(self._conninfo)
        try:
            yield conn
        finally:
            conn.close()

    def run_migrations(self) -> None:
        with self._connection() as conn:
            query = sql.SQL(CREATE_TABLE_SQL).format(
                self._table_name, self._name_column, self._item_column
            )
            conn.execute(query)
            conn.commit()

    def _update(self, item: FeatureFlagStoreItem) -> None:
        with self._connection() as conn:
            query = sql.SQL(UPDATE_ITEM_SQL).format(
                self._table_name, self._item_column, self._name_column
            )
            conn.execute(query, (item.serialize(), item.feature_name))
            conn.commit()

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        item = FeatureFlagStoreItem(
            feature_name, is_enabled, FeatureFlagStoreMeta(now(), client_data)
        )

        with self._connection() as conn:
            query = sql.SQL(CREATE_ITEM_SQL).format(
                self._table_name,
                self._name_column,
                self._item_column,
                self._name_column,
                self._item_column,
            )
            conn.execute(query, (item.feature_name, item.serialize(), item.serialize()))
            conn.commit()

        return item

    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        with self._connection() as conn:
            query = sql.SQL(SELECT_ITEM_SQL).format(
                self._item_column, self._table_name, self._name_column
            )
            row = conn.execute(query, (feature_name,)).fetchone()

        if not row:
            return None
        return FeatureFlagStoreItem.deserialize(row[0].tobytes())

    def set(self, feature_name: str, is_enabled: bool) -> None:
        existing = self.get(feature_name)

        if existing is None:
            self.create(feature_name, is_enabled)
        else:
            item = FeatureFlagStoreItem(
                feature_name, is_enabled, FeatureFlagStoreMeta.from_dict(existing.meta)
            )
            self._update(item)

    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlagStoreItem]:
        with self._connection() as conn:
            query = sql.SQL(LIST_ITEMS_SQL).format(
                self._item_column,
                self._table_name,
                sql.SQL("ALL") if limit is None else sql.Literal(limit),
                sql.Literal(offset),
            )
            rows = conn.execute(query).fetchall()

        for row in rows:
            yield FeatureFlagStoreItem.deserialize(row[0].tobytes())

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta) -> None:
        existing = self.get(feature_name)

        if existing is None:
            raise FlagDoesNotExistError(f"Feature {feature_name} does not exist")

        item = FeatureFlagStoreItem(feature_name, existing.raw_is_enabled, meta)

        self._update(item)

    def delete(self, feature_name: str) -> None:
        with self._connection() as conn:
            query = sql.SQL(DELETE_ITEM_SQL).format(self._table_name, self._name_column)
            conn.execute(query, (feature_name,))
            conn.commit()
