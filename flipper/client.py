# Copyright 2018 eShares, Inc. dba Carta, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from typing import Iterator, Optional

from .bucketing.base import AbstractBucketer
from .conditions import Condition
from .contrib.interface import AbstractFeatureFlagStore
from .flag import FeatureFlag


class FeatureFlagClient:
    def __init__(self, store: AbstractFeatureFlagStore) -> None:
        self._store = store

    def is_enabled(self, feature_name: str, **conditions) -> bool:
        return self.get(feature_name).is_enabled(**conditions)

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlag:
        self._store.create(feature_name, is_enabled=is_enabled, client_data=client_data)
        return self.get(feature_name)

    def exists(self, feature_name: str) -> bool:
        return self._store.get(feature_name) is not None

    def get(self, feature_name: str) -> FeatureFlag:
        return FeatureFlag(feature_name, self._store)

    def destroy(self, feature_name: str):
        return self.get(feature_name).destroy()

    def enable(self, feature_name: str):
        return self.get(feature_name).enable()

    def disable(self, feature_name: str):
        return self.get(feature_name).disable()

    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlag]:
        for item in self._store.list(limit=limit, offset=offset):
            yield self.get(item.feature_name)

    def set_client_data(self, feature_name: str, client_data: dict):
        return self.get(feature_name).set_client_data(client_data)

    def get_client_data(self, feature_name: str) -> dict:
        return self.get(feature_name).get_client_data()

    def get_meta(self, feature_name: str) -> dict:
        return self.get(feature_name).get_meta()

    def add_condition(self, feature_name: str, condition: Condition):
        return self.get(feature_name).add_condition(condition)

    def set_bucketer(self, feature_name: str, bucketer: AbstractBucketer):
        return self.get(feature_name).set_bucketer(bucketer)
