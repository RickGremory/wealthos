<script setup lang="ts">
import type { AccountListItemView } from '~/types/accounts'
import type { BackendAccountType } from '~/utils/account-type-mapper'
import { createAccountsRepository } from '~/repositories/accounts.repository'
import { toUserMessage } from '~/lib/api/errors'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { canWrite, canArchive } = useOrganizationPermissions()
const {
  listLoading,
  summaryLoading,
  listError,
  summaryError,
  filterChip,
  search,
  currencyFilter,
  currencySummaries,
  availableCurrencies,
  groups,
  hasActiveAccounts,
  hasAnyAccounts,
  load,
} = useAccounts()
const cache = useFinanceCache()
const toast = useToast()
const organization = useOrganizationStore()
const { $api } = useNuxtApp()

const archiveTarget = ref<AccountListItemView | null>(null)
const archiveOpen = ref(false)
const archiveLoading = ref(false)

const filterOptions: Array<{ value: typeof filterChip.value, label: string }> = [
  { value: 'all', label: 'Todas' },
  { value: 'cash', label: 'Efectivo' },
  { value: 'savings', label: 'Ahorro' },
  { value: 'investments', label: 'Inversiones' },
  { value: 'debts', label: 'Deudas' },
  { value: 'archived', label: 'Archivadas' },
]

const quickTypes: Array<{ type: BackendAccountType, label: string }> = [
  { type: 'checking', label: 'Cuenta bancaria' },
  { type: 'cash', label: 'Efectivo' },
  { type: 'credit_card', label: 'Tarjeta' },
  { type: 'savings', label: 'Ahorro' },
]

onMounted(() => {
  void load()
})

function goNew(type?: BackendAccountType) {
  const query = type ? `?type=${type}` : ''
  return navigateTo(`/app/accounts/new${query}`)
}

function goDetail(id: string) {
  return navigateTo(`/app/accounts/${id}`)
}

function goEdit(id: string) {
  return navigateTo(`/app/accounts/${id}/edit`)
}

function openArchive(id: string) {
  const group = groups.value.flatMap(g => g.accounts).find(a => a.id === id)
  if (!group) return
  archiveTarget.value = group
  archiveOpen.value = true
}

async function confirmArchive() {
  if (!archiveTarget.value) return
  const orgId = organization.currentOrganizationId
  if (!orgId) return

  archiveLoading.value = true
  try {
    const repo = createAccountsRepository($api)
    await repo.archive(orgId, archiveTarget.value.id)
    cache.invalidateAccounts()
    toast.success('Cuenta archivada', archiveTarget.value.name)
    archiveOpen.value = false
    archiveTarget.value = null
    await load()
  } catch (e) {
    toast.error('No se pudo archivar', toUserMessage(e))
  } finally {
    archiveLoading.value = false
  }
}
</script>

<template>
  <div data-testid="accounts-page">
    <AppPageHeader
      title="Cuentas"
      description="Consulta tus saldos y organiza dónde vive tu dinero."
    >
      <template v-if="canWrite" #actions>
        <UiButton type="button" @click="goNew()">
          Nueva cuenta
        </UiButton>
      </template>
    </AppPageHeader>

    <section class="accounts-summary stack" aria-label="Resumen por moneda">
      <div v-if="summaryLoading" class="summary-grid">
        <UiSkeleton height="8rem" />
        <UiSkeleton height="8rem" />
      </div>
      <UiAlert v-else-if="summaryError" tone="danger" title="No se pudo cargar el resumen">
        {{ summaryError }}
      </UiAlert>
      <div v-else-if="currencySummaries.length" class="summary-grid">
        <AccountCurrencySummary
          v-for="summary in currencySummaries"
          :key="summary.currency"
          :summary="summary"
        />
      </div>
    </section>

    <section class="accounts-filters cluster" aria-label="Filtros">
      <button
        v-for="option in filterOptions"
        :key="option.value"
        type="button"
        class="chip"
        :data-active="filterChip === option.value"
        @click="filterChip = option.value"
      >
        {{ option.label }}
      </button>
      <button
        v-for="currency in availableCurrencies"
        :key="currency"
        type="button"
        class="chip chip--currency"
        :data-active="currencyFilter === currency"
        @click="currencyFilter = currencyFilter === currency ? null : currency"
      >
        {{ currency }}
      </button>
      <UiInput
        v-model="search"
        class="accounts-filters__search"
        placeholder="Buscar cuenta…"
        inputmode="search"
      />
    </section>

    <section class="accounts-list stack" aria-label="Listado de cuentas">
      <div v-if="listLoading" class="stack">
        <UiSkeleton height="5rem" />
        <UiSkeleton height="5rem" />
        <UiSkeleton height="5rem" />
      </div>
      <UiAlert v-else-if="listError" tone="danger" title="No se pudieron cargar las cuentas">
        {{ listError }}
      </UiAlert>
      <UiCard v-else-if="!hasAnyAccounts || (!hasActiveAccounts && filterChip === 'all')">
        <UiEmptyState
          title="Sin cuentas"
          description="Crea tu primera cuenta bancaria, efectivo o tarjeta para ver tu panorama."
        >
          <template v-if="canWrite" #actions>
            <div class="quick-types">
              <UiButton
                v-for="item in quickTypes"
                :key="item.type"
                type="button"
                variant="secondary"
                @click="goNew(item.type)"
              >
                {{ item.label }}
              </UiButton>
              <UiButton type="button" @click="goNew()">
                Nueva cuenta
              </UiButton>
            </div>
          </template>
        </UiEmptyState>
      </UiCard>
      <UiEmptyState
        v-else-if="!groups.length"
        title="Sin resultados"
        description="Prueba otro filtro o limpia la búsqueda."
      />
      <div v-else class="stack">
        <AccountGroup
          v-for="group in groups"
          :key="group.key"
          :group="group"
          :can-write="canWrite"
          :can-archive="canArchive"
          @view="goDetail"
          @edit="goEdit"
          @archive="openArchive"
        />
      </div>
    </section>

    <ArchiveAccountDialog
      v-model:open="archiveOpen"
      :account="archiveTarget"
      :loading="archiveLoading"
      @confirm="confirmArchive"
    />
  </div>
</template>

<style scoped>
.accounts-summary {
  margin-bottom: var(--space-6);
}

.summary-grid {
  display: grid;
  gap: var(--space-4);
}

@media (min-width: 900px) {
  .summary-grid {
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  }
}

.accounts-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  align-items: center;
}

.accounts-filters__search {
  flex: 1 1 12rem;
  min-width: 10rem;
}

.chip {
  border: 1px solid var(--color-border-strong);
  background: var(--color-surface);
  color: var(--color-slate-700);
  border-radius: var(--radius-md);
  padding: 0.4rem 0.75rem;
  font: inherit;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.chip[data-active='true'] {
  background: var(--color-teal-50);
  border-color: var(--color-teal-700);
  color: var(--color-teal-900);
}

.quick-types {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
}
</style>
