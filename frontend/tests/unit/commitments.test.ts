import { describe, expect, it } from 'vitest'
import { mapCommitmentDto } from '~/repositories/commitments.repository'
import { sortCommitments } from '~/utils/commitment-sort'
import { getCommitmentDisplayMeta, isAttentionStatus } from '~/utils/commitment-status'
import type { CommitmentListItemView } from '~/types/commitments'

describe('mapCommitmentDto', () => {
  it('maps snake_case debt payload to commitment view', () => {
    const view = mapCommitmentDto({
      id: 'c1',
      organization_id: 'o1',
      account_id: 'a1',
      name: 'Tarjeta Nu',
      debt_type: 'credit_card',
      creditor: 'Nu',
      currency: 'MXN',
      priority: 'high',
      interest_rate: 42,
      minimum_payment: 1250,
      scheduled_payment: null,
      credit_limit: 50000,
      original_amount: null,
      maturity_date: null,
      due_day: 20,
      statement_day: 5,
      status: 'active',
      display_status: 'overdue',
      behavior: 'revolving',
      notes: null,
      version: 1,
      current_balance: 18450,
      next_due_date: '2026-08-20',
      days_until_due: 26,
      utilization_percentage: 36.9,
      next_action: {
        type: 'pay_overdue',
        reason_code: 'overdue',
        amount: 1250,
        due_date: '2026-08-20',
      },
      created_at: '2026-07-01T00:00:00Z',
      updated_at: '2026-07-01T00:00:00Z',
      closed_at: null,
      archived_at: null,
    })

    expect(view.name).toBe('Tarjeta Nu')
    expect(view.currentBalance).toBe('18450.00')
    expect(view.displayStatus).toBe('overdue')
    expect(view.nextAction?.type).toBe('pay_overdue')
    expect(view.utilizationPercentage).toBe('36.90')
  })
})

describe('commitment status helpers', () => {
  it('flags attention statuses', () => {
    expect(isAttentionStatus('overdue')).toBe(true)
    expect(isAttentionStatus('active')).toBe(false)
    expect(getCommitmentDisplayMeta('due_soon').tone).toBe('warning')
  })
})

describe('sortCommitments', () => {
  it('puts attention items first', () => {
    const base = {
      organizationId: 'o',
      accountId: 'a',
      debtType: 'credit_card' as const,
      creditor: null,
      currency: 'MXN',
      priority: 'medium' as const,
      interestRate: null,
      minimumPayment: null,
      scheduledPayment: null,
      creditLimit: null,
      originalAmount: null,
      maturityDate: null,
      dueDay: null,
      statementDay: null,
      status: 'active' as const,
      behavior: null,
      notes: null,
      version: 1,
      nextDueDate: null,
      daysUntilDue: null,
      utilizationPercentage: null,
      nextAction: null,
      createdAt: '2026-07-01T00:00:00Z',
      updatedAt: '2026-07-01T00:00:00Z',
      closedAt: null,
      archivedAt: null,
    }

    const items: CommitmentListItemView[] = [
      {
        ...base,
        id: 'ok',
        name: 'OK',
        displayStatus: 'active',
        currentBalance: '5000.00',
        daysUntilDue: 20,
      },
      {
        ...base,
        id: 'late',
        name: 'Late',
        displayStatus: 'overdue',
        currentBalance: '1000.00',
        daysUntilDue: 0,
      },
    ]

    expect(sortCommitments(items)[0]?.id).toBe('late')
  })
})
