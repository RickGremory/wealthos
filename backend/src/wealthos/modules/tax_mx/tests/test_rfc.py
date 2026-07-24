"""RFC value object tests."""

import pytest

from wealthos.modules.tax_mx.domain.exceptions import InvalidRFC
from wealthos.modules.tax_mx.domain.value_objects.rfc import RFC


def test_valid_individual_rfc() -> None:
    rfc = RFC("XAXX010101000")
    assert rfc.value == "XAXX010101000"


def test_valid_moral_rfc() -> None:
    rfc = RFC("ABC010101AB1")
    assert len(rfc.value) == 12 or len(rfc.value) == 13


def test_invalid_rfc_raises() -> None:
    with pytest.raises(InvalidRFC):
        RFC("invalid")
