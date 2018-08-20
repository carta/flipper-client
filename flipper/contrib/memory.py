from datetime import datetime
from typing import Optional

from .interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


class MemoryFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self):
        self._memory = {}

    def create(
        self,
        feature_name: str,
        is_enabled: Optional[bool] = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlagStoreItem:
        item = FeatureFlagStoreItem(
            feature_name,
            is_enabled,
            FeatureFlagStoreMeta(now(), client_data),
        )
        return self._save(item)

    def _save(self, item: FeatureFlagStoreItem):
        self._memory[item.feature_name] = item
        return item

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        return self._memory.get(feature_name)

    def set(
        self,
        feature_name: str,
        is_enabled: bool,
    ):
        existing = self.get(feature_name)

        if existing is None:
            self.create(feature_name, is_enabled)
            return

        item = FeatureFlagStoreItem(
            feature_name,
            is_enabled,
            FeatureFlagStoreMeta.fromJSON(existing.meta),
        )
        self._save(item)

    def delete(self, feature_name: str):
        if feature_name in self._memory:
            del self._memory[feature_name]

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        existing = self.get(feature_name)

        if existing is None:
            raise FlagDoesNotExistError('Feature %s does not exist' % feature_name)  # noqa: E501

        item = FeatureFlagStoreItem(
            feature_name,
            existing.is_enabled(),
            meta,
        )

        self._save(item)
