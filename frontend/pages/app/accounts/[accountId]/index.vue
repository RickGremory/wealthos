<script setup lang="ts">
import { createAccountsRepository } from '~/repositories/accounts.repository'
import { toListItem } from '~/composables/use-accounts'
import type { AccountListItemView } from '~/types/accounts'
import { toUserMessage } from '~/lib/api/errors'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const accountId = computed(() => String(route.params.accountId))
const organization = useOrganizationStore()
const { canWrite, canArchive } = useOrganizationPermissions()
const { $api } = useNuxtApp()
const cache = useFinanceCache()
const toast = useToast()

const account = ref<AccountListItemView | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const archiveOpen = ref(false)
const archiveLoading = ref(false)

async function load() {
  const orgId = organization.currentOrganizationId
  if (!orgId) {
    error.value = 'Selecciona una organización.'
    loading.value = false
    return
  }

  loading.value = true
  error.value = null
  try {
    const repo = createAccountsRepository($api)
    const raw = await repo.get(orgId, accountId.value)
    account.value = toListItem(raw)
  } catch (e) {
    error.value = toUserMessage(e)
    account.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})

watch(accountId, () => {
  void load()
})

async function confirmArchive() {
  if (!account.value) return
  const orgId = organization.currentOrganizationId
  if (!orgId) return

  archiveLoading.value = true
  try {
    const repo = createAccountsRepository($api)
    await repo.archive(orgId, account.value.id)
    cache.invalidateAccounts()
    toast.success('Cuenta archivada')
    archiveOpen.value = false
    await navigateTo('/app/accounts')
  } catch (e) {
    toast.error('No se pudo archivar', toUserMessage(e))
  } finally {
    archiveLoading.value = false
  }
}
</script>

<template>
  <div data-testid="account-detail-page">
    <div v-if="loading" class="stack">
      <UiSkeleton height="6rem" />
      <UiSkeleton height="10rem" />
    </div>

    <UiAlert v-else-if="error" tone="danger" title="No se pudo cargar la cuenta">
      <p>{{ error }}</p>
      <div class="cluster" style="margin-top: 0.75rem">
        <UiButton type="button" variant="secondary" @click="navigateTo('/app/accounts')">
          Volver a cuentas
        </UiButton>
      </div>
    </UiAlert>

    <template v-else-if="account">
      <AccountDetailHeader
        :account="account"
        :can-write="canWrite"
        :can-archive="canArchive"
        @edit="navigateTo(`/app/accounts/${account.id}/edit`)"
        @archive="archiveOpen = true"
      />

      <div class="detail-grid">
        <UiCard title="Resumen">
          <dl class="info-list">
            <div>
              <dt>{{ account.balanceLabel }}</dt>
              <dd>
                <AccountBalanceValue
                  :amount="account.balance"
                  :currency="account.currency"
                  :prefix="account.balancePrefix"
                  :presentation="account.balancePresentation"
                />
              </dd>
            </div>
            <div>
              <dt>Moneda</dt>
              <dd>{{ account.currency }}</dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd>{{ account.isArchived ? 'Archivada' : 'Activa' }}</dd>
            </div>
          </dl>
        </UiCard>

        <UiCard title="Actividad">
          <UiEmptyState
            title="Todavía no hay movimientos registrados"
            description="Cuando registres ingresos, gastos o transferencias, aparecerán aquí."
          />
        </UiCard>

        <UiCard title="Información">
          <dl class="info-list">
            <div>
              <dt>Tipo</dt>
              <dd>{{ account.displayType }}</dd>
            </div>
            <div>
              <dt>Institución</dt>
              <dd>{{ account.institution || '—' }}</dd>
            </div>
            <div>
              <dt>Últimos 4 dígitos</dt>
              <dd>{{ account.lastFour || '—' }}</dd>
            </div>
          </dl>
        </UiCard>
      </div>

      <ArchiveAccountDialog
        v-model:open="archiveOpen"
        :account="account"
        :loading="archiveLoading"
        @confirm="confirmArchive"
      />
    </template>
  </div>
</template>

<style scoped>
.detail-grid {
  display: grid;
  gap: var(--space-4);
}

@media (min-width: 900px) {
  .detail-grid {
    grid-template-columns: 1fr 1.2fr;
  }
}

.info-list {
  margin: 0;
  display: grid;
  gap: var(--space-3);
}

.info-list dt {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.info-list dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
}
</style>
