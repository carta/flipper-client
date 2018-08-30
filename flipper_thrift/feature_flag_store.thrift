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
