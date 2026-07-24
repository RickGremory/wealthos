/**
 * Convert an organization name into a URL-safe slug matching
 * `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
 */
export function slugify(value: string): string {
  const normalized = value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-{2,}/g, '-')

  return normalized || 'org'
}
