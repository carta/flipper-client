import grpc
from proto.python.feature_flag_store_pb2 import (
    CreateRequest,
    DeleteRequest,
    GetRequest,
    SetRequest,
)
from proto.python.feature_flag_store_pb2_grpc import FeatureFlagStoreStub

from .store import AbstractFeatureFlagStore


class GRPCFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, channel):
        self._channel = channel
        self._stub = FeatureFlagStoreStub(self._channel)

    def create(self, feature_name: str, default: Optional[bool]=False):
        self._stub.Create(
            CreateRequest(
                feature_name=feature_name,
                enabled=default,
            )
        )

    def _raise_for_error(self, result):
        if result is not None:
            raise PBMessageException

    def get(self, feature_name: str, default: Optional[bool]=False) -> bool:
        self._stub.Get(
            GetRequest(
                feature_name=feature_name,
                default=default,
            )
        )

    def set(self, feature_name: str, value: bool):
        self._stub.Set(
            SetRequest(
                feature_name=feature_name,
                enabled=value,
            )
        )

    def delete(self, feature_name: str):
        self._stub.Delete(DeleteRequest(feature_name=feature_name))


class PBMessageException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Request failed with code %i: %s' % (self.code, self.message)
