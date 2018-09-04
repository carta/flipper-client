import json
from typing import Iterator, Optional

from flipper_thrift.python.feature_flag_store.ttypes import (
    FeatureFlagStoreItem as TFeatureFlagStoreItem
)

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


class ThriftRPCFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, client):
        self._client = client

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        return self._client.Create(feature_name, is_enabled, client_data)

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        item = self._client.Get(feature_name)
        return FeatureFlagStoreItem(
            feature_name,
            item.is_enabled,
            self._meta_from_thrift(item)
        )

    def _meta_from_thrift(
        self, item: TFeatureFlagStoreItem
    ) -> FeatureFlagStoreMeta:
        client_data = {}
        if item.meta.client_data is not None:
            client_data = json.loads(item.meta.client_data)

        return FeatureFlagStoreMeta(item.meta.created_date, client_data)

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
    ):
        return self._client.Set(feature_name, is_enabled)

    def delete(self, feature_name: str):
        return self._client.Delete(feature_name)

    def list(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Iterator[FeatureFlagStoreItem]:
        return self._client.List(limit, offset)

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        self._client.SetMeta(feature_name, json.dumps(meta.to_dict()))
