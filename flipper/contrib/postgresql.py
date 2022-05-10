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

from psycopg import Connection, connect, sql

from .interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


class PostgreSQLFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(
        self,
        conninfo: str,
        table_name: str = "feature_flags",
    ) -> None:
        self._conninfo = conninfo
        self._table_name = sql.Identifier(table_name)
        self._name_column = sql.Identifier("name")
        self._item_column = sql.Identifier("item")
        self._run_migrations()

    @contextmanager
    def _connection(self) -> Connection:
        conn = connect(self._conninfo)
        try:
            yield conn
        finally:
            conn.close()

    def _run_migrations(self) -> None:
        with self._connection() as conn:
            query = sql.SQL(
                """CREATE TABLE IF NOT EXISTS {} \
                ({} varchar(40) PRIMARY KEY, {} bytea NOT NULL)"""
            ).format(self._table_name, self._name_column, self._item_column)
            conn.execute(query)
            conn.commit()

    def _update(self, item: FeatureFlagStoreItem) -> None:
        with self._connection() as conn:
            query = sql.SQL("UPDATE {} SET {} = %s WHERE {} = %s").format(
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
        if self.get(feature_name) is None:
            with self._connection() as conn:
                query = sql.SQL("INSERT INTO {} ({}, {}) VALUES (%s, %s)").format(
                    self._table_name, self._name_column, self._item_column
                )
                conn.execute(query, (item.feature_name, item.serialize()))
                conn.commit()
        else:
            self._update(item)

        return item

    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        with self._connection() as conn:
            query = sql.SQL("SELECT {} FROM {} WHERE {} = %s").format(
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
            if limit is None:
                query = sql.SQL("SELECT {} FROM {} OFFSET {}").format(
                    self._item_column, self._table_name, sql.Literal(offset)
                )
            else:
                query = sql.SQL("SELECT {} FROM {} LIMIT {} OFFSET {}").format(
                    self._item_column,
                    self._table_name,
                    sql.Literal(limit),
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
            query = sql.SQL("DELETE FROM {} WHERE {} = %s").format(
                self._table_name, self._name_column
            )
            conn.execute(query, (feature_name,))
            conn.commit()
