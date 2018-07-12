from datetime import datetime
import logging
from typing import Optional, Tuple
import threading

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


logger = logging.getLogger(__name__)


class ConsulFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(
        self,
        consul,
        base_key='features'
    ):
        self._cache = {}
        self._consul = consul
        self.base_key = base_key

        self._start()

    def _start(self):
        logger.debug('Spawning a thread to track changes in consul')

        self._thread = threading.Thread(target=self._watch)
        self._thread.daemon = True
        self._thread.start()

    def _watch(self):
        index = None
        while True:
            index, data = self._consul.kv.get(self.base_key, recurse=True)
            self._parse_data(data)

    def _parse_data(self, data: Tuple[dict]):
        for item in data:
            serialized = item['Value']

            deserialized = None

            if serialized is not None:
                deserialized = FeatureFlagStoreItem.deserialize(serialized)

            self._set_item_in_cache(item['Key'], deserialized)

    def _set_item_in_cache(self, key: str, item: FeatureFlagStoreItem):
        self._cache[key] = item

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        self.set(feature_name, is_enabled, client_data=client_data)
        return self.get(feature_name)

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        return self._cache.get(self._make_key(feature_name))

    def _make_key(self, feature_name: str) -> str:
        return '/'.join([self.base_key, feature_name])

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
        client_data: Optional[dict] = None,
    ):
        client_data = client_data or {}

        item = FeatureFlagStoreItem(
            feature_name,
            is_enabled,
            FeatureFlagStoreMeta(now(), client_data)
        )

        self._consul.kv.put(
            self._make_key(feature_name),
            item.serialize(),
        )

        self._set_item_in_cache(feature_name, item)

    def delete(self, feature_name: str):
        self._consul.kv.delete(self._make_key(feature_name))
