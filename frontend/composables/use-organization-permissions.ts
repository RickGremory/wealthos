import type { OrganizationSummary } from '~/types/domain'

export function useOrganizationPermissions() {
  const organization = useOrganizationStore()

  const role = computed(() => organization.currentOrganization?.role ?? null)

  const canView = computed(() => Boolean(role.value))
  const canWrite = computed(() =>
    role.value === 'owner' || role.value === 'admin' || role.value === 'member',
  )
  const canArchive = computed(() =>
    role.value === 'owner' || role.value === 'admin',
  )
  const isViewer = computed(() => role.value === 'viewer')

  function canWriteIn(membership: OrganizationSummary | null | undefined) {
    const r = membership?.role
    return r === 'owner' || r === 'admin' || r === 'member'
  }

  return {
    role,
    canView,
    canWrite,
    canArchive,
    isViewer,
    canWriteIn,
  }
}
