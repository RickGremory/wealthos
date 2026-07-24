<script setup lang="ts">
import { createAccountsRepository } from '~/repositories/accounts.repository'
import { createCategoriesRepository } from '~/repositories/categories.repository'
import type { AccountSummary } from '~/types/domain'
import type { CategoryTreeNodeView } from '~/types/categories'
import type { TransactionDetailView, TransactionType } from '~/types/transactions'
import { toUserMessage } from '~/lib/api/errors'

const composer = useTransactionComposerStore()
const { canWrite, canArchive } = useOrganizationPermissions()
const organization = useOrganizationStore()
const { $api } = useNuxtApp()
const cache = useFinanceCache()
const toast = useToast()

const accounts = ref<AccountSummary[]>([])
const categories = ref<CategoryTreeNodeView[]>([])
const enrichmentLoading = ref(false)

const {
  form,
  submitting,
  error,
  fieldErrors,
  currencyMismatch,
  reset,
  setType,
  applyDuplicateDraft,
  submit,
} = useTransactionForm({
  accounts,
  categoryNameResolver: (id) => {
    const find = (nodes: CategoryTreeNodeView[]): string | null => {
      for (const n of nodes) {
        if (n.id === id) return n.name
        const child = find(n.children || [])
        if (child) return child
      }
      return null
    }
    return find(categories.value)
  },
})

const { voidTransaction } = useTransactions()

const voidOpen = ref(false)
const voiding = ref(false)
const successTx = ref<TransactionDetailView | null>(null)

async function loadEnrichment() {
  const orgId = organization.currentOrganizationId
  if (!orgId) return
  enrichmentLoading.value = true
  try {
    const [accountList, categoryTree] = await Promise.all([
      createAccountsRepository($api).list(orgId, { includeArchived: false }),
      createCategoriesRepository($api).list(orgId, { tree: true }),
    ])
    accounts.value = accountList
    categories.value = categoryTree
  } catch (e) {
    error.value = toUserMessage(e)
  } finally {
    enrichmentLoading.value = false
  }
}

watch(
  () => composer.open,
  async (isOpen) => {
    if (!isOpen) {
      successTx.value = null
      return
    }
    await loadEnrichment()
    if (composer.mode === 'duplicate') {
      applyDuplicateDraft(composer.duplicateDraft)
    } else {
      reset(composer.initialType)
    }
  },
)

watch(
  () => cache.categoriesVersion.value,
  () => {
    if (composer.open) void loadEnrichment()
  },
)

function onTypeChange(type: TransactionType) {
  setType(type)
}

function close() {
  composer.close()
  successTx.value = null
}

async function onSubmit() {
  const result = await submit()
  if (result) {
    successTx.value = result
  }
}

function onView() {
  const id = successTx.value?.id
  close()
  if (id) void navigateTo(`/app/transactions/${id}`)
}

function onAnother() {
  successTx.value = null
  reset(form.value.type)
}

function onUndoRequest() {
  if (!canArchive.value) {
    toast.error('Solo administradores pueden anular transacciones.')
    return
  }
  voidOpen.value = true
}

async function onVoidConfirm(reason: string) {
  const id = successTx.value?.id
  if (!id) return
  voiding.value = true
  try {
    await voidTransaction(id, reason)
    toast.success('Transacción anulada.')
    voidOpen.value = false
    close()
  } catch (e) {
    toast.error(toUserMessage(e))
  } finally {
    voiding.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="composer.open"
      class="tx-drawer"
      role="dialog"
      aria-modal="true"
      data-testid="quick-transaction-drawer"
      @click.self="close"
    >
      <div class="tx-drawer__panel">
        <header class="tx-drawer__header">
          <div>
            <p class="tx-drawer__eyebrow">
              {{ composer.mode === 'duplicate' ? 'Duplicar' : 'Nueva' }} transacción
            </p>
            <h2 class="tx-drawer__title">Registrar movimiento</h2>
          </div>
          <UiButton variant="ghost" size="sm" type="button" @click="close">
            Cerrar
          </UiButton>
        </header>

        <div class="tx-drawer__body">
          <UiAlert v-if="!canWrite" tone="warning" title="Solo lectura">
            Tu rol no permite registrar transacciones.
          </UiAlert>

          <TransactionSuccessState
            v-else-if="successTx"
            :transaction="successTx"
            @view="onView"
            @another="onAnother"
            @undo="onUndoRequest"
          />

          <template v-else>
            <UiAlert v-if="error" tone="danger" title="No se pudo guardar">
              {{ error }}
            </UiAlert>
            <UiSkeleton v-if="enrichmentLoading" style="height: 12rem" />
            <TransactionForm
              v-else
              v-model="form"
              :accounts="accounts"
              :categories="categories"
              :field-errors="fieldErrors"
              :disabled="submitting || !canWrite"
              :currency-mismatch="currencyMismatch"
              @type-change="onTypeChange"
              @category-created="loadEnrichment"
            />
          </template>
        </div>

        <footer v-if="canWrite && !successTx" class="tx-drawer__footer">
          <UiButton type="button" variant="ghost" :disabled="submitting" @click="close">
            Cancelar
          </UiButton>
          <UiButton
            type="button"
            variant="primary"
            :loading="submitting"
            data-testid="submit-transaction-button"
            @click="onSubmit"
          >
            Guardar
          </UiButton>
        </footer>
      </div>
    </div>
  </Teleport>

  <VoidTransactionDialog
    v-model:open="voidOpen"
    :loading="voiding"
    @confirm="onVoidConfirm"
  />
</template>

<style scoped>
.tx-drawer {
  position: fixed;
  inset: 0;
  z-index: 90;
  background: rgba(10, 22, 40, 0.5);
  display: flex;
  justify-content: flex-end;
}

.tx-drawer__panel {
  width: min(100%, 28rem);
  height: 100%;
  background: var(--color-surface);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  animation: slide-in 180ms ease;
}

@keyframes slide-in {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.tx-drawer__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-5);
  border-bottom: 1px solid var(--color-border);
}

.tx-drawer__eyebrow {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-teal-800);
}

.tx-drawer__title {
  margin: 0.15rem 0 0;
  font-size: 1.25rem;
}

.tx-drawer__body {
  flex: 1;
  overflow: auto;
  padding: var(--space-5);
}

.tx-drawer__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-muted);
}

@media (max-width: 640px) {
  .tx-drawer {
    align-items: flex-end;
  }

  .tx-drawer__panel {
    width: 100%;
    height: min(94vh, 100%);
    border-radius: var(--radius-xl) var(--radius-xl) 0 0;
    animation: slide-up 180ms ease;
  }

  @keyframes slide-up {
    from { transform: translateY(100%); }
    to { transform: translateY(0); }
  }
}
</style>
