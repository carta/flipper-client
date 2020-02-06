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

import enum


class EventType(enum.Enum):
    PRE_CREATE = "pre_create"
    POST_CREATE = "post_create"

    PRE_ENABLE = "pre_enable"
    POST_ENABLE = "post_enable"

    PRE_DISABLE = "pre_disable"
    POST_DISABLE = "post_disable"

    PRE_DESTROY = "pre_destroy"
    POST_DESTROY = "post_destroy"

    PRE_ADD_CONDITION = "pre_add_condition"
    POST_ADD_CONDITION = "post_add_condition"

    PRE_SET_CONDITIONS = "pre_set_conditions"
    POST_SET_CONDITIONS = "post_set_conditions"

    PRE_SET_CLIENT_DATA = "pre_set_client_data"
    POST_SET_CLIENT_DATA = "post_set_client_data"

    PRE_SET_BUCKETER = "pre_set_bucketer"
    POST_SET_BUCKETER = "post_set_bucketer"
