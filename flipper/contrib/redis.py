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

from redis import Redis

from .interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now
from .util.iter import batchify

DEFAULT_LIST_METHOD_BATCH_SIZE = 100


class RedisFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(
        self,
        redis: Redis,
        base_key: str = "features",
        list_method_batch_size: int = DEFAULT_LIST_METHOD_BATCH_SIZE,
    ) -> None:
        self._redis = redis
        self.base_key = base_key
        self.list_method_batch_size = list_method_batch_size

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
        all_feature_keys = self._enumerate_feature_keys(limit, offset)

        for batch_of_keys in batchify(all_feature_keys, self.list_method_batch_size):
            results = self._redis.mget(list(batch_of_keys))

            for serialized in results:
                yield FeatureFlagStoreItem.deserialize(serialized)

    def _enumerate_feature_keys(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[str]:
        visited = 0

        for feature_key in self._scan_redis_for_feature_keys():
            visited += 1

            if visited <= offset:
                continue
            if limit is not None and visited > limit + offset:
                return

            yield feature_key

    def _scan_redis_for_feature_keys(self) -> Iterator[str]:
        keys = self._redis.scan_iter(match=self._make_scan_wildcard_match())
        for key in keys:
            yield key.decode("utf-8")

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
