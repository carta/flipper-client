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

from typing import Any, Tuple

from .operators import Operator
from .operators.interface import AbstractOperator

OPERATOR_DELIMITER = "__"


class Check:
    def __init__(self, variable: str, value: Any, operator: AbstractOperator) -> None:
        self._variable = variable
        self._value = value
        self._operator = operator

    @property
    def variable(self):
        return self._variable

    @property
    def value(self):
        return self._value

    @property
    def operator(self):
        return self._operator

    def check(self, value):
        return self._operator.compare(value, self._value)

    @classmethod
    def factory(cls, check_key: str, check_value: Any):
        variable, operator = cls._parse_check_key(check_key)
        return cls(variable, check_value, operator)

    @classmethod
    def _parse_check_key(cls, check_key: str) -> Tuple[str, AbstractOperator]:
        variable, raw_operator = check_key, None

        try:
            variable, raw_operator = check_key.split(OPERATOR_DELIMITER)
        except ValueError:
            pass

        return variable, Operator.factory(raw_operator)

    def to_dict(self) -> dict:
        return {
            "variable": self._variable,
            "value": self._value,
            "operator": self._operator.SYMBOL,
        }

    @classmethod
    def from_dict(cls, fields: dict) -> "Check":
        return cls(
            fields["variable"], fields["value"], Operator.factory(fields["operator"])
        )

    @classmethod
    def make_check_key(cls, variable: str, operator: str) -> str:
        if operator is None:
            return variable
        return OPERATOR_DELIMITER.join([variable, operator])
