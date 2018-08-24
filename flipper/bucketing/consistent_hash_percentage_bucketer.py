import hashlib
import json
from typing import Any, Dict, Tuple

from .percentage import PercentageFactory
from .percentage_bucketer import PercentageBucketer


class ConsistentHashPercentageBucketer(PercentageBucketer):
    def __init__(self, **kwargs):
        self._key_whitelist = set(kwargs.pop('key_whitelist', []))
        super().__init__(**kwargs)

    @classmethod
    def get_type(cls) -> str:
        return 'ConsistentHashPercentageBucketer'

    def check(self, **checks) -> bool:
        if self._percentage == 0:
            return False

        serialized = self._serialize_checks(checks)

        hashed = hashlib.sha1(serialized)
        score = self._score_hash(hashed)

        return score <= self._percentage

    def _serialize_checks(self, checks: Dict[str, Any]) -> bytes:
        filtered_checks = self._filter_checks(checks)
        sorted_checks = self._sort_checks(filtered_checks)
        return json.dumps(sorted_checks).encode('utf-8')

    def _filter_checks(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for (k, v) in checks.items() if self._should_check_key(k)}

    def _should_check_key(self, key: str) -> bool:
        if len(self._key_whitelist) == 0:
            return True
        return key in self._key_whitelist

    def _sort_checks(self, checks: Dict[str, Any]) -> Tuple[str, Any]:
        return sorted(checks.items(), key=lambda x: x[0])

    def _score_hash(self, hashed) -> float:
        return (int(hashed.hexdigest(), 16) % 100) / 100

    def toJSON(self) -> Dict[str, Any]:
        return {
            **super().toJSON(),
            'type': ConsistentHashPercentageBucketer.get_type(),
            'key_whitelist': list(self._key_whitelist),
        }

    @classmethod
    def fromJSON(
        cls,
        fields: Dict[str, Any],
    ) -> 'ConsistentHashPercentageBucketer':
        key_whitelist = fields.get('key_whitelist', [])
        percentage_fields = fields.get('percentage')
        percentage = None
        if percentage_fields is not None:
            percentage = PercentageFactory.create(percentage_fields)
        return cls(key_whitelist=key_whitelist, percentage=percentage)
