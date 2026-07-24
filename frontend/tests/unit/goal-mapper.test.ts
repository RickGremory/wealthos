import { describe, expect, it } from 'vitest'
import { mapGoalDto } from '../../repositories/goals.repository'
import { sortGoals, selectPrimaryGoalId } from '../../utils/goal-sort'
import type { GoalListItemView } from '../../types/goals'

function makeGoal(overrides: Partial<GoalListItemView> = {}): GoalListItemView {
  return {
    id: 'g1',
    organizationId: 'org',
    name: 'Meta',
    targetAmount: '10000.00',
    currency: 'MXN',
    targetDate: null,
    strategy: 'manual',
    linkedAccountIds: [],
    status: 'active',
    currentAmount: '1000.00',
    remainingAmount: '9000.00',
    completionPercentage: '10',
    estimatedCompletionDate: null,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    completedAt: null,
    archivedAt: null,
    priority: 2,
    displayStatus: 'active',
    ...overrides,
  }
}

describe('goal-mapper', () => {
  it('maps decimal fields to strings', () => {
    const view = mapGoalDto({
      id: '00000000-0000-4000-8000-0000000000g1',
      organization_id: '00000000-0000-4000-8000-000000000001',
      name: 'Vacaciones',
      target_amount: 25000,
      currency: 'MXN',
      target_date: '2026-12-01',
      strategy: 'manual',
      linked_account_ids: [],
      status: 'active',
      current_amount: 5000.5,
      remaining_amount: 19999.5,
      completion_percentage: 20.002,
      estimated_completion_date: null,
      created_at: '2026-07-01T00:00:00Z',
      updated_at: '2026-07-20T00:00:00Z',
      completed_at: null,
      archived_at: null,
    }, 1)

    expect(view.targetAmount).toBe('25000.00')
    expect(view.currentAmount).toBe('5000.50')
    expect(view.remainingAmount).toBe('19999.50')
    expect(view.completionPercentage).toBe('20.002')
    expect(view.priority).toBe(1)
    expect(view.strategy).toBe('manual')
  })

  it('sorts by priority then target date then completion', () => {
    const goals = [
      makeGoal({ id: 'a', priority: 2, targetDate: '2026-09-01', completionPercentage: '90' }),
      makeGoal({ id: 'b', priority: 1, targetDate: null, completionPercentage: '10' }),
      makeGoal({ id: 'c', priority: 2, targetDate: null, completionPercentage: '50' }),
      makeGoal({ id: 'd', priority: 2, targetDate: '2026-08-01', completionPercentage: '20' }),
    ]
    expect(sortGoals(goals).map(g => g.id)).toEqual(['b', 'd', 'a', 'c'])
  })

  it('selects preferred primary when active', () => {
    const goals = [
      makeGoal({ id: 'a', priority: 1, status: 'active' }),
      makeGoal({ id: 'b', priority: 2, status: 'active' }),
    ]
    expect(selectPrimaryGoalId(goals, 'b')).toBe('b')
  })

  it('falls back to priority 1 then nearest date then highest completion', () => {
    expect(
      selectPrimaryGoalId(
        [
          makeGoal({ id: 'low', priority: 3, completionPercentage: '90' }),
          makeGoal({ id: 'high', priority: 1, completionPercentage: '5' }),
        ],
        null,
      ),
    ).toBe('high')

    expect(
      selectPrimaryGoalId(
        [
          makeGoal({ id: 'later', priority: 2, targetDate: '2026-12-01', completionPercentage: '80' }),
          makeGoal({ id: 'soon', priority: 2, targetDate: '2026-08-01', completionPercentage: '10' }),
        ],
        null,
      ),
    ).toBe('soon')

    expect(
      selectPrimaryGoalId(
        [
          makeGoal({ id: 'small', priority: 2, completionPercentage: '10' }),
          makeGoal({ id: 'big', priority: 2, completionPercentage: '70' }),
        ],
        null,
      ),
    ).toBe('big')
  })
})
