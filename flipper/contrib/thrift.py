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

"""
   isort:skip_file
   See: https://github.com/ambv/black/issues/250
"""
import json
from typing import Any, Dict, Iterator, List, Optional  # noqa: F401

from flipper_thrift.python.feature_flag_store import ttypes

from .interface import AbstractFeatureFlagStore
from .storage import FeatureFlagStoreItem, FeatureFlagStoreMeta

from ..bucketing import BucketerFactory
from ..bucketing.base import AbstractBucketer
from ..conditions import Condition
from ..conditions.check import Check
from ..exceptions import FlagDoesNotExistError


class ThriftRPCFeatureFlagStore(AbstractFeatureFlagStore):
    def __init__(self, client, ttypes=ttypes):
        self._client = client
        self._ttypes = ttypes

    def create(
        self,
        feature_name: str,
        is_enabled: bool = False,
        client_data: Optional[dict] = None,
    ):
        item = self._client.Create(
            feature_name, is_enabled, json.dumps(client_data or {})
        )
        return self._convert_titem_to_item(item)

    def get(self, feature_name: str) -> Optional[FeatureFlagStoreItem]:
        try:
            item = self._client.Get(feature_name)
        except self._ttypes.FlipperException as e:
            if e.code == self._ttypes.ErrorCode.NOT_FOUND:
                return None
            raise
        return self._convert_titem_to_item(item)

    def _convert_titem_to_item(self, item) -> FeatureFlagStoreItem:
        return FeatureFlagStoreItem(
            item.feature_name, item.is_enabled, self._convert_tmeta_to_meta(item.meta)
        )

    def _convert_tmeta_to_meta(self, tmeta) -> FeatureFlagStoreMeta:
        meta = FeatureFlagStoreMeta(created_date=tmeta.created_date)

        if tmeta.client_data is not None:
            meta.client_data = self._convert_thrift_to_client_data(tmeta.client_data)

        if tmeta.conditions is not None:
            meta.conditions = self._convert_thrift_to_conditions(tmeta.conditions)

        if tmeta.bucketer is not None:
            meta.bucketer = self._convert_thrift_to_bucketer(tmeta.bucketer)

        return meta

    def _convert_thrift_to_client_data(self, client_data: str) -> Dict:
        return json.loads(client_data)

    def _convert_thrift_to_conditions(
        self, conditions: List[Dict[str, List]]
    ) -> List[Condition]:
        return [
            Condition(
                **{
                    Check.make_check_key(
                        check.variable, check.operator.symbol
                    ): json.loads(check.value)
                }
            )
            for condition in conditions
            for checks in condition.values()
            for check in checks
        ]

    def _convert_thrift_to_bucketer(self, bucketer: str) -> AbstractBucketer:
        return BucketerFactory.create(json.loads(bucketer))

    def set(self, feature_name: str, is_enabled: bool):
        return self._client.Set(feature_name, is_enabled)

    def delete(self, feature_name: str):
        return self._client.Delete(feature_name)

    def list(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> Iterator[FeatureFlagStoreItem]:
        return (
            self._convert_titem_to_item(item)
            for item in self._client.List(limit, offset)
        )

    def set_meta(self, feature_name: str, meta: FeatureFlagStoreMeta):
        try:
            self._client.SetMeta(feature_name, self._convert_meta_to_tmeta(meta))
        except self._ttypes.FlipperException as e:
            if e.code == self._ttypes.ErrorCode.NOT_FOUND:
                raise FlagDoesNotExistError("Feature %s does not exist" % feature_name)
            raise

    def _convert_meta_to_tmeta(self, meta: FeatureFlagStoreMeta):
        tmeta = self._ttypes.FeatureFlagStoreMeta(created_date=meta.created_date)

        if meta.client_data is not None:
            tmeta.client_data = self._convert_client_data_to_thrift(meta.client_data)

        if meta.conditions is not None:
            tmeta.conditions = self._convert_conditions_to_thrift(meta.conditions)

        if meta.bucketer is not None:
            tmeta.bucketer = self._convert_bucketer_to_thrift(meta.bucketer)

        return tmeta

    def _convert_client_data_to_thrift(self, client_data: dict) -> str:
        return json.dumps(client_data)

    def _convert_conditions_to_thrift(
        self, conditions: List[Condition]
    ) -> List[Dict[str, List]]:
        return [
            {
                variable: [
                    self._ttypes.ConditionCheck(
                        variable=variable,
                        value=json.dumps(check.value),
                        operator=self._ttypes.ConditionOperator(
                            symbol=check.operator.SYMBOL
                        ),
                    )
                    for check in checks
                ]
                for variable, checks in condition.checks.items()
            }
            for condition in conditions
        ]

    def _convert_bucketer_to_thrift(self, bucketer: AbstractBucketer) -> str:
        return json.dumps(bucketer.to_dict())
