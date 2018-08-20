from datetime import datetime, timedelta
from typing import List, Optional

from flipper.conditions import Condition


class FeatureFlagStoreMeta:
    def __init__(
        self,
        created_date: int,
        client_data: Optional[dict] = None,
        conditions: Optional[List[Condition]] = None,
    ):
        self.created_date = created_date
        self.client_data = client_data or {}
        self.conditions = conditions or []

    def toJSON(self):
        return {
            'client_data': self.client_data,
            'created_date': self.created_date,
            'conditions': [
                condition.toJSON() for condition in self.conditions
            ],
        }

    @classmethod
    def fromJSON(cls, fields: dict):
        return cls(
            fields['created_date'],
            client_data=fields['client_data'],
            conditions=[
                Condition.fromJSON(condition)
                for condition in fields['conditions']
            ],
        )

    def update(
        self,
        created_date: Optional[int]=None,
        client_data: Optional[dict]=None,
        conditions: Optional[List[Condition]]=None,
    ):
        if created_date is not None:
            self.created_date = created_date
        if client_data is not None:
            self._merge_client_data(client_data)
        if conditions is not None:
            self.conditions = conditions

    def _merge_client_data(self, client_data: dict):
        self.client_data.update(client_data)
