from threading import Thread
from typing import Callable, Dict, Iterator, Optional, Tuple

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class ReplicatedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(
        self,
        primary: AbstractFeatureFlagStore,
        *replicas: AbstractFeatureFlagStore,
        replication_timeout=1,
    ) -> None:
        self._primary = primary
        self._replicas = replicas
        self._stores = [primary] + list(replicas)
        self._replication_timeout = replication_timeout

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
        asynch: Optional[bool] = True,
    ) -> None:
        def create(store, *args, **kwargs):
            store.create(*args, **kwargs)

        args = (feature_name,)
        kwargs = {"is_enabled": is_enabled, "client_data": client_data}

        create(self._primary, *args, **kwargs)

        self._replicate(create, asynch=asynch, args=args, kwargs=kwargs)

    def _replicate(
        self,
        fn: Callable,
        asynch: Optional[bool] = True,
        args: Tuple = (),
        kwargs: Dict = {},
    ) -> None:
        threads = []

        for replica in self._replicas:
            threads.append(self._start_thread(fn, args=(replica, *args), kwargs=kwargs))

        if asynch is False:
            return

        for thread in threads:
            thread.join(timeout=self._replication_timeout)

    def _start_thread(
        self, fn: Callable, args: Tuple = (), kwargs: Dict = {}
    ) -> Thread:
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread

    def get(self, *args, **kwargs) -> Optional[FeatureFlagStoreItem]:
        return self._primary.get(*args, **kwargs)

    def set(
        self, feature_name: str, is_enabled: bool, asynch: Optional[bool] = True
    ) -> None:
        def set_(store, *args, **kwargs):
            store.set(*args, **kwargs)

        args = (feature_name, is_enabled)

        set_(self._primary, *args)

        self._replicate(set_, asynch=asynch, args=args)

    def delete(self, feature_name: str, asynch: Optional[bool] = True) -> None:
        def delete(store, *args, **kwargs):
            store.delete(*args, **kwargs)

        delete(self._primary, feature_name)

        self._replicate(delete, asynch=asynch, args=(feature_name,))

    def list(self, *args, **kwargs) -> Iterator[FeatureFlagStoreItem]:
        return self._primary.list(*args, **kwargs)

    def set_meta(
        self,
        feature_name: str,
        meta: FeatureFlagStoreMeta,
        asynch: Optional[bool] = True,
    ) -> None:
        def set_meta(store, *args, **kwargs):
            store.set_meta(*args, **kwargs)

        args = (feature_name, meta)

        set_meta(self._primary, *args)

        self._replicate(set_meta, asynch=asynch, args=args)
