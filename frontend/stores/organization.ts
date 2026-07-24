import { defineStore } from 'pinia'
import { toUserMessage } from '~/lib/api/errors'
import { createOrganizationsRepository } from '~/repositories/organizations.repository'
import type { CreateOrganizationInput } from '~/repositories/organizations.repository'
import type { OrganizationSummary } from '~/types/domain'

export const useOrganizationStore = defineStore('organization', () => {
  const orgCookie = useCookie<string | null>('wealthos_organization_id', {
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 30,
    watch: true,
  })

  const memberships = ref<OrganizationSummary[]>([])
  const currentOrganizationId = computed(() => orgCookie.value)
  const loading = ref(false)
  const switching = ref(false)
  const hydrated = ref(false)

  const currentOrganization = computed(() =>
    memberships.value.find(m => m.id === orgCookie.value) ?? null,
  )

  function selectOrganization(organizationId: string) {
    switching.value = true
    try {
      orgCookie.value = organizationId
    } finally {
      switching.value = false
    }
  }

  /** @deprecated Prefer selectOrganization */
  function selectOrg(organizationId: string) {
    selectOrganization(organizationId)
  }

  function clear() {
    orgCookie.value = null
    memberships.value = []
    hydrated.value = false
  }

  async function loadMemberships() {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      memberships.value = []
      hydrated.value = true
      return
    }

    loading.value = true
    try {
      const { $api } = useNuxtApp()
      const repo = createOrganizationsRepository($api)
      memberships.value = await repo.listMemberships()

      const stillValid = memberships.value.some(m => m.id === orgCookie.value)
      if (memberships.value.length > 0 && !stillValid) {
        orgCookie.value = null
      }

      if (!orgCookie.value && memberships.value.length === 1) {
        orgCookie.value = memberships.value[0]!.id
      }
    } catch {
      // Keep current org cookie on transient API failures (e.g. SSR without mocks).
      memberships.value = []
    } finally {
      loading.value = false
      hydrated.value = true
    }
  }

  /** Alias used by existing hydrate call sites. */
  async function hydrate() {
    return loadMemberships()
  }

  async function createOrganization(input: CreateOrganizationInput) {
    loading.value = true
    try {
      const { $api } = useNuxtApp()
      const repo = createOrganizationsRepository($api)
      const created = await repo.create(input)
      const summary: OrganizationSummary = {
        ...created,
        role: 'owner',
      }
      const exists = memberships.value.some(m => m.id === summary.id)
      if (!exists) {
        memberships.value = [...memberships.value, summary]
      }
      selectOrganization(summary.id)
      hydrated.value = true
      return summary
    } catch (error) {
      throw new Error(toUserMessage(error), { cause: error })
    } finally {
      loading.value = false
    }
  }

  return {
    memberships,
    currentOrganizationId,
    currentOrganization,
    loading,
    switching,
    hydrated,
    selectOrganization,
    selectOrg,
    clear,
    loadMemberships,
    hydrate,
    createOrganization,
  }
})
