import pytest

from wealthos.modules.organizations.domain.exceptions import InvalidTimezone
from wealthos.modules.organizations.domain.value_objects.timezone import Timezone


def test_timezone_accepts_iana() -> None:
    assert Timezone("America/Cancun").value == "America/Cancun"


def test_timezone_rejects_invalid() -> None:
    with pytest.raises(InvalidTimezone):
        Timezone("Not/A_Zone")
