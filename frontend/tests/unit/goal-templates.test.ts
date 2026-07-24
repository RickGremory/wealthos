import { describe, expect, it } from 'vitest'
import { GOAL_TEMPLATES, getGoalTemplate } from '../../utils/goal-templates'

describe('goal-templates', () => {
  it('includes the expected starter templates', () => {
    const ids = GOAL_TEMPLATES.map(t => t.id)
    expect(ids).toEqual([
      'emergency_fund',
      'house',
      'vacation',
      'car',
      'laptop',
      'taxes',
      'retirement',
    ])
  })

  it('returns template by id with suggested amount and strategy hint', () => {
    const emergency = getGoalTemplate('emergency_fund')
    expect(emergency?.name).toBe('Fondo de emergencia')
    expect(emergency?.suggestedTargetAmount).toBe('50000.00')
    expect(emergency?.strategyHint).toBe('linked_accounts')
    expect(emergency?.emoji).toBeTruthy()
  })

  it('maps retirement to patrimonio neto strategy', () => {
    expect(getGoalTemplate('retirement')?.strategyHint).toBe('net_worth_percentage')
  })
})
