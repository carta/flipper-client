from datetime import datetime, timedelta
import json
from typing import Optional


class JSONSerializationMixin:
    def serialize(self, is_enabled: bool, ttl: Optional[int] = None):
        return json.dumps(
            self._create_record(is_enabled, ttl=ttl)
        ).encode('utf-8')

    def _create_record(
        self,
        is_enabled: bool,
        ttl: Optional[int] = None
    ) -> dict:
        return {
            'value': is_enabled,
            'options': {
                'ttl': ttl,
                'expiration_date': self._serialize_expiration_date(ttl),
            },
        }

    def _serialize_expiration_date(self, ttl: int) -> int:
        if ttl is None:
            return None
        expires_at = datetime.now() + timedelta(seconds=ttl)
        return int(expires_at.timestamp())

    def deserialize(self, serialized: bytes) -> dict:
        return json.loads(serialized.decode('utf-8'))
