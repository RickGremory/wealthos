"""RegisterUser command — create user, default organization, and owner membership."""

from __future__ import annotations

from dataclasses import dataclass, field

from wealthos.modules.categories.application.services.category_seed_service import (
    CategorySeedService,
)
from wealthos.modules.identity.application.services.access_token_service import (
    AccessTokenService,
)
from wealthos.modules.identity.application.services.organization_slug import (
    allocate_unique_slug,
)
from wealthos.modules.identity.application.services.password_hasher import PasswordHasher
from wealthos.modules.identity.application.services.password_policy import validate_password
from wealthos.modules.identity.domain.entities.user import User
from wealthos.modules.identity.domain.exceptions import UserEmailAlreadyExists
from wealthos.modules.identity.domain.repositories.user_repository import UserRepository
from wealthos.modules.identity.domain.value_objects.email import Email
from wealthos.modules.legal.application.services.legal_consent_service import (
    ConsentContext,
    LegalAcceptanceItem,
    LegalConsentService,
)
from wealthos.modules.organizations.domain.entities.organization import Organization
from wealthos.modules.organizations.domain.entities.organization_membership import (
    OrganizationMembership,
)
from wealthos.modules.organizations.domain.repositories.membership_repository import (
    MembershipRepository,
)
from wealthos.modules.organizations.domain.repositories.organization_repository import (
    OrganizationRepository,
)


@dataclass(frozen=True, slots=True)
class RegisterUserInput:
    email: str
    password: str
    display_name: str
    organization_name: str
    currency: str = "MXN"
    timezone: str = "America/Cancun"
    locale: str = "es-MX"
    legal_acceptances: list[LegalAcceptanceItem] = field(default_factory=list)
    marketing_consent: bool = False
    client_ip: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True, slots=True)
class RegisterUserResult:
    user: User
    organization: Organization
    membership: OrganizationMembership
    access_token: str
    expires_in: int


class RegisterUserCommand:
    """Register a user and provision their first owned organization."""

    def __init__(
        self,
        *,
        users: UserRepository,
        organizations: OrganizationRepository,
        memberships: MembershipRepository,
        category_seed: CategorySeedService,
        password_hasher: PasswordHasher,
        token_service: AccessTokenService,
        legal: LegalConsentService,
    ) -> None:
        self._users = users
        self._organizations = organizations
        self._memberships = memberships
        self._category_seed = category_seed
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._legal = legal

    def execute(self, data: RegisterUserInput) -> RegisterUserResult:
        email = Email(data.email)
        password = validate_password(data.password)

        documents = self._legal.validate_registration_acceptances(data.legal_acceptances)

        if self._users.get_by_email(email) is not None:
            raise UserEmailAlreadyExists(f"Email '{email.value}' is already registered.")

        user = User.create(email=data.email, display_name=data.display_name)
        password_hash = self._password_hasher.hash(password)
        stored_user = self._users.add(user, password_hash=password_hash)

        slug = allocate_unique_slug(self._organizations, data.organization_name)
        organization = Organization.create(
            name=data.organization_name,
            slug=slug,
            currency=data.currency,
            timezone=data.timezone,
            locale=data.locale,
        )
        stored_organization = self._organizations.add(organization)

        membership = OrganizationMembership.create(
            organization_id=stored_organization.id,
            user_id=stored_user.id,
            role="owner",
        )
        stored_membership = self._memberships.add(membership)

        self._category_seed.seed_defaults(stored_organization.id)

        self._legal.record_registration_consents(
            user_id=stored_user.id,
            organization_id=stored_organization.id,
            documents=documents,
            marketing_consent=data.marketing_consent,
            context=ConsentContext(
                ip_address=data.client_ip,
                user_agent=data.user_agent,
            ),
        )

        access_token = self._token_service.create(stored_user.id)
        return RegisterUserResult(
            user=stored_user,
            organization=stored_organization,
            membership=stored_membership,
            access_token=access_token,
            expires_in=self._token_service.expires_in_seconds,
        )
