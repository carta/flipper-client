from typing import Optional

from .store import AbstractFeatureFlagStore


class MemoryFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self):
        self._memory = {}

    def create(self, feature_name: str, is_enabled: Optional[bool]=False):
        self.set(feature_name, is_enabled)

    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        return self._memory.get(feature_name, default)

    def set(self, feature_name: str, is_enabled: bool):
        self._memory[feature_name] = is_enabled

    def delete(self, feature_name: str):
        if feature_name in self._memory:
            del self._memory[feature_name]
