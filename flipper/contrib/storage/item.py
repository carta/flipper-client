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

import json

from flipper.bucketing import NoOpBucketer

from .meta import FeatureFlagStoreMeta


class FeatureFlagStoreItem:
    def __init__(
        self, feature_name: str, is_enabled: bool, meta: FeatureFlagStoreMeta
    ) -> None:
        self.feature_name = feature_name
        self._is_enabled = is_enabled
        self._meta = meta

    def to_dict(self):
        return {
            "feature_name": self.feature_name,
            "is_enabled": self._is_enabled,
            "meta": self._meta.to_dict(),
        }

    def serialize(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")

    @classmethod
    def deserialize(cls, serialized: bytes) -> "FeatureFlagStoreItem":
        deserialized = json.loads(serialized.decode("utf-8"))

        return cls(
            deserialized["feature_name"],
            deserialized["is_enabled"],
            FeatureFlagStoreMeta.from_dict(deserialized["meta"]),
        )

    @property
    def raw_is_enabled(self):
        return self._is_enabled

    def is_enabled(self, **conditions) -> bool:
        if self._is_enabled is False:
            return False

        if len(conditions) and self._has_conditions():
            return self._all_conditions_satisfied(**conditions)

        if self._has_bucketer():
            return self._meta.bucketer.check(**conditions)

        return True

    def _all_conditions_satisfied(self, **conditions) -> bool:
        return all(c.check(**conditions) for c in self._meta.conditions)

    def _has_bucketer(self) -> bool:
        return self._meta.bucketer.get_type() != NoOpBucketer.get_type()

    def _has_conditions(self) -> bool:
        return len(self._meta.conditions) > 0

    @property
    def meta(self):
        return self._meta.to_dict()
