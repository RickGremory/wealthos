import type { RecurringOccurrenceView } from '~/types/recurring'
import type { TransactionDuplicateDraft, TransactionSourceInput } from '~/types/transactions'

export function buildRecurringConfirmationDraft(
  occurrence: RecurringOccurrenceView,
): TransactionDuplicateDraft {
  const type
    = occurrence.direction === 'inflow'
      ? 'income'
      : occurrence.direction === 'transfer'
        ? 'transfer'
        : 'expense'

  return {
    type,
    amount: occurrence.expectedAmount,
    description: occurrence.name,
    accountId: occurrence.accountId ?? undefined,
    categoryId: occurrence.categoryId ?? undefined,
    sourceAccountId: occurrence.accountId ?? undefined,
    destinationAccountId: occurrence.destinationAccountId ?? undefined,
    occurredDate: occurrence.expectedOn,
  }
}

export function buildRecurringSource(
  occurrence: RecurringOccurrenceView,
): TransactionSourceInput {
  return {
    type: 'recurring_occurrence',
    occurrenceKey: occurrence.occurrenceKey,
    relatedResourceType: 'recurring_rule',
    relatedResourceId: occurrence.recurringRuleId,
  }
}

export function useRecurringConfirmation() {
  const composer = useTransactionComposerStore()

  function openConfirm(occurrence: RecurringOccurrenceView) {
    composer.openWithDraft(buildRecurringConfirmationDraft(occurrence), {
      label: 'Confirmar recurrente',
      source: buildRecurringSource(occurrence),
    })
  }

  return { openConfirm }
}
