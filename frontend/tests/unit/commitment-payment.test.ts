import { describe, expect, it } from 'vitest'
import type { CommitmentListItemView } from '~/types/commitments'
import {
  buildCommitmentPaymentDraft,
  commitmentPaymentQuery,
  suggestedCommitmentPaymentAmount,
} from '~/utils/commitment-payment'

function sample(overrides: Partial<CommitmentListItemView> = {}): CommitmentListItemView {
  return {
    id: 'c1',
    organizationId: 'o1',
    accountId: 'liability-1',
    name: 'Tarjeta Nu',
    debtType: 'credit_card',
    creditor: 'Nu',
    currency: 'MXN',
    priority: 'medium',
    interestRate: '42.00',
    minimumPayment: '2000.00',
    scheduledPayment: null,
    creditLimit: '50000.00',
    originalAmount: null,
    maturityDate: null,
    dueDay: 20,
    statementDay: 5,
    status: 'active',
    displayStatus: 'active',
    behavior: 'revolving',
    notes: null,
    version: 1,
    currentBalance: '10000.00',
    nextDueDate: '2026-08-20',
    daysUntilDue: 26,
    utilizationPercentage: '20.00',
    nextAction: {
      type: 'pay_minimum',
      reasonCode: 'minimum_payment_required',
      amount: '2000.00',
      dueDate: '2026-08-20',
    },
    createdAt: '2026-07-01T00:00:00Z',
    updatedAt: '2026-07-01T00:00:00Z',
    closedAt: null,
    archivedAt: null,
    ...overrides,
  }
}

describe('commitment payment helpers', () => {
  it('prefers scheduled payment over minimum', () => {
    expect(
      suggestedCommitmentPaymentAmount(
        sample({ scheduledPayment: '3500.00', minimumPayment: '2000.00' }),
      ),
    ).toBe('3500.00')
  })

  it('builds transfer draft to liability account', () => {
    const draft = buildCommitmentPaymentDraft(sample())
    expect(draft.type).toBe('transfer')
    expect(draft.destinationAccountId).toBe('liability-1')
    expect(draft.description).toBe('Pago de Tarjeta Nu')
    expect(draft.amount).toBe('2000.00')
  })

  it('builds deep-link query params', () => {
    const q = commitmentPaymentQuery(sample())
    expect(q.type).toBe('transfer')
    expect(q.destination_account_id).toBe('liability-1')
    expect(q.source).toBe('commitment')
    expect(q.commitment_id).toBe('c1')
    expect(q.amount).toBe('2000.00')
  })
})
