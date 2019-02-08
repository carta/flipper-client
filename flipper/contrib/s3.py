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


class S3FeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(
        self, client, bucket_name: str, page_size: Optional[int] = 1000
    ) -> None:
        self._client = client
        self._bucket_name = bucket_name
        self._page_size = page_size

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

    def _save(self, item: FeatureFlagStoreItem):
        self._client.put_object(
            Bucket=self._bucket_name, Key=item.feature_name, Body=item.serialize()
        )
        return item

    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        try:
            response = self._client.get_object(
                Bucket=self._bucket_name, Key=feature_name
            )
        except self._client.exceptions.NoSuchKey:
            return None
        serialized = response["Body"].read()
        return FeatureFlagStoreItem.deserialize(serialized)

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

        for key in self._list_object_keys():
            visited += 1

            if self._has_not_exceeded_list_offset(visited, offset):
                continue
            if self._has_reached_end_of_list(limit, offset, visited):
                return

            yield cast(FeatureFlagStoreItem, self.get(key))

    def _list_object_keys(self) -> Iterator[str]:
        paginator = self._client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self._bucket_name):
            for content in page.get("Contents", []):
                yield content["Key"]

    def _has_not_exceeded_list_offset(self, visited: int, offset: int) -> bool:
        return visited <= offset

    def _has_reached_end_of_list(
        self, limit: Optional[int], offset: int, visited: int
    ) -> bool:
        return limit is not None and visited > limit + offset

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta) -> None:
        existing = self.get(feature_name)

        if existing is None:
            raise FlagDoesNotExistError("Feature %s does not exist" % feature_name)

        item = FeatureFlagStoreItem(feature_name, existing.raw_is_enabled, meta)

        self._save(item)

    def delete(self, feature_name: str) -> None:
        self._client.delete_object(Bucket=self._bucket_name, Key=feature_name)
