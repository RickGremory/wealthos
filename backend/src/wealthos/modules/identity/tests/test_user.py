"""Identity domain tests."""

import pytest

from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import InvalidEmail
from wealthos.modules.identity.domain.value_objects.email import Email


def test_email_normalizes_to_lowercase() -> None:
    assert Email("Ricardo@Example.COM").value == "ricardo@example.com"


def test_email_rejects_invalid() -> None:
    with pytest.raises(InvalidEmail):
        Email("not-an-email")


def test_user_create_factory() -> None:
    user = User.create(email="Ricardo@Example.com", display_name="Ricardo Balam")
    assert user.email.value == "ricardo@example.com"
    assert user.display_name.value == "Ricardo Balam"
    assert user.is_active is True
