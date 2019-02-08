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

from typing import Optional

from .equality_operator import EqualityOperator
from .greater_than_operator import GreaterThanOperator
from .greater_than_or_equal_to_operator import GreaterThanOrEqualToOperator
from .less_than_operator import LessThanOperator
from .less_than_or_equal_to_operator import LessThanOrEqualToOperator
from .negated_set_membership_operator import NegatedSetMembershipOperator
from .negation_operator import NegationOperator
from .set_membership_operator import SetMembershipOperator


class Operator:
    OPERATOR_MAP = {
        EqualityOperator.SYMBOL: EqualityOperator,
        GreaterThanOperator.SYMBOL: GreaterThanOperator,
        GreaterThanOrEqualToOperator.SYMBOL: GreaterThanOrEqualToOperator,
        LessThanOperator.SYMBOL: LessThanOperator,
        LessThanOrEqualToOperator.SYMBOL: LessThanOrEqualToOperator,
        NegationOperator.SYMBOL: NegationOperator,
        SetMembershipOperator.SYMBOL: SetMembershipOperator,
        NegatedSetMembershipOperator.SYMBOL: NegatedSetMembershipOperator,
    }  # Dict[Optional[str], Any]

    class InvalidSymbolError(Exception):
        pass

    @classmethod
    def factory(cls, operator_symbol: Optional[str]):
        try:
            return cls.OPERATOR_MAP[operator_symbol]()  # type: ignore
        except KeyError:
            raise cls.InvalidSymbolError("Operator not supported: %s" % operator_symbol)
