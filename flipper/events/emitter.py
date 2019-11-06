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

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional

from pyee import BaseEventEmitter

from .subscriber import FlipperEventSubscriber
from .types import EventType


class IEventEmitter(metaclass=ABCMeta):
    @abstractmethod
    def emit(self, event: Any, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def on(self, event: Any, f: Optional[Callable] = None) -> bool:
        pass

    @abstractmethod
    def remove_listener(self, event: Any, f: Callable) -> None:
        pass

    @abstractmethod
    def remove_subscriber(self, subscriber: FlipperEventSubscriber) -> None:
        pass


class FlipperEventEmitter(BaseEventEmitter, IEventEmitter):
    def register_subscriber(self, subscriber: FlipperEventSubscriber) -> None:
        for event_type in EventType:
            self.on(event_type, f=self._handler_method_for(subscriber, event_type))

    def _handler_method_for(
        self, subscriber: FlipperEventSubscriber, event_type: EventType
    ) -> Callable:
        return getattr(subscriber, "on_%s" % event_type.value)

    def remove_subscriber(self, subscriber: FlipperEventSubscriber) -> None:
        for event_type in EventType:
            self.remove_listener(
                event_type, f=self._handler_method_for(subscriber, event_type)
            )
