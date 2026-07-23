"""Money value object — Decimal amounts, never float."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from wealthos.shared.domain.exceptions import CurrencyMismatch
from wealthos.shared.domain.value_objects.currency import Currency

_TWOPLACES = Decimal("0.01")


def _to_decimal(amount: Decimal | str | int) -> Decimal:
    if isinstance(amount, float):  # noqa: UP038 — explicit runtime guard
        raise TypeError("Money does not accept float; use str or Decimal.")
    try:
        value = amount if isinstance(amount, Decimal) else Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid money amount: {amount!r}") from exc
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


class Money:
    """Immutable monetary amount with currency."""

    __slots__ = ("_amount", "_currency")

    def __init__(self, amount: Decimal | str | int, currency: Currency | str) -> None:
        self._amount = _to_decimal(amount)
        self._currency = currency if isinstance(currency, Currency) else Currency(currency)

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._currency

    def __add__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._ensure_same_currency(other)
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other: object) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        self._ensure_same_currency(other)
        return Money(self._amount - other._amount, self._currency)

    def _ensure_same_currency(self, other: Money) -> None:
        if self._currency != other._currency:
            raise CurrencyMismatch(
                f"Cannot operate on {self._currency.value} and {other._currency.value}."
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self._amount == other._amount and self._currency == other._currency

    def __repr__(self) -> str:
        return f"Money({str(self._amount)!r}, {self._currency!r})"

    def __str__(self) -> str:
        return f"{self._amount} {self._currency.value}"
