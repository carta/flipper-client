from .contrib.interface import AbstractFeatureFlagStore



class FlagDoesNotExistError(Exception):
    pass


def flag_must_exist(fn):
    def wrapper(self, *args, **kwargs):
        item = self._store.get(self.name)
        if item is None:
            raise FlagDoesNotExistError()
        return fn(self, *args, **kwargs)
    return wrapper


class FeatureFlag:
    def __init__(self, feature_name: str, store: AbstractFeatureFlagStore):
        self.name = feature_name
        self._store = store

    def is_enabled(self, default=False) -> bool:
        item = self._store.get(self.name)
        if item is None:
            return default
        return item.is_enabled()

    @flag_must_exist
    def enable(self):
        self._store.set(self.name, True)

    @flag_must_exist
    def disable(self):
        self._store.set(self.name, False)

    @flag_must_exist
    def destroy(self):
        self._store.delete(self.name)

    @flag_must_exist
    def add_condition(self, condition):
        raise NotImplementedError()
