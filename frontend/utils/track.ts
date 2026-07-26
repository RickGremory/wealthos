/**
 * Minimal product analytics helper.
 * Never send balances, names, creditors, notes, or payment amounts.
 * No-op unless the user opted into analytics cookies.
 */

export type TrackProps = Record<string, string | number | boolean | null | undefined>

const SAFE_KEYS = new Set([
  'commitment_type',
  'strategy',
  'currency_count',
  'source_screen',
  'success',
  'error_code',
  'event_type',
  'display_status',
])

function sanitize(props?: TrackProps): Record<string, string | number | boolean> {
  const out: Record<string, string | number | boolean> = {}
  if (!props) return out
  for (const [key, value] of Object.entries(props)) {
    if (!SAFE_KEYS.has(key) || value == null) continue
    out[key] = value
  }
  return out
}

export function track(event: string, props?: TrackProps): void {
  if (!import.meta.client) return
  try {
    const prefs = useCookiePreferencesStore()
    if (!prefs.analytics) return
    const payload = {
      event,
      props: sanitize(props),
      ts: new Date().toISOString(),
    }
    // Foundation only: console in dev; replace with vendor later.
    if (import.meta.dev) {
      // eslint-disable-next-line no-console
      console.info('[analytics]', payload)
    }
  }
  catch {
    // Never break UX for analytics.
  }
}
