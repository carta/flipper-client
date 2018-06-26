from typing import Optional, List

from .store import AbstractFeatureFlagStore


class RedisFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, redis, base_key='features'):
        self._redis = redis
        self.base_key = 'features'

    def create(self, feature_name: str, default: Optional[bool]=False) -> bool:
        self.set(feature_name, default)

    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        value = self._redis.get(self._key_name(feature_name))
        if value is None:
            return default
        return self._deserialize(value)

    def _key_name(self, feature_name: str) -> str:
        return '/'.join([self.base_key, feature_name])

    def _deserialize(self, value: str) -> bool:
        return bool(int(value))

    def set(self, feature_name: str, value: bool):
        self._redis.set(self._key_name(feature_name), self._serialize(value))

    def _serialize(self, value: bool) -> str:
        return b'1' if value is True else b'0'

    def delete(self, feature_name: str):
        self._redis.delete(self._key_name(feature_name))
