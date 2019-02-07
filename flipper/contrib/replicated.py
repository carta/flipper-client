from threading import Thread
from typing import Callable, Dict, Iterator, Optional, Tuple

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta


class ReplicatedFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(  # type: ignore
        self,
        primary: AbstractFeatureFlagStore,
        *replicas: AbstractFeatureFlagStore,
        replication_timeout=1,
    ):
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
        def perform_create_on_store(store, *args, **kwargs):
            store.create(*args, **kwargs)

        args = (feature_name,)
        kwargs = {"is_enabled": is_enabled, "client_data": client_data}

        perform_create_on_store(self._primary, *args, **kwargs)

        self._replicate(
            perform_create_on_store, asynch=asynch, args=args, kwargs=kwargs
        )

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
        def perform_set_on_store(store, *args, **kwargs):
            store.set(*args, **kwargs)

        args = (feature_name, is_enabled)

        perform_set_on_store(self._primary, *args)

        self._replicate(perform_set_on_store, asynch=asynch, args=args)

    def delete(self, feature_name: str, asynch: Optional[bool] = True) -> None:
        def perform_delete_on_store(store, *args, **kwargs):
            store.delete(*args, **kwargs)

        perform_delete_on_store(self._primary, feature_name)

        self._replicate(perform_delete_on_store, asynch=asynch, args=(feature_name,))

    def list(self, *args, **kwargs) -> Iterator[FeatureFlagStoreItem]:
        return self._primary.list(*args, **kwargs)

    def set_meta(
        self,
        feature_name: str,
        meta: FeatureFlagStoreMeta,
        asynch: Optional[bool] = True,
    ) -> None:
        def perform_set_meta_on_store(store, *args, **kwargs):
            store.set_meta(*args, **kwargs)

        args = (feature_name, meta)

        perform_set_meta_on_store(self._primary, *args)

        self._replicate(perform_set_meta_on_store, asynch=asynch, args=args)
