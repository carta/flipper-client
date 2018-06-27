from .contrib.store import AbstractFeatureFlagStore
from .flag import FeatureFlag


class FeatureFlagClient:
    def __init__(self, store: AbstractFeatureFlagStore):
        self._store = store

    def is_enabled(self, feature_name, **kwargs):
        return self.get(feature_name).is_enabled()

    def create(self, feature_name: str, is_enabled=False) -> FeatureFlag:
        self._store.create(feature_name, is_enabled=is_enabled)
        return self.get(feature_name)

    def get(self, feature_name: str) -> FeatureFlag:
        return FeatureFlag(feature_name, self._store)

    def destroy(self, feature_name: str):
        return self.get(feature_name).destroy()

    def enable(self, feature_name: str):
        return self.get(feature_name).enable()

    def disable(self, feature_name: str):
        return self.get(feature_name).disable()
