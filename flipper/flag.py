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

from typing import cast

from .bucketing.base import AbstractBucketer
from .conditions import Condition
from .contrib.interface import AbstractFeatureFlagStore
from .contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class FlagDoesNotExistError(Exception):
    pass


def flag_must_exist(fn):
    def wrapper(self, *args, **kwargs):
        if not self.exists():
            raise FlagDoesNotExistError()
        return fn(self, *args, **kwargs)

    return wrapper


class FeatureFlag:
    def __init__(self, feature_name: str, store: AbstractFeatureFlagStore) -> None:
        self.name = feature_name
        self._store = store

    def is_enabled(self, default=False, **conditions) -> bool:
        item = self._store.get(self.name)
        if item is None:
            return default
        return item.is_enabled(**conditions)

    def exists(self):
        return self._store.get(self.name) is not None

    @flag_must_exist
    def enable(self):
        self._store.set(self.name, True)

    @flag_must_exist
    def disable(self):
        self._store.set(self.name, False)

    @flag_must_exist
    def destroy(self):
        self._store.delete(self.name)

    @flag_must_exist
    def add_condition(self, condition: Condition):
        meta = FeatureFlagStoreMeta.from_dict(self.get_meta())

        meta.conditions.append(condition)

        self._store.set_meta(self.name, meta)

    @flag_must_exist
    def set_client_data(self, client_data: dict):
        meta = FeatureFlagStoreMeta.from_dict(self.get_meta())

        meta.update(client_data=client_data)

        self._store.set_meta(self.name, meta)

    def get_client_data(self) -> dict:
        return self.get_meta()["client_data"]

    @flag_must_exist
    def get_meta(self) -> dict:
        return cast(FeatureFlagStoreItem, self._store.get(self.name)).meta

    @flag_must_exist
    def set_bucketer(self, bucketer: AbstractBucketer):
        meta = FeatureFlagStoreMeta.from_dict(self.get_meta())

        meta.update(bucketer=bucketer)

        self._store.set_meta(self.name, meta)
