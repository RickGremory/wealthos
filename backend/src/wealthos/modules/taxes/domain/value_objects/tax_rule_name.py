"""Tax rule name."""

from __future__ import annotations

import re

from wealthos.modules.taxes.domain.exceptions import TaxRuleNameEmpty, TaxRuleNameTooLong

_MULTI = re.compile(r"\s+")
MIN_LENGTH = 2
MAX_LENGTH = 120


class TaxRuleName:
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        cleaned = _MULTI.sub(" ", value.strip())
        if len(cleaned) < MIN_LENGTH:
            raise TaxRuleNameEmpty(f"Tax rule name must be at least {MIN_LENGTH} characters.")
        if len(cleaned) > MAX_LENGTH:
            raise TaxRuleNameTooLong(f"Tax rule name cannot exceed {MAX_LENGTH} characters.")
        self._value = cleaned

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaxRuleName):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)
