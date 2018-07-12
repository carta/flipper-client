from datetime import datetime
from typing import Optional, List

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


class RedisFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, redis, base_key='features'):
        self._redis = redis
        self.base_key = 'features'

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        self.set(feature_name, is_enabled, client_data=client_data)
        return self.get(feature_name)

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        serialized = self._redis.get(self._key_name(feature_name))
        if not serialized:
            return None
        return FeatureFlagStoreItem.deserialize(serialized)

    def _key_name(self, feature_name: str) -> str:
        return '/'.join([self.base_key, feature_name])

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
        client_data: Optional[dict] = None,
    ):
        client_data = client_data or {}

        item = FeatureFlagStoreItem(
            feature_name,
            is_enabled,
            FeatureFlagStoreMeta(now(), client_data),
        )

        self._redis.set(
            self._key_name(feature_name),
            item.serialize(),
        )

    def delete(self, feature_name: str):
        self._redis.delete(self._key_name(feature_name))
