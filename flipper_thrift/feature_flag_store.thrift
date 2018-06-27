service FeatureFlagStore {
    void Create(1: string feature_name, 2: bool is_enabled = false),
    void Delete(1: string feature_name),
    bool Get(1: string feature_name),
    bool Set(1: string feature_name, 2: bool is_enabled)
}
