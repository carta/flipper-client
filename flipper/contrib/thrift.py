from typing import Optional

from .store import AbstractFeatureFlagStore


class ThriftRPCFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, client):
        self._client = client

    def create(self, feature_name: str, default: Optional[bool]=False):
        return self._client.Create(feature_name, default)

    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        return self._client.Get(feature_name, default)

    def set(self, feature_name: str, value: bool):
        return self._client.Set(feature_name, value)

    def delete(self, feature_name: str):
        return self._client.Delete(feature_name)
