import { describe, expect, it } from 'vitest'
import { deriveGoalDisplayStatus } from '../../utils/goal-status'

describe('goal-status', () => {
  it('marks archived as paused', () => {
    const meta = deriveGoalDisplayStatus({
      status: 'archived',
      targetDate: null,
      estimatedCompletionDate: null,
      completionPercentage: '40',
    })
    expect(meta.status).toBe('paused')
    expect(meta.tone).toBe('neutral')
  })

  it('marks completed', () => {
    const meta = deriveGoalDisplayStatus({
      status: 'completed',
      targetDate: null,
      estimatedCompletionDate: null,
      completionPercentage: '100',
    })
    expect(meta.status).toBe('completed')
    expect(meta.tone).toBe('success')
  })

  it('marks behind when estimated completion is past target', () => {
    const meta = deriveGoalDisplayStatus({
      status: 'active',
      targetDate: '2026-08-01',
      estimatedCompletionDate: '2026-10-01',
      completionPercentage: '20',
      asOf: '2026-07-01',
    })
    expect(meta.status).toBe('behind')
    expect(meta.label).toBe('Ajusta el ritmo')
    expect(meta.tone).toBe('warning')
  })

  it('marks behind when target date already passed', () => {
    const meta = deriveGoalDisplayStatus({
      status: 'active',
      targetDate: '2026-01-01',
      estimatedCompletionDate: null,
      completionPercentage: '50',
      asOf: '2026-07-01',
    })
    expect(meta.status).toBe('behind')
  })

  it('never uses danger tone', () => {
    const cases = [
      deriveGoalDisplayStatus({
        status: 'active',
        targetDate: '2026-01-01',
        estimatedCompletionDate: null,
        completionPercentage: '10',
        asOf: '2026-07-01',
      }),
      deriveGoalDisplayStatus({
        status: 'archived',
        targetDate: null,
        estimatedCompletionDate: null,
        completionPercentage: '0',
      }),
    ]
    for (const meta of cases) {
      expect(meta.tone).not.toBe('danger')
    }
  })

  it('marks on_track when progress is healthy', () => {
    const meta = deriveGoalDisplayStatus({
      status: 'active',
      targetDate: '2026-12-31',
      estimatedCompletionDate: '2026-11-01',
      completionPercentage: '80',
      asOf: '2026-07-01',
    })
    expect(meta.status).toBe('on_track')
    expect(meta.tone).toBe('teal')
  })
})
