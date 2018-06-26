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

from abc import ABCMeta, abstractmethod
from typing import Iterator, Optional

from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class AbstractFeatureFlagStore(metaclass=ABCMeta):
    @abstractmethod
    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ):
        pass

    @abstractmethod
    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        pass

    @abstractmethod
    def set(self, feature_name: str, is_enabled: bool):
        pass

    @abstractmethod
    def delete(self, feature_name: str):
        pass

    @abstractmethod
    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlagStoreItem]:
        pass

    @abstractmethod
    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        pass


class FlagDoesNotExistError(Exception):
    pass
