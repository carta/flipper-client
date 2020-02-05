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

from typing import Iterable, Optional

from flipper.bucketing.base import AbstractBucketer
from flipper.conditions import Condition


class FlipperEventSubscriber:
    def on_pre_create(
        self, flag_name: str, is_enabled: bool, client_data: Optional[dict]
    ):
        pass

    def on_post_create(
        self, flag_name: str, is_enabled: bool, client_data: Optional[dict]
    ):
        pass

    def on_pre_enable(self, flag_name: str):
        pass

    def on_post_enable(self, flag_name: str):
        pass

    def on_pre_disable(self, flag_name: str):
        pass

    def on_post_disable(self, flag_name: str):
        pass

    def on_pre_destroy(self, flag_name: str):
        pass

    def on_post_destroy(self, flag_name: str):
        pass

    def on_pre_add_condition(self, flag_name: str, condition: Condition):
        pass

    def on_post_add_condition(self, flag_name: str, condition: Condition):
        pass

    def on_pre_set_conditions(self, flag_name: str, conditions: Iterable[Condition]):
        pass

    def on_post_set_conditions(self, flag_name: str, conditions: Iterable[Condition]):
        pass

    def on_pre_set_client_data(self, flag_name: str, client_data: dict):
        pass

    def on_post_set_client_data(self, flag_name: str, client_data: dict):
        pass

    def on_pre_set_bucketer(self, flag_name: str, bucketer: AbstractBucketer):
        pass

    def on_post_set_bucketer(self, flag_name: str, bucketer: AbstractBucketer):
        pass
