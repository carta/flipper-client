from .contrib.store import AbstractFeatureFlagStore


class FeatureFlag:
    def __init__(self, feature_name: str, store: AbstractFeatureFlagStore):
        self.name = feature_name
        self._store = store

    def is_enabled(self) -> bool:
        return self._store.get(self.name, default=False)

    def enable(self):
        self._store.set(self.name, True)

    def disable(self):
        self._store.set(self.name, False)

    def destroy(self):
        self._store.delete(self.name)

    def add_condition(self, condition):
        raise NotImplementedError()
