<script setup lang="ts">
import type { AccountSummary } from '~/types/domain'
import type { CategoryTreeNodeView } from '~/types/categories'
import type { TransactionFormModel, TransactionType } from '~/types/transactions'
import { presentTransaction } from '~/utils/transaction-presentation'
import { deriveEffectiveExchangeRate, formatFxRateLabel } from '~/utils/fx-transfer'

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
  enableFx: []
  disableFx: []
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

const destinationCurrency = computed(
  () => destinationAccount.value?.currency || 'USD',
)

const effectiveRate = computed(() => {
  if (!form.value.fxConversion) return null
  return deriveEffectiveExchangeRate(form.value.amount, form.value.destinationAmount)
})

const rateLabel = computed(() =>
  formatFxRateLabel(
    effectiveRate.value,
    moneyCurrency.value,
    destinationCurrency.value,
  ),
)

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
      <TransferAccountSelector
        v-model:source-id="form.sourceAccountId"
        v-model:destination-id="form.destinationAccountId"
        :accounts="accounts"
        :source-error="fieldErrors?.sourceAccountId"
        :destination-error="fieldErrors?.destinationAccountId"
        :currency-mismatch="currencyMismatch"
        :fx-conversion="form.fxConversion"
        :disabled="disabled"
        @enable-fx="emit('enableFx')"
        @disable-fx="emit('disableFx')"
      />

      <template v-if="form.fxConversion">
        <MoneyInput
          v-model="form.amount"
          label="Monto enviado"
          :currency="moneyCurrency"
          :error="fieldErrors?.amount"
          :disabled="disabled"
        />
        <MoneyInput
          v-model="form.destinationAmount"
          label="Monto recibido"
          :currency="destinationCurrency"
          :error="fieldErrors?.destinationAmount"
          :disabled="disabled"
        />
        <p
          v-if="rateLabel"
          class="tx-form__rate"
          data-testid="fx-effective-rate"
        >
          Tipo de cambio efectivo: <strong>{{ rateLabel }}</strong>
        </p>
        <MoneyInput
          v-model="form.feeAmount"
          label="Comisión (opcional)"
          :currency="moneyCurrency"
          :error="fieldErrors?.feeAmount"
          :disabled="disabled"
        />
        <UiInput
          v-model="form.description"
          label="Descripción"
          placeholder="Ej. Envío a Hapi / compra de USD"
          :error="fieldErrors?.description"
          :disabled="disabled"
          required
        />
        <div class="tx-form__fx-preview" data-testid="fx-preview">
          <p class="tx-form__fx-title">Vista previa</p>
          <p>
            {{ sourceAccount?.name || 'Origen' }}:
            −{{ form.amount || '0.00' }} {{ moneyCurrency }}
          </p>
          <p>
            {{ destinationAccount?.name || 'Destino' }}:
            +{{ form.destinationAmount || '0.00' }} {{ destinationCurrency }}
          </p>
          <p v-if="form.feeAmount.trim()" class="text-muted">
            Comisión: −{{ form.feeAmount }} {{ moneyCurrency }}
          </p>
        </div>
      </template>

      <template v-else>
        <MoneyInput
          v-model="form.amount"
          :currency="moneyCurrency"
          :error="fieldErrors?.amount"
          :disabled="disabled || currencyMismatch"
        />
        <UiInput
          v-model="form.description"
          label="Descripción"
          placeholder="Ej. Traspaso a ahorro"
          :error="fieldErrors?.description"
          :disabled="disabled || currencyMismatch"
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

<style scoped>
.tx-form__rate {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-muted, #667085);
}

.tx-form__fx-preview {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-teal-50);
  border: 1px solid var(--color-teal-100);
}

.tx-form__fx-title {
  margin: 0 0 var(--space-2);
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-teal-900);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tx-form__fx-preview p {
  margin: 0.25rem 0;
}
</style>
