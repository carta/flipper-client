from datetime import datetime, timedelta
from typing import Optional


class FeatureFlagStoreMeta:
    def __init__(
        self,
        created_date: int,
        client_data: dict,
    ):
        self.created_date = created_date
        self.client_data = client_data

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
