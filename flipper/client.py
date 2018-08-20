from typing import Optional

from .conditions import Condition
from .contrib.interface import AbstractFeatureFlagStore
from .flag import FeatureFlag


class FeatureFlagClient:
    def __init__(self, store: AbstractFeatureFlagStore):
        self._store = store

    def is_enabled(self, feature_name: str, **conditions) -> bool:
        return self.get(feature_name).is_enabled(**conditions)

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlag:
        self._store.create(
            feature_name, is_enabled=is_enabled, client_data=client_data
        )
        return self.get(feature_name)

    def get(self, feature_name: str) -> FeatureFlag:
        return FeatureFlag(feature_name, self._store)

    def destroy(self, feature_name: str):
        return self.get(feature_name).destroy()

    def enable(self, feature_name: str):
        return self.get(feature_name).enable()

    def disable(self, feature_name: str):
        return self.get(feature_name).disable()

    def set_client_data(self, feature_name: str, client_data: dict):
        return self.get(feature_name).set_client_data(client_data)

    def get_client_data(self, feature_name: str) -> dict:
        return self.get(feature_name).get_client_data()

    def get_meta(self, feature_name: str) -> dict:
        return self.get(feature_name).get_meta()

    def add_condition(self, feature_name: str, condition: Condition):
        return self.get(feature_name).add_condition(condition)
