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

from typing import Iterator, Optional, cast

from .interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


class RedisFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, redis, base_key="features"):
        self._redis = redis
        self.base_key = "features"

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        item = FeatureFlagStoreItem(
            feature_name, is_enabled, FeatureFlagStoreMeta(now(), client_data)
        )
        return self._save(item)

    def _save(self, item: FeatureFlagStoreItem) -> FeatureFlagStoreItem:
        self._redis.set(self._key_name(item.feature_name), item.serialize())
        return item

    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        serialized = self._redis.get(self._key_name(feature_name))
        if not serialized:
            return None
        return FeatureFlagStoreItem.deserialize(serialized)

    def _key_name(self, feature_name: str) -> str:
        return "/".join([self.base_key, feature_name])

    def set(self, feature_name: str, is_enabled: bool):
        existing = self.get(feature_name)

        if existing is None:
            self.create(feature_name, is_enabled)
            return

        item = FeatureFlagStoreItem(
            feature_name, is_enabled, FeatureFlagStoreMeta.from_dict(existing.meta)
        )

        self._save(item)

    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlagStoreItem]:
        visited = 0

        for feature_name in self._list_keys():
            visited += 1

            if visited <= offset:
                continue
            if limit is not None and visited > limit + offset:
                return

            yield cast(FeatureFlagStoreItem, self.get(feature_name))

    def _list_keys(self) -> Iterator[str]:
        keys = self._redis.scan_iter(match=self._make_scan_wildcard_match())
        for key in keys:
            yield self._feature_name(key.decode("utf-8"))

    def _feature_name(self, key_name: str) -> str:
        return key_name.replace("%s/" % self.base_key, "")

    def _make_scan_wildcard_match(self) -> str:
        return "%s/*" % self.base_key

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        existing = self.get(feature_name)

        if existing is None:
            raise FlagDoesNotExistError(
                "Feature %s does not exist" % feature_name
            )  # noqa: E501

        item = FeatureFlagStoreItem(feature_name, existing.raw_is_enabled, meta)

        self._save(item)

    def delete(self, feature_name: str):
        self._redis.delete(self._key_name(feature_name))
