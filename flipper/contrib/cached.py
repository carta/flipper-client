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

from typing import Iterator, Optional

from lruttl import LRUCache

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta

DEFAULT_SIZE = 5000
DEFAULT_TTL = None


class CachedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, store: AbstractFeatureFlagStore, **cache_options) -> None:
        self._cache = LRUCache(cache_options.get("size", DEFAULT_SIZE))
        self._store = store
        self._cache_options = {"ttl": None, **cache_options}

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        item = self._store.create(
            feature_name, is_enabled=is_enabled, client_data=client_data
        )
        self._cache.set(feature_name, item, **self._cache_options)
        return item

    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        cached = self._cache.get(feature_name)
        if cached is not None:
            return cached

        item = self._store.get(feature_name)
        self._cache.set(feature_name, item, **self._cache_options)

        return item

    def set(self, feature_name: str, is_enabled: bool):
        self._store.set(feature_name, is_enabled)
        self._cache.set(
            feature_name, self._store.get(feature_name), **self._cache_options
        )

    def delete(self, feature_name: str):
        self._store.delete(feature_name)
        self._cache.set(feature_name, None, -1)

    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlagStoreItem]:
        return self._store.list(limit=limit, offset=offset)

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        self._store.set_meta(feature_name, meta)
        self._cache.set(
            feature_name, self._store.get(feature_name), **self._cache_options
        )
