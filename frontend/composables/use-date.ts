export function formatDate(
  value: string | Date | null | undefined,
  locale = 'es-MX',
  options?: Intl.DateTimeFormatOptions,
): string {
  if (!value) return '—'
  const date = value instanceof Date ? value : new Date(value)
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

export function formatRelativeDay(
  value: string | Date | null | undefined,
  locale = 'es-MX',
): string {
  if (!value) return '—'
  const date = value instanceof Date ? value : new Date(value)
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
  }
}
