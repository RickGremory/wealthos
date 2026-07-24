<script setup lang="ts">
import type { CreateAccountFormModel, UpdateAccountFormModel } from '~/types/accounts'
import type { BackendAccountType } from '~/utils/account-type-mapper'
import { getAccountTypeOption } from '~/utils/account-type-mapper'
import { formatMoney } from '~/composables/use-money'
import { formatDate } from '~/composables/use-date'

const form = defineModel<CreateAccountFormModel>('form', { required: true })
const editForm = defineModel<UpdateAccountFormModel | undefined>('editForm')

const props = withDefaults(
  defineProps<{
    mode: 'create' | 'edit'
    balanceLabel: string
    currencyOptions: Array<{ label: string, value: string }>
    fieldErrors?: Record<string, string>
    submitting?: boolean
    error?: string | null
  }>(),
  {
    fieldErrors: () => ({}),
    submitting: false,
    error: null,
  },
)

const emit = defineEmits<{
  submit: []
  'update:accountType': [type: BackendAccountType]
}>()

const typeModel = computed({
  get: () => form.value.accountType,
  set: (value: BackendAccountType) => emit('update:accountType', value),
})

const summaryLines = computed(() => {
  if (props.mode !== 'create') return null
  const option = getAccountTypeOption(form.value.accountType)
  return {
    name: form.value.name.trim() || 'Sin nombre',
    type: option.label,
    balance: formatMoney(form.value.openingBalance || '0.00', form.value.currency),
    date: formatDate(form.value.openingBalanceDate),
    balanceField: props.balanceLabel,
  }
})

const liabilityHint = computed(() => {
  const option = getAccountTypeOption(form.value.accountType)
  if (option.presentation !== 'liability') return undefined
  return 'Ingresa el monto que debes; WealthOS lo registrará correctamente en el ledger.'
})
</script>

<template>
  <form class="account-form stack" @submit.prevent="emit('submit')">
    <UiAlert v-if="error" tone="danger" title="No se pudo guardar">
      {{ error }}
    </UiAlert>

    <template v-if="mode === 'create'">
      <UiInput
        v-model="form.name"
        label="Nombre"
        required
        :error="fieldErrors.name"
        placeholder="Ej. Cuenta principal"
      />

      <AccountTypeSelector v-model="typeModel" :disabled="submitting" />

      <UiSelect
        v-model="form.currency"
        label="Moneda"
        :options="currencyOptions"
        :disabled="submitting"
        required
      />

      <OpeningBalanceField
        v-model="form.openingBalance"
        :label="balanceLabel"
        :hint="liabilityHint"
        :error="fieldErrors.openingBalance"
        :disabled="submitting"
      />

      <UiInput
        v-model="form.openingBalanceDate"
        label="Fecha del saldo"
        type="date"
        required
        :error="fieldErrors.openingBalanceDate"
        :disabled="submitting"
      />

      <UiInput
        v-model="form.institutionName"
        label="Institución (opcional)"
        placeholder="Banco, caja, broker…"
        :disabled="submitting"
      />

      <UiInput
        v-model="form.lastFour"
        label="Últimos 4 dígitos (opcional)"
        inputmode="numeric"
        placeholder="1234"
        :error="fieldErrors.lastFour"
        :disabled="submitting"
      />

      <UiCard v-if="summaryLines" title="Resumen antes de crear">
        <dl class="account-form__summary">
          <div>
            <dt>Cuenta</dt>
            <dd>{{ summaryLines.name }}</dd>
          </div>
          <div>
            <dt>Tipo</dt>
            <dd>{{ summaryLines.type }}</dd>
          </div>
          <div>
            <dt>{{ summaryLines.balanceField }}</dt>
            <dd>{{ summaryLines.balance }}</dd>
          </div>
          <div>
            <dt>Fecha</dt>
            <dd>{{ summaryLines.date }}</dd>
          </div>
        </dl>
      </UiCard>
    </template>

    <template v-else-if="editForm">
      <UiAlert tone="info" title="Saldo y tipo">
        El tipo, la moneda y el saldo no se editan aquí. Usa «Ajustar saldo» (próximamente) para corregir el balance.
      </UiAlert>

      <UiInput
        v-model="editForm.name"
        label="Nombre"
        required
        :error="fieldErrors.name"
        :disabled="submitting"
      />

      <UiInput
        v-model="editForm.institutionName"
        label="Institución (opcional)"
        :disabled="submitting"
      />

      <UiInput
        v-model="editForm.lastFour"
        label="Últimos 4 dígitos (opcional)"
        inputmode="numeric"
        :error="fieldErrors.lastFour"
        :disabled="submitting"
      />
    </template>

    <div class="account-form__actions">
      <slot name="actions" />
    </div>
  </form>
</template>

<style scoped>
.account-form__summary {
  display: grid;
  gap: var(--space-3);
  margin: 0;
}

.account-form__summary dt {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.account-form__summary dd {
  margin: 0.1rem 0 0;
  font-weight: 600;
}

.account-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: flex-end;
}
</style>
