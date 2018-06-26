import logging
from typing import Optional, Tuple
import threading

from gevent.threadpool import ThreadPool

from .store import AbstractFeatureFlagStore


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
            self._set_value(item['Key'], item['Value'])

    def _set_value(self, key: str, value: str):
        self._cache[key] = self._deserialize(value)

    def create(self, feature_name: str, default: Optional[bool]=False):
        self.set(feature_name, default)

    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        return self._cache.get(self._make_key(feature_name), default)

    def _make_key(self, feature_name: str) -> str:
        return '/'.join([self.base_key, feature_name])

    def set(self, feature_name: str, value: bool):
        self._consul.kv.put(
            self._make_key(feature_name),
            self._serialize(value),
        )
        self._set_value(feature_name, value)

    def _serialize(self, value: bool) -> str:
        return b'1' if value is True else b'0'

    def _deserialize(self, value: str) -> bool:
        if value is None:
            return None
        return bool(int(value))

    def delete(self, feature_name: str):
        self._consul.kv.delete(self._make_key(feature_name))
