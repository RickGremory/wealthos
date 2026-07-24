import { describe, expect, it } from 'vitest'
import {
  getGoalStrategyDescription,
  getGoalStrategyLabel,
  GOAL_STRATEGY_OPTIONS,
} from '../../utils/goal-strategies'

describe('goal-strategies', () => {
  it('exposes three strategies', () => {
    expect(GOAL_STRATEGY_OPTIONS.map(o => o.value)).toEqual([
      'manual',
      'linked_accounts',
      'net_worth_percentage',
    ])
  })

  it('labels net_worth_percentage as Patrimonio neto', () => {
    expect(getGoalStrategyLabel('net_worth_percentage')).toBe('Patrimonio neto')
  })

  it('provides descriptions for each strategy', () => {
    for (const option of GOAL_STRATEGY_OPTIONS) {
      expect(getGoalStrategyDescription(option.value).length).toBeGreaterThan(10)
    }
  })
})
