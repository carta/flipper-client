from datetime import datetime
from typing import Optional, List

from .interface import AbstractFeatureFlagStore, FlagDoesNotExistError
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .util.date import now


class RedisFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, redis, base_key='features'):
        self._redis = redis
        self.base_key = 'features'

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

    def _save(self, item: FeatureFlagStoreItem) -> FeatureFlagStoreItem:
        self._redis.set(
            self._key_name(item.feature_name),
            item.serialize(),
        )
        return item

    def get(self, feature_name: str) -> FeatureFlagStoreItem:
        serialized = self._redis.get(self._key_name(feature_name))
        if not serialized:
            return None
        return FeatureFlagStoreItem.deserialize(serialized)

    def _key_name(self, feature_name: str) -> str:
        return '/'.join([self.base_key, feature_name])

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

    def set_client_data(
        self,
        feature_name: str,
        client_data: dict,
    ):
        existing = self.get(feature_name)

        if existing is None:
            raise FlagDoesNotExistError('Feature %s does not exist' % feature_name)  # noqa: E501

        updated_meta = self._get_merged_meta(existing.meta, client_data)

        item = FeatureFlagStoreItem(
            feature_name,
            existing.is_enabled(),
            FeatureFlagStoreMeta.fromJSON(updated_meta),
        )

        self._save(item)

    def _get_merged_meta(
        self, existing_meta: dict, client_data: dict
    ) -> dict:
        existing_meta['client_data'] = {
            **existing_meta['client_data'],
            **client_data,
        }
        return existing_meta

    def delete(self, feature_name: str):
        self._redis.delete(self._key_name(feature_name))
