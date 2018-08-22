from datetime import datetime
import json
from typing import Optional

from flipper.bucketing import NoOpBucketer

from .meta import FeatureFlagStoreMeta


class FeatureFlagStoreItem:
    def __init__(
        self,
        feature_name: str,
        is_enabled: bool,
        meta: FeatureFlagStoreMeta,
    ):
        self.feature_name = feature_name
        self._is_enabled = is_enabled
        self._meta = meta

    def toJSON(self):
        return {
            'feature_name': self.feature_name,
            'is_enabled': self._is_enabled,
            'meta': self._meta.toJSON(),
        }

    def serialize(self) -> bytes:
        return json.dumps(self.toJSON()).encode('utf-8')

    @classmethod
    def deserialize(cls, serialized: bytes):
        deserialized = json.loads(serialized.decode('utf-8'))

        return cls(
            deserialized['feature_name'],
            deserialized['is_enabled'],
            FeatureFlagStoreMeta.fromJSON(deserialized['meta']),
        )

    @property
    def raw_is_enabled(self):
        return self._is_enabled

    def is_enabled(self, **conditions) -> bool:
        if self._is_enabled is False:
            return False

        for condition in self._meta.conditions:
            if condition.check(**conditions) is False:
                return False

        bucketer_satisfied = self._meta.bucketer.check(**conditions)
        conditions_satisfied = self._all_conditions_satisfied(**conditions)

        has_bucketer = self._has_bucketer()
        has_conditions = self._has_conditions()

        if has_bucketer and has_conditions:
            return bucketer_satisfied or conditions_satisfied
        elif has_bucketer:
            return bucketer_satisfied
        elif has_conditions:
            return conditions_satisfied

        return True

    def _all_conditions_satisfied(self, **conditions) -> bool:
        return all(c.check(**conditions) for c in self._meta.conditions)

    def _has_bucketer(self) -> bool:
        return self._meta.bucketer.get_type() != NoOpBucketer.get_type()

    def _has_conditions(self) -> bool:
        return len(self._meta.conditions) > 0

    @property
    def meta(self):
        return self._meta.toJSON()
