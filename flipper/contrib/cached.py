from typing import Optional, List

from lru import LRUCacheDict

from .store import AbstractFeatureFlagStore


class CachedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, store: AbstractFeatureFlagStore, **cache_options):
        self._cache = LRUCacheDict(**cache_options)
        self._store = store

    def create(self, feature_name: str, default: Optional[bool]=False):
        self._store.create(feature_name, default=default)
        self._cache[feature_name] = default

    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        try:
            return self._cache[feature_name]
        except KeyError:
            pass

        value = self._store.get(feature_name, default=default)
        self._cache[feature_name] = value

        return value

    def set(self, feature_name: str, value: bool):
        self._store.set(feature_name, value)
        self._cache[feature_name] = value

    def delete(self, feature_name: str):
        self._store.delete(feature_name)
        self._cache.__delete__(feature_name)