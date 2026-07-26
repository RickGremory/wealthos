export function formatDate(
  value: string | Date | null | undefined,
  locale = 'es-MX',
  options?: Intl.DateTimeFormatOptions,
): string {
  if (!value) return '—'
  const date = parseCalendarDate(value)
  if (Number.isNaN(date.getTime())) return String(value)

  return new Intl.DateTimeFormat(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  }).format(date)
}

export function formatDateTime(
  value: string | Date | null | undefined,
  locale = 'es-MX',
): string {
  return formatDate(value, locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Local calendar date as YYYY-MM-DD.
 * Prefer this over `toISOString().slice(0, 10)` (UTC), which shifts the day
 * for users west of UTC (e.g. MX) in the evening.
 */
export function todayLocalIsoDate(now = new Date()): string {
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/** Parse Date or YYYY-MM-DD as a local calendar day (no UTC shift). */
export function parseCalendarDate(value: string | Date): Date {
  if (value instanceof Date) return value
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value.trim())
  if (match) {
    return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
  }
  return new Date(value)
}

export function formatRelativeDay(
  value: string | Date | null | undefined,
  locale = 'es-MX',
): string {
  if (!value) return '—'
  const date = parseCalendarDate(value)
  if (Number.isNaN(date.getTime())) return String(value)

  const now = new Date()
  const startToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const startTarget = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const diffDays = Math.round(
    (startTarget.getTime() - startToday.getTime()) / (24 * 60 * 60 * 1000),
  )

  try {
    return new Intl.RelativeTimeFormat(locale, { numeric: 'auto' }).format(
      diffDays,
      'day',
    )
  } catch {
    return formatDate(date, locale)
  }
}

export function useDate() {
  const preferences = usePreferencesStore()

  return {
    formatDate: (value: string | Date | null | undefined, options?: Intl.DateTimeFormatOptions) =>
      formatDate(value, preferences.locale, options),
    formatDateTime: (value: string | Date | null | undefined) =>
      formatDateTime(value, preferences.locale),
    formatRelativeDay: (value: string | Date | null | undefined) =>
      formatRelativeDay(value, preferences.locale),
    todayLocalIsoDate,
  }
}
