<script setup lang="ts">
import type { AccountSummary } from '~/types/domain'
import type { CategoryTreeNodeView } from '~/types/categories'
import type { TransactionFormModel, TransactionType } from '~/types/transactions'
import { presentTransaction } from '~/utils/transaction-presentation'

const form = defineModel<TransactionFormModel>({ required: true })

const props = defineProps<{
  accounts: AccountSummary[]
  categories: CategoryTreeNodeView[]
  fieldErrors?: Record<string, string>
  disabled?: boolean
  currencyMismatch?: boolean
}>()

const emit = defineEmits<{
  typeChange: [type: TransactionType]
  categoryCreated: []
}>()

const selectedAccount = computed(() =>
  props.accounts.find(a => a.id === form.value.accountId) ?? null,
)

const sourceAccount = computed(() =>
  props.accounts.find(a => a.id === form.value.sourceAccountId) ?? null,
)

const destinationAccount = computed(() =>
  props.accounts.find(a => a.id === form.value.destinationAccountId) ?? null,
)

const moneyCurrency = computed(() => {
  if (form.value.type === 'transfer') {
    return sourceAccount.value?.currency || 'MXN'
  }
  return selectedAccount.value?.currency || 'MXN'
})

const impactHint = computed(() => {
  if (form.value.type !== 'expense' || !selectedAccount.value) return null
  return presentTransaction({
    type: 'expense',
    status: 'posted',
    accountType: selectedAccount.value.accountType,
  }).impactHint
})

const categoryType = computed(() =>
  form.value.type === 'income' ? 'income' : 'expense',
)

function onTypeUpdate(type: TransactionType) {
  emit('typeChange', type)
}
</script>

<template>
  <div class="tx-form stack" data-testid="transaction-form">
    <TransactionTypeSelector
      :model-value="form.type"
      @update:model-value="onTypeUpdate"
    />

    <template v-if="form.type === 'adjustment'">
      <TransactionAccountSelector
        v-model="form.accountId"
        :accounts="accounts"
        transaction-type="adjustment"
        label="Cuenta"
        :error="fieldErrors?.accountId"
        :disabled="disabled"
      />
      <MoneyInput
        v-model="form.realBalance"
        label="Saldo real"
        :currency="moneyCurrency"
        :unsigned="false"
        :error="fieldErrors?.realBalance"
        :disabled="disabled"
      />
      <UiInput
        v-model="form.description"
        label="Motivo"
        placeholder="¿Por qué ajustas el saldo?"
        :error="fieldErrors?.description"
        :disabled="disabled"
        required
      />
      <TransactionPreview
        type="adjustment"
        :real-balance="form.realBalance"
        :current-balance="selectedAccount?.currentBalance"
        :currency="moneyCurrency"
        :account-name="selectedAccount?.name"
      />
    </template>

    <template v-else-if="form.type === 'transfer'">
      <MoneyInput
        v-model="form.amount"
        :currency="moneyCurrency"
        :error="fieldErrors?.amount"
        :disabled="disabled"
      />
      <TransferAccountSelector
        v-model:source-id="form.sourceAccountId"
        v-model:destination-id="form.destinationAccountId"
        :accounts="accounts"
        :source-error="fieldErrors?.sourceAccountId"
        :destination-error="fieldErrors?.destinationAccountId"
        :currency-mismatch="currencyMismatch"
        :disabled="disabled"
      />
      <UiInput
        v-model="form.description"
        label="Descripción"
        placeholder="Ej. Traspaso a ahorro"
        :error="fieldErrors?.description"
        :disabled="disabled"
        required
      />
      <TransactionPreview
        type="transfer"
        :amount="form.amount"
        :currency="moneyCurrency"
        :source-name="sourceAccount?.name"
        :destination-name="destinationAccount?.name"
      />
    </template>

    <template v-else>
      <MoneyInput
        v-model="form.amount"
        :currency="moneyCurrency"
        :error="fieldErrors?.amount"
        :disabled="disabled"
      />
      <TransactionAccountSelector
        v-model="form.accountId"
        :accounts="accounts"
        :transaction-type="form.type"
        :error="fieldErrors?.accountId"
        :disabled="disabled"
      />
      <TransactionCategorySelector
        v-model="form.categoryId"
        :categories="categories"
        :category-type="categoryType"
        :error="fieldErrors?.categoryId"
        :disabled="disabled"
        @created="emit('categoryCreated')"
      />
      <UiAlert v-if="impactHint" tone="warning" :title="impactHint" />
      <UiInput
        v-model="form.description"
        label="Descripción"
        placeholder="Opcional — se usa el nombre de la categoría"
        :error="fieldErrors?.description"
        :disabled="disabled"
      />
    </template>

    <TransactionDateField
      v-model="form.occurredDate"
      :error="fieldErrors?.occurredDate"
      :disabled="disabled"
    />

    <UiInput
      v-model="form.notes"
      label="Notas"
      placeholder="Opcional"
      :disabled="disabled"
    />
  </div>
</template>
