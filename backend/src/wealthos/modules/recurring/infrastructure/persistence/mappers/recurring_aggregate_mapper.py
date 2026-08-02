"""Map RecurringAggregate ↔ SQLAlchemy models."""

from __future__ import annotations

from decimal import Decimal

from wealthos.modules.recurring.domain.entities.occurrence_exception import (
    RecurringOccurrenceException,
)
from wealthos.modules.recurring.domain.entities.occurrence_settlement import (
    RecurringOccurrenceSettlement,
)
from wealthos.modules.recurring.domain.entities.recurring_aggregate import (
    RecurringAggregate,
)
from wealthos.modules.recurring.domain.entities.recurring_rule import RecurringRule
from wealthos.modules.recurring.domain.entities.recurring_rule_pause import (
    RecurringRulePause,
)
from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.occurrence import (
    RecurringExceptionType,
    RecurringSettlementLinkType,
    RecurringSettlementMode,
)
from wealthos.modules.recurring.domain.enums.recurrence import (
    InvalidDatePolicy,
    RecurrenceFrequency,
    Weekday,
)
from wealthos.modules.recurring.domain.enums.rule import (
    RecurringAmountStrategy,
    RecurringCertainty,
    RecurringDirection,
    RecurringRuleStatus,
    RecurringSourceType,
)
from wealthos.modules.recurring.domain.value_objects.recurrence_pattern import (
    RecurrencePattern,
)
from wealthos.modules.recurring.infrastructure.persistence.models.recurring_models import (
    RecurringOccurrenceExceptionModel,
    RecurringOccurrenceSettlementModel,
    RecurringRuleModel,
    RecurringRulePauseModel,
    RecurringRuleVersionModel,
)


class RecurringAggregateMapper:
    def to_entity(self, model: RecurringRuleModel) -> RecurringAggregate:
        rule = RecurringRule(
            id=model.id,
            organization_id=model.organization_id,
            source_type=RecurringSourceType.parse(model.source_type),
            related_resource_type=model.related_resource_type,
            related_resource_id=model.related_resource_id,
            status=RecurringRuleStatus.parse(model.status),
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
        )
        versions = [self._version_to_entity(item) for item in model.versions]
        pauses = [self._pause_to_entity(item) for item in model.pauses]
        exceptions = [self._exception_to_entity(item) for item in model.exceptions]
        return RecurringAggregate(
            rule=rule,
            versions=versions,
            pauses=pauses,
            exceptions=exceptions,
        )

    def to_model(self, aggregate: RecurringAggregate) -> RecurringRuleModel:
        rule = aggregate.rule
        model = RecurringRuleModel(
            id=rule.id,
            organization_id=rule.organization_id,
            source_type=rule.source_type.value,
            related_resource_type=rule.related_resource_type,
            related_resource_id=rule.related_resource_id,
            status=rule.status.value,
            version=rule.version,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            archived_at=rule.archived_at,
        )
        model.versions = [
            self._version_to_model(item) for item in aggregate.versions
        ]
        model.pauses = [self._pause_to_model(item) for item in aggregate.pauses]
        model.exceptions = [
            self._exception_to_model(item) for item in aggregate.exceptions
        ]
        return model

    def apply_to_model(
        self,
        model: RecurringRuleModel,
        aggregate: RecurringAggregate,
    ) -> None:
        rule = aggregate.rule
        model.source_type = rule.source_type.value
        model.related_resource_type = rule.related_resource_type
        model.related_resource_id = rule.related_resource_id
        model.status = rule.status.value
        model.version = rule.version
        model.updated_at = rule.updated_at
        model.archived_at = rule.archived_at

        existing_versions = {item.id: item for item in model.versions}
        model.versions = []
        for version in aggregate.versions:
            row = existing_versions.get(version.id)
            if row is None:
                model.versions.append(self._version_to_model(version))
            else:
                self._apply_version(row, version)
                model.versions.append(row)

        existing_pauses = {item.id: item for item in model.pauses}
        model.pauses = []
        for pause in aggregate.pauses:
            row = existing_pauses.get(pause.id)
            if row is None:
                model.pauses.append(self._pause_to_model(pause))
            else:
                self._apply_pause(row, pause)
                model.pauses.append(row)

        existing_exceptions = {item.id: item for item in model.exceptions}
        model.exceptions = []
        for exception in aggregate.exceptions:
            row = existing_exceptions.get(exception.id)
            if row is None:
                model.exceptions.append(self._exception_to_model(exception))
            else:
                self._apply_exception(row, exception)
                model.exceptions.append(row)

    def settlement_to_entity(
        self,
        model: RecurringOccurrenceSettlementModel,
    ) -> RecurringOccurrenceSettlement:
        return RecurringOccurrenceSettlement(
            id=model.id,
            organization_id=model.organization_id,
            recurring_rule_id=model.recurring_rule_id,
            occurrence_key=model.occurrence_key,
            transaction_id=model.transaction_id,
            settled_amount=Decimal(model.settled_amount),
            link_type=RecurringSettlementLinkType.parse(model.link_type),
            linked_by=model.linked_by,
            linked_at=model.linked_at,
            created_at=model.created_at,
            voided_at=model.voided_at,
        )

    def settlement_to_model(
        self,
        entity: RecurringOccurrenceSettlement,
    ) -> RecurringOccurrenceSettlementModel:
        return RecurringOccurrenceSettlementModel(
            id=entity.id,
            organization_id=entity.organization_id,
            recurring_rule_id=entity.recurring_rule_id,
            occurrence_key=entity.occurrence_key,
            transaction_id=entity.transaction_id,
            settled_amount=entity.settled_amount,
            link_type=entity.link_type.value,
            linked_by=entity.linked_by,
            linked_at=entity.linked_at,
            created_at=entity.created_at,
            voided_at=entity.voided_at,
        )

    def _version_to_entity(self, model: RecurringRuleVersionModel) -> RecurringRuleVersion:
        days = tuple(Weekday.parse(day) for day in (model.days_of_week or []))
        pattern = RecurrencePattern(
            frequency=RecurrenceFrequency.parse(model.frequency),
            interval=model.interval,
            days_of_week=days,
            day_of_month=model.day_of_month,
            month_of_year=model.month_of_year,
            end_of_month=model.end_of_month,
            invalid_date_policy=InvalidDatePolicy.parse(model.invalid_date_policy),
        )
        return RecurringRuleVersion(
            id=model.id,
            recurring_rule_id=model.recurring_rule_id,
            organization_id=model.organization_id,
            effective_from=model.effective_from,
            effective_until=model.effective_until,
            name=model.name,
            direction=RecurringDirection.parse(model.direction),
            amount=Decimal(model.amount),
            currency=model.currency,
            amount_strategy=RecurringAmountStrategy.parse(model.amount_strategy),
            certainty=RecurringCertainty.parse(model.certainty),
            settlement_mode=RecurringSettlementMode.parse(model.settlement_mode),
            pattern=pattern,
            starts_on=model.starts_on,
            ends_on=model.ends_on,
            grace_period_days=model.grace_period_days,
            account_id=model.account_id,
            destination_account_id=model.destination_account_id,
            category_id=model.category_id,
            notes=model.notes,
            created_by=model.created_by,
            created_at=model.created_at,
        )

    def _version_to_model(self, entity: RecurringRuleVersion) -> RecurringRuleVersionModel:
        pattern = entity.pattern
        return RecurringRuleVersionModel(
            id=entity.id,
            recurring_rule_id=entity.recurring_rule_id,
            organization_id=entity.organization_id,
            effective_from=entity.effective_from,
            effective_until=entity.effective_until,
            name=entity.name,
            direction=entity.direction.value,
            amount=entity.amount,
            currency=entity.currency,
            amount_strategy=entity.amount_strategy.value,
            certainty=entity.certainty.value,
            settlement_mode=entity.settlement_mode.value,
            frequency=pattern.frequency.value,
            interval=pattern.interval,
            days_of_week=[int(day) for day in pattern.days_of_week],
            day_of_month=pattern.day_of_month,
            month_of_year=pattern.month_of_year,
            end_of_month=pattern.end_of_month,
            invalid_date_policy=pattern.invalid_date_policy.value,
            starts_on=entity.starts_on,
            ends_on=entity.ends_on,
            grace_period_days=entity.grace_period_days,
            account_id=entity.account_id,
            destination_account_id=entity.destination_account_id,
            category_id=entity.category_id,
            notes=entity.notes,
            created_by=entity.created_by,
            created_at=entity.created_at,
        )

    def _apply_version(
        self,
        model: RecurringRuleVersionModel,
        entity: RecurringRuleVersion,
    ) -> None:
        pattern = entity.pattern
        model.effective_from = entity.effective_from
        model.effective_until = entity.effective_until
        model.name = entity.name
        model.direction = entity.direction.value
        model.amount = entity.amount
        model.currency = entity.currency
        model.amount_strategy = entity.amount_strategy.value
        model.certainty = entity.certainty.value
        model.settlement_mode = entity.settlement_mode.value
        model.frequency = pattern.frequency.value
        model.interval = pattern.interval
        model.days_of_week = [int(day) for day in pattern.days_of_week]
        model.day_of_month = pattern.day_of_month
        model.month_of_year = pattern.month_of_year
        model.end_of_month = pattern.end_of_month
        model.invalid_date_policy = pattern.invalid_date_policy.value
        model.starts_on = entity.starts_on
        model.ends_on = entity.ends_on
        model.grace_period_days = entity.grace_period_days
        model.account_id = entity.account_id
        model.destination_account_id = entity.destination_account_id
        model.category_id = entity.category_id
        model.notes = entity.notes

    def _pause_to_entity(self, model: RecurringRulePauseModel) -> RecurringRulePause:
        return RecurringRulePause(
            id=model.id,
            recurring_rule_id=model.recurring_rule_id,
            organization_id=model.organization_id,
            starts_on=model.starts_on,
            ends_on=model.ends_on,
            reason=model.reason,
            created_by=model.created_by,
            version=model.version,
            created_at=model.created_at,
        )

    def _pause_to_model(self, entity: RecurringRulePause) -> RecurringRulePauseModel:
        return RecurringRulePauseModel(
            id=entity.id,
            recurring_rule_id=entity.recurring_rule_id,
            organization_id=entity.organization_id,
            starts_on=entity.starts_on,
            ends_on=entity.ends_on,
            reason=entity.reason,
            created_by=entity.created_by,
            version=entity.version,
            created_at=entity.created_at,
        )

    def _apply_pause(
        self,
        model: RecurringRulePauseModel,
        entity: RecurringRulePause,
    ) -> None:
        model.starts_on = entity.starts_on
        model.ends_on = entity.ends_on
        model.reason = entity.reason
        model.version = entity.version

    def _exception_to_entity(
        self,
        model: RecurringOccurrenceExceptionModel,
    ) -> RecurringOccurrenceException:
        return RecurringOccurrenceException(
            id=model.id,
            organization_id=model.organization_id,
            recurring_rule_id=model.recurring_rule_id,
            original_occurrence_key=model.original_occurrence_key,
            original_expected_on=model.original_expected_on,
            exception_type=RecurringExceptionType.parse(model.exception_type),
            replacement_expected_on=model.replacement_expected_on,
            replacement_amount=(
                Decimal(model.replacement_amount)
                if model.replacement_amount is not None
                else None
            ),
            replacement_certainty=(
                RecurringCertainty.parse(model.replacement_certainty)
                if model.replacement_certainty
                else None
            ),
            reason=model.reason,
            is_active=model.is_active,
            created_by=model.created_by,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deactivated_at=model.deactivated_at,
        )

    def _exception_to_model(
        self,
        entity: RecurringOccurrenceException,
    ) -> RecurringOccurrenceExceptionModel:
        return RecurringOccurrenceExceptionModel(
            id=entity.id,
            organization_id=entity.organization_id,
            recurring_rule_id=entity.recurring_rule_id,
            original_occurrence_key=entity.original_occurrence_key,
            original_expected_on=entity.original_expected_on,
            exception_type=entity.exception_type.value,
            replacement_expected_on=entity.replacement_expected_on,
            replacement_amount=entity.replacement_amount,
            replacement_certainty=(
                entity.replacement_certainty.value
                if entity.replacement_certainty
                else None
            ),
            reason=entity.reason,
            is_active=entity.is_active,
            created_by=entity.created_by,
            version=entity.version,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deactivated_at=entity.deactivated_at,
        )

    def _apply_exception(
        self,
        model: RecurringOccurrenceExceptionModel,
        entity: RecurringOccurrenceException,
    ) -> None:
        model.exception_type = entity.exception_type.value
        model.replacement_expected_on = entity.replacement_expected_on
        model.replacement_amount = entity.replacement_amount
        model.replacement_certainty = (
            entity.replacement_certainty.value if entity.replacement_certainty else None
        )
        model.reason = entity.reason
        model.is_active = entity.is_active
        model.version = entity.version
        model.updated_at = entity.updated_at
        model.deactivated_at = entity.deactivated_at
