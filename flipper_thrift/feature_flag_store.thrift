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

service FeatureFlagStore {
    void Create(1: string feature_name, 2: bool is_enabled = false, 3: string client_data),
    void Delete(1: string feature_name),
    FeatureFlagStoreItem Get(1: string feature_name),
    void Set(1: string feature_name, 2: bool is_enabled)
    void SetMeta(1: string feature_name, 2: string meta)
    list<FeatureFlagStoreItem> List(1: i64 limit, 2: i64 offset)
}


struct FeatureFlagStoreItem {
    1: required string feature_name;
    2: required bool is_enabled;
    3: required FeatureFlagStoreMeta meta;
}


struct FeatureFlagStoreMeta {
    1: required i64 created_date;
    2: optional string client_data;
}
