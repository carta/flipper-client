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
