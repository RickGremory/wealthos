import { describe, expect, it } from 'vitest'
import { formatDate, parseCalendarDate, todayLocalIsoDate } from '~/composables/use-date'

describe('todayLocalIsoDate', () => {
  it('uses local calendar components, not UTC ISO date', () => {
    const localEvening = new Date(2026, 6, 25, 22, 0, 0)
    expect(todayLocalIsoDate(localEvening)).toBe('2026-07-25')
  })
})

describe('parseCalendarDate / formatDate', () => {
  it('formats YYYY-MM-DD without UTC day shift', () => {
    const date = parseCalendarDate('2026-07-25')
    expect(date.getFullYear()).toBe(2026)
    expect(date.getMonth()).toBe(6)
    expect(date.getDate()).toBe(25)
    expect(formatDate('2026-07-25', 'es-MX')).toMatch(/25/)
  })
})
