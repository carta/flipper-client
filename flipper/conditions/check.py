from typing import Any, Tuple

from .operators import Operator

OPERATOR_DELIMITER = "__"


class Check:
    def __init__(self, variable: str, value: any, operator: Operator):
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
    def _parse_check_key(cls, check_key: str) -> Tuple[str, Operator]:
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
