"""Recurring aggregate root (rule + versions + pauses + exceptions)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from uuid import UUID

from wealthos.modules.recurring.domain.entities.occurrence_exception import (
    RecurringOccurrenceException,
)
from wealthos.modules.recurring.domain.entities.recurring_rule import RecurringRule
from wealthos.modules.recurring.domain.entities.recurring_rule_pause import (
    RecurringRulePause,
)
from wealthos.modules.recurring.domain.entities.recurring_rule_version import (
    RecurringRuleVersion,
)
from wealthos.modules.recurring.domain.enums.rule import RecurringRuleStatus
from wealthos.modules.recurring.domain.exceptions import (
    DuplicateOccurrenceException,
    PauseAlreadyOpen,
    PauseNotOpen,
    PausePeriodOverlap,
    RecurringRuleArchived,
    RecurringVersionOverlap,
)
from wealthos.modules.recurring.domain.value_objects.effective_period import EffectivePeriod


@dataclass
class RecurringAggregate:
    rule: RecurringRule
    versions: list[RecurringRuleVersion] = field(default_factory=list)
    pauses: list[RecurringRulePause] = field(default_factory=list)
    exceptions: list[RecurringOccurrenceException] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._assert_versions_do_not_overlap()

    @property
    def id(self) -> UUID:
        return self.rule.id

    @property
    def organization_id(self) -> UUID:
        return self.rule.organization_id

    @property
    def version(self) -> int:
        return self.rule.version

    def versions_tuple(self) -> tuple[RecurringRuleVersion, ...]:
        return tuple(sorted(self.versions, key=lambda item: item.effective_from))

    def active_exceptions(self) -> tuple[RecurringOccurrenceException, ...]:
        return tuple(item for item in self.exceptions if item.is_active)

    def current_version(self, on_date: date) -> RecurringRuleVersion | None:
        for version in reversed(self.versions_tuple()):
            if version.effective_period.contains(on_date):
                return version
        return None

    def versions_affecting(
        self,
        period_start: date,
        period_end: date,
    ) -> tuple[RecurringRuleVersion, ...]:
        window = EffectivePeriod(period_start, period_end)
        return tuple(
            version
            for version in self.versions_tuple()
            if version.effective_period.overlaps(window)
        )

    def open_pause(self) -> RecurringRulePause | None:
        for pause in self.pauses:
            if pause.is_open:
                return pause
        return None

    def add_version(self, version: RecurringRuleVersion) -> None:
        self._ensure_writable()
        if version.recurring_rule_id != self.rule.id:
            raise RecurringVersionOverlap("Version does not belong to this rule.")
        probe = EffectivePeriod(version.effective_from, version.effective_until)
        for existing in self.versions:
            if existing.effective_period.overlaps(probe):
                raise RecurringVersionOverlap(
                    "Effective periods for a rule must not overlap."
                )
        self.versions.append(version)
        self.rule.touch()

    def close_current_and_add_version(
        self,
        *,
        effective_from: date,
        new_version: RecurringRuleVersion,
    ) -> None:
        """Close the open version the day before ``effective_from``, then add."""
        self._ensure_writable()
        if new_version.effective_from != effective_from:
            raise RecurringVersionOverlap("new_version.effective_from mismatch.")
        day_before = effective_from - timedelta(days=1)
        open_versions = [
            version
            for version in self.versions
            if version.effective_until is None
            or version.effective_until >= effective_from
        ]
        for version in open_versions:
            if version.effective_from >= effective_from:
                raise RecurringVersionOverlap(
                    "Cannot insert a version that starts before an existing later version."
                )
            version.close_on(day_before)
        self.add_version(new_version)

    def add_pause(self, pause: RecurringRulePause) -> None:
        self._ensure_writable()
        if pause.recurring_rule_id != self.rule.id:
            raise PausePeriodOverlap("Pause does not belong to this rule.")
        if pause.is_open and self.open_pause() is not None:
            raise PauseAlreadyOpen("A rule may have only one open pause.")
        for existing in self.pauses:
            if self._pauses_overlap(existing, pause):
                raise PausePeriodOverlap("Pause period overlaps an existing pause.")
        self.pauses.append(pause)
        self.rule.mark_paused()

    def resume(self, resume_on: date) -> RecurringRulePause:
        self._ensure_writable()
        open_pause = self.open_pause()
        if open_pause is None:
            raise PauseNotOpen("There is no open pause to resume.")
        open_pause.close_before(resume_on)
        self.rule.mark_active()
        return open_pause

    def add_exception(self, exception: RecurringOccurrenceException) -> None:
        self._ensure_writable()
        if exception.recurring_rule_id != self.rule.id:
            raise DuplicateOccurrenceException("Exception does not belong to this rule.")
        for existing in self.active_exceptions():
            if existing.original_occurrence_key == exception.original_occurrence_key:
                raise DuplicateOccurrenceException(
                    "An active exception already exists for this occurrence key."
                )
        self.exceptions.append(exception)
        self.rule.touch()

    def archive(self) -> None:
        if self.rule.status is RecurringRuleStatus.ARCHIVED:
            return
        self.rule.mark_archived()

    def end(self, ends_on: date, *, today: date) -> None:
        """Set series end on the current/open version."""
        self._ensure_writable()
        current = self.current_version(ends_on) or (
            self.versions_tuple()[-1] if self.versions else None
        )
        if current is None:
            raise RecurringVersionOverlap("Rule has no versions to end.")
        if current.ends_on is None or ends_on < current.ends_on:
            current.ends_on = ends_on
        if ends_on <= today:
            self.rule.status = RecurringRuleStatus.ENDED
        self.rule.touch()

    def _ensure_writable(self) -> None:
        if self.rule.status is RecurringRuleStatus.ARCHIVED:
            raise RecurringRuleArchived("Archived rules cannot be modified.")

    def _assert_versions_do_not_overlap(self) -> None:
        ordered = self.versions_tuple()
        for left, right in zip(ordered, ordered[1:], strict=False):
            if left.effective_period.overlaps(right.effective_period):
                raise RecurringVersionOverlap(
                    "Effective periods for a rule must not overlap."
                )

    @staticmethod
    def _pauses_overlap(left: RecurringRulePause, right: RecurringRulePause) -> bool:
        left_end = left.ends_on or date.max
        right_end = right.ends_on or date.max
        return left.starts_on <= right_end and right.starts_on <= left_end
