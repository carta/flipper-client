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

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class SyncedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, source, local):
        self.source = source
        self.local = local

    def is_synced(self):
        return bool(self.local.get('features_synced'))

    def sync(self):
        for feature_name in self.source.list():
            feature = self.source.get(feature_name)

            flag_name = feature.name
            flag_is_enabled = feature.is_enabled()
            flag_meta = feature.get_meta()

            self.local.create(
                flag_name,
                is_enabled=flag_is_enabled
            )
            self.local.set_meta(
                flag_name,
                FeatureFlagStoreMeta.from_dict(flag_meta)
            )

        self.local.set('features_synced', True)

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        return self.local.create(feature_name, is_enabled, client_data)

    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        features_synced = self.is_synced()

        if not features_synced:
            self.sync()

        return self.get(feature_name)

    def set(self, feature_name: str, is_enabled: bool):
        self.local.set(feature_name, is_enabled)

    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlagStoreItem]:
        if not self.is_synced():
            self.sync()

        return self.local.list(limit, offset)

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        self.local.set_meta(feature_name, meta)

    def delete(self, feature_name: str):
        self.local.delete(feature_name)
