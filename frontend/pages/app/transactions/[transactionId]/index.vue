<script setup lang="ts">
import type { TransactionDetailView } from '~/types/transactions'
import { formatDateTime } from '~/composables/use-date'
import { toUserMessage } from '~/lib/api/errors'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const composer = useTransactionComposerStore()
const { canWrite, canArchive } = useOrganizationPermissions()
const toast = useToast()
const { getDetail, voidTransaction } = useTransactions()
const cache = useFinanceCache()

const transactionId = computed(() => String(route.params.transactionId || ''))
const loading = ref(true)
const error = ref<string | null>(null)
const detail = ref<TransactionDetailView | null>(null)
const voidOpen = ref(false)
const voiding = ref(false)

async function load() {
  loading.value = true
  error.value = null
  try {
    detail.value = await getDetail(transactionId.value)
    if (!detail.value) error.value = 'No se encontró la transacción.'
  } catch (e) {
    error.value = toUserMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => { void load() })

watch(transactionId, () => { void load() })
watch(() => cache.transactionsVersion.value, () => { void load() })

function duplicate() {
  if (!detail.value) return
  composer.openDuplicate(detail.value)
}

async function onVoid(reason: string) {
  voiding.value = true
  try {
    detail.value = await voidTransaction(transactionId.value, reason)
    voidOpen.value = false
    toast.success('Transacción anulada.')
  } catch (e) {
    toast.error(toUserMessage(e))
  } finally {
    voiding.value = false
  }
}
</script>

<template>
  <div class="tx-detail" data-testid="transaction-detail-page">
    <div class="tx-detail__nav cluster-sm">
      <NuxtLink to="/app/transactions" class="text-muted">← Movimientos</NuxtLink>
    </div>

    <UiSkeleton v-if="loading" style="height: 10rem" />

    <UiAlert v-else-if="error" tone="danger" title="Error">
      {{ error }}
    </UiAlert>

    <template v-else-if="detail">
      <TransactionDetailHeader :transaction="detail" />

      <div class="tx-detail__actions cluster-sm">
        <UiButton
          v-if="canWrite && detail.status === 'posted'"
          type="button"
          variant="secondary"
          size="sm"
          @click="navigateTo(`/app/transactions/${detail.id}/edit`)"
        >
          Editar metadatos
        </UiButton>
        <UiButton
          v-if="canWrite"
          type="button"
          variant="secondary"
          size="sm"
          @click="duplicate"
        >
          Duplicar
        </UiButton>
        <UiButton
          v-if="canArchive && detail.status === 'posted'"
          type="button"
          variant="danger"
          size="sm"
          data-testid="void-transaction-button"
          @click="voidOpen = true"
        >
          Anular
        </UiButton>
      </div>

      <UiCard title="Detalles">
        <dl class="tx-detail__dl">
          <div>
            <dt>Cuenta</dt>
            <dd>
              <template v-if="detail.type === 'transfer'">
                {{ detail.sourceAccountName }} → {{ detail.destinationAccountName }}
              </template>
              <template v-else>
                {{ detail.accountName || '—' }}
              </template>
            </dd>
          </div>
          <div v-if="detail.categoryName">
            <dt>Categoría</dt>
            <dd>{{ detail.categoryName }}</dd>
          </div>
          <div>
            <dt>Creado</dt>
            <dd>{{ formatDateTime(detail.createdAt) }}</dd>
          </div>
          <div v-if="detail.notes">
            <dt>Notas</dt>
            <dd>{{ detail.notes }}</dd>
          </div>
          <div v-if="detail.voidedAt">
            <dt>Anulado</dt>
            <dd>{{ formatDateTime(detail.voidedAt) }}</dd>
          </div>
        </dl>
      </UiCard>

      <TransactionEntriesCard :entries="detail.entries" />
    </template>

    <VoidTransactionDialog
      v-model:open="voidOpen"
      :loading="voiding"
      @confirm="onVoid"
    />
  </div>
</template>

<style scoped>
.tx-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 40rem;
}

.tx-detail__nav a {
  text-decoration: none;
  font-size: 0.9rem;
}

.tx-detail__dl {
  margin: 0;
  display: grid;
  gap: var(--space-3);
}

.tx-detail__dl dt {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-slate-600);
}

.tx-detail__dl dd {
  margin: 0.15rem 0 0;
}
</style>
