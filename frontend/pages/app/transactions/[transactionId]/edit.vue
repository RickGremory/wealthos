<script setup lang="ts">
import type { TransactionDetailView } from '~/types/transactions'
import { toUserMessage } from '~/lib/api/errors'
import { buildOccurredAtIso, todayDateInputValue } from '~/utils/transaction-payload'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const { canWrite } = useOrganizationPermissions()
const toast = useToast()
const { getDetail, updateMetadata, loadEnrichment, categories } = useTransactions()

const transactionId = computed(() => String(route.params.transactionId || ''))
const loading = ref(true)
const saving = ref(false)
const error = ref<string | null>(null)
const detail = ref<TransactionDetailView | null>(null)

const description = ref('')
const notes = ref('')
const occurredDate = ref(todayDateInputValue())
const categoryId = ref('')

async function load() {
  loading.value = true
  error.value = null
  try {
    await loadEnrichment(useOrganizationStore().currentOrganizationId!)
    detail.value = await getDetail(transactionId.value)
    if (!detail.value) {
      error.value = 'No se encontró la transacción.'
      return
    }
    description.value = detail.value.description
    notes.value = detail.value.notes || ''
    occurredDate.value = detail.value.occurredAt.slice(0, 10)
    categoryId.value = detail.value.categoryId || ''
  } catch (e) {
    error.value = toUserMessage(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => { void load() })

const canEditCategory = computed(() => {
  const t = detail.value?.type
  return t === 'income' || t === 'expense' || t === 'adjustment'
})

const categoryType = computed(() =>
  detail.value?.type === 'income' ? 'income' : 'expense',
)

async function save() {
  if (!canWrite.value) return
  if (description.value.trim().length < 2) {
    toast.error('La descripción debe tener al menos 2 caracteres.')
    return
  }
  saving.value = true
  try {
    await updateMetadata(transactionId.value, {
      description: description.value.trim(),
      notes: notes.value.trim() || null,
      occurredAt: buildOccurredAtIso({ date: occurredDate.value }),
      categoryId: canEditCategory.value ? (categoryId.value || null) : undefined,
    })
    toast.success('Cambios guardados.')
    void navigateTo(`/app/transactions/${transactionId.value}`)
  } catch (e) {
    toast.error(toUserMessage(e))
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="tx-edit" data-testid="transaction-edit-page">
    <AppPageHeader
      title="Editar metadatos"
      description="Puedes corregir descripción, notas, fecha y categoría. El monto y las cuentas no se editan: anula y vuelve a registrar si necesitas cambiarlos."
    />

    <UiAlert v-if="!canWrite" tone="warning" title="Solo lectura">
      Tu rol no permite editar transacciones.
    </UiAlert>

    <UiSkeleton v-else-if="loading" style="height: 12rem" />

    <UiAlert v-else-if="error" tone="danger" title="Error">
      {{ error }}
    </UiAlert>

    <UiCard v-else class="stack">
      <UiInput
        v-model="description"
        label="Descripción"
        required
      />
      <TransactionDateField v-model="occurredDate" />
      <TransactionCategorySelector
        v-if="canEditCategory && detail?.type !== 'adjustment'"
        v-model="categoryId"
        :categories="categories"
        :category-type="categoryType"
        :allow-quick-create="false"
      />
      <UiInput
        v-model="notes"
        label="Notas"
      />

      <div class="cluster-sm" style="justify-content: flex-end">
        <UiButton
          type="button"
          variant="ghost"
          :disabled="saving"
          @click="navigateTo(`/app/transactions/${transactionId}`)"
        >
          Cancelar
        </UiButton>
        <UiButton
          type="button"
          variant="primary"
          :loading="saving"
          data-testid="save-transaction-metadata"
          @click="save"
        >
          Guardar
        </UiButton>
      </div>
    </UiCard>
  </div>
</template>

<style scoped>
.tx-edit {
  max-width: 32rem;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
</style>
