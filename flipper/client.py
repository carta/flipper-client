# Copyright 2018 eShares, Inc. dba Carta, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from typing import Iterable, Iterator, Optional, cast

from .bucketing.base import AbstractBucketer
from .conditions import Condition
from .contrib.interface import AbstractFeatureFlagStore
from .contrib.storage import FeatureFlagStoreItem, FeatureFlagStoreMeta
from .events import EventType, FlipperEventEmitter, IEventEmitter
from .exceptions import FlagDoesNotExistError
from .flag import FeatureFlag


def flag_must_exist(fn):
    def wrapper(self, feature_name: str, *args, **kwargs):
        if not self.exists(feature_name):
            raise FlagDoesNotExistError()
        return fn(self, feature_name, *args, **kwargs)

    return wrapper


class FeatureFlagClient:
    def __init__(self, store: AbstractFeatureFlagStore) -> None:
        self._store = store
        self._event_emitter = FlipperEventEmitter()  # type: IEventEmitter

    def get_events(self) -> IEventEmitter:
        return self._event_emitter

    def set_events(self, event_emitter: IEventEmitter):
        self._event_emitter = event_emitter

    events = property(get_events, set_events)

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ) -> FeatureFlag:
        self._event_emitter.emit(
            EventType.PRE_CREATE,
            feature_name,
            is_enabled=is_enabled,
            client_data=client_data,
        )

        self._store.create(feature_name, is_enabled=is_enabled, client_data=client_data)

        self._event_emitter.emit(
            EventType.POST_CREATE,
            feature_name,
            is_enabled=is_enabled,
            client_data=client_data,
        )

        return self.get(feature_name)

    def is_enabled(self, feature_name: str, default=False, **conditions) -> bool:
        item = self._store.get(feature_name)
        if item is None:
            return default
        return item.is_enabled(**conditions)

    def exists(self, feature_name: str):
        return self._store.get(feature_name) is not None

    def get(self, feature_name: str) -> FeatureFlag:
        return FeatureFlag(feature_name, self)

    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlag]:
        for item in self._store.list(limit=limit, offset=offset):
            yield self.get(item.feature_name)

    @flag_must_exist
    def enable(self, feature_name: str):
        self._event_emitter.emit(EventType.PRE_ENABLE, feature_name)
        self._store.set(feature_name, True)
        self._event_emitter.emit(EventType.POST_ENABLE, feature_name)

    @flag_must_exist
    def disable(self, feature_name: str):
        self._event_emitter.emit(EventType.PRE_DISABLE, feature_name)
        self._store.set(feature_name, False)
        self._event_emitter.emit(EventType.POST_DISABLE, feature_name)

    @flag_must_exist
    def destroy(self, feature_name: str):
        self._event_emitter.emit(EventType.PRE_DESTROY, feature_name)
        self._store.delete(feature_name)
        self._event_emitter.emit(EventType.POST_DESTROY, feature_name)

    @flag_must_exist
    def add_condition(self, feature_name: str, condition: Condition):
        meta = FeatureFlagStoreMeta.from_dict(self.get_meta(feature_name))

        meta.conditions.append(condition)

        self._event_emitter.emit(EventType.PRE_ADD_CONDITION, feature_name, condition)
        self._store.set_meta(feature_name, meta)
        self._event_emitter.emit(EventType.POST_ADD_CONDITION, feature_name, condition)

    @flag_must_exist
    def set_client_data(self, feature_name: str, client_data: dict):
        meta = FeatureFlagStoreMeta.from_dict(self.get_meta(feature_name))

        meta.update(client_data=client_data)

        self._event_emitter.emit(
            EventType.PRE_SET_CLIENT_DATA, feature_name, meta.client_data
        )
        self._store.set_meta(feature_name, meta)
        self._event_emitter.emit(
            EventType.POST_SET_CLIENT_DATA, feature_name, meta.client_data
        )

    def get_client_data(self, feature_name: str) -> dict:
        return self.get_meta(feature_name)["client_data"]

    @flag_must_exist
    def get_meta(self, feature_name: str) -> dict:
        return cast(FeatureFlagStoreItem, self._store.get(feature_name)).meta

    @flag_must_exist
    def set_bucketer(self, feature_name: str, bucketer: AbstractBucketer):
        meta = FeatureFlagStoreMeta.from_dict(self.get_meta(feature_name))

        meta.update(bucketer=bucketer)

        self._event_emitter.emit(EventType.PRE_SET_BUCKETER, feature_name, bucketer)
        self._store.set_meta(feature_name, meta)
        self._event_emitter.emit(EventType.POST_SET_BUCKETER, feature_name, bucketer)

    @flag_must_exist
    def set_conditions(self, feature_name: str, conditions: Iterable[Condition]):
        """
        This method will set the conditions to the feature flag.
        Contrary to `add_conditions` it will not append the condition, but will
        update the whole condition set the the new values provided.
        """
        meta = FeatureFlagStoreMeta.from_dict(self.get_meta(feature_name))

        meta.conditions = list(conditions)

        self._event_emitter.emit(EventType.PRE_SET_CONDITIONS, feature_name, conditions)
        self._store.set_meta(feature_name, meta)
        self._event_emitter.emit(
            EventType.POST_SET_CONDITIONS, feature_name, conditions
        )
