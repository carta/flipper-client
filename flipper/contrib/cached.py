from typing import Optional, List

from lru import LRUCacheDict

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem


class CachedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, store: AbstractFeatureFlagStore, **cache_options):
        self._cache = LRUCacheDict(**cache_options)
        self._store = store

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        item = self._store.create(
            feature_name, is_enabled=is_enabled, client_data=client_data
        )
        self._cache[feature_name] = item
        return item

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        try:
            return self._cache[feature_name]
        except KeyError:
            pass

        value = self._store.get(feature_name)
        self._cache[feature_name] = value

        return value

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
        client_data: Optional[dict] = None,
    ):
        self._store.set(feature_name, is_enabled, client_data=client_data)
        self._cache[feature_name] = is_enabled

    def delete(self, feature_name: str):
        self._store.delete(feature_name)
        self._cache.__delete__(feature_name)
