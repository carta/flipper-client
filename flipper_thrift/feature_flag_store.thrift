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


namespace java com.carta.flipper

exception FlipperException {
    1: optional ErrorCode code;
    2: optional string message = "";
}

enum ErrorCode {
    NOT_FOUND
}

typedef string JSON

typedef map<string, list<ConditionCheck>> Condition

struct ConditionCheck {
    1: optional string variable;
    2: optional JSON value;
    3: optional ConditionOperator operator;
}

struct ConditionOperator {
    1: optional string symbol;
}

struct FeatureFlagStoreItem {
    1: optional string feature_name;
    2: optional bool is_enabled;
    3: optional FeatureFlagStoreMeta meta;
}

struct FeatureFlagStoreMeta {
    1: optional i64 created_date;
    2: optional JSON client_data;
    3: optional list<Condition> conditions;
    4: optional JSON bucketer;
}

service FeatureFlagStore {
    FeatureFlagStoreItem Create(1: string feature_name, 2: bool is_enabled, 3: JSON client_data) throws (1: FlipperException error),

    FeatureFlagStoreItem Get(1: string feature_name) throws (1: FlipperException error),

    void Set(1: string feature_name, 2: bool is_enabled) throws (1: FlipperException error),

    void Delete(1: string feature_name) throws (1: FlipperException error),

    list<FeatureFlagStoreItem> List(1: i64 limit, 2: i64 offset) throws (1: FlipperException error),

    void SetMeta(1: string feature_name, 2: FeatureFlagStoreMeta meta) throws (1: FlipperException error)
}
