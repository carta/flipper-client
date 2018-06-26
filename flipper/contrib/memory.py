from typing import Optional

from .store import AbstractFeatureFlagStore


class MemoryFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self):
        self._memory = {}

    def create(self, feature_name: str, default: Optional[bool]=False):
        self.set(feature_name, default)

    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        return self._memory.get(feature_name, default)

    def set(self, feature_name: str, value: bool):
        self._memory[feature_name] = value

    def delete(self, feature_name: str):
        if feature_name in self._memory:
            del self._memory[feature_name]
