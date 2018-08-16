from datetime import datetime, timedelta
from typing import Optional


class FeatureFlagStoreMeta:
    def __init__(
        self,
        created_date: int,
        client_data: Optional[dict],
    ):
        self.created_date = created_date
        self.client_data = client_data or {}

    def toJSON(self):
        return {
            'client_data': self.client_data,
            'created_date': self.created_date,
        }

    @classmethod
    def fromJSON(cls, fields: dict):
        return cls(
            fields['created_date'],
            fields['client_data'],
        )

    def update(
        self,
        created_date: Optional[int]=None,
        client_data: Optional[dict]=None,
    ):
        if created_date is not None:
            self.created_date = created_date
        if client_data is not None:
            self._merge_client_data(client_data)

    def _merge_client_data(self, client_data: dict):
        self.client_data.update(client_data)
