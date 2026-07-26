<script setup lang="ts">
import type {
  CommitmentAccountOption,
  CreateCommitmentFormModel,
  UpdateCommitmentFormModel,
} from '~/types/commitments'
import { COMMITMENT_TYPE_OPTIONS } from '~/utils/commitment-types'

const form = defineModel<CreateCommitmentFormModel>('form', { required: false })
const editForm = defineModel<UpdateCommitmentFormModel>('editForm', { required: false })

const props = withDefaults(
  defineProps<{
    mode: 'create' | 'edit'
    currencyOptions: { label: string, value: string }[]
    accounts?: CommitmentAccountOption[]
    accountsLoading?: boolean
    fieldErrors?: Record<string, string>
    submitting?: boolean
    error?: string | null
    lockedCurrency?: string
    lockedTypeLabel?: string
  }>(),
  {
    accounts: () => [],
    accountsLoading: false,
    fieldErrors: () => ({}),
    submitting: false,
    error: null,
    lockedCurrency: undefined,
    lockedTypeLabel: undefined,
  },
)

const emit = defineEmits<{
  submit: []
  'debt-type-change': [string]
}>()

const priorityOptions = [
  { label: 'Alta', value: 'high' },
  { label: 'Media', value: 'medium' },
  { label: 'Baja', value: 'low' },
]

const accountTypeOptions = [
  { label: 'Tarjeta de crédito', value: 'credit_card' },
  { label: 'Préstamo', value: 'loan' },
]

const accountOptions = computed(() => [
  { label: 'Selecciona una cuenta…', value: '' },
  ...props.accounts.map(a => ({
    label: `${a.name} (${a.currency})`,
    value: a.id,
  })),
])

function onTypeChange(value: string) {
  emit('debt-type-change', value)
}
</script>

<template>
  <form class="commitment-form stack" data-testid="commitment-form" @submit.prevent="emit('submit')">
    <UiAlert v-if="error" tone="danger" title="Revisa el formulario">
      {{ error }}
    </UiAlert>

    <template v-if="mode === 'create' && form">
      <UiSelect
        v-model="form.debtType"
        label="Tipo"
        :options="COMMITMENT_TYPE_OPTIONS.map(o => ({ label: o.label, value: o.value }))"
        required
        @update:model-value="onTypeChange"
      />
      <UiInput
        v-model="form.name"
        label="Nombre"
        required
        :error="fieldErrors.name"
        data-testid="commitment-name"
      />
      <UiInput v-model="form.creditor" label="Acreedor (opcional)" />
      <UiSelect
        v-model="form.priority"
        label="Prioridad"
        :options="priorityOptions"
      />
      <UiSelect
        v-model="form.currency"
        label="Moneda"
        :options="currencyOptions"
      />

      <div class="commitment-form__account">
        <label class="checkbox">
          <input v-model="form.createAccountInline" type="checkbox">
          Crear cuenta de pasivo ahora
        </label>

        <template v-if="form.createAccountInline">
          <UiInput
            v-model="form.newAccountName"
            label="Nombre de la cuenta"
            :error="fieldErrors.newAccountName"
          />
          <UiSelect
            v-model="form.newAccountType"
            label="Tipo de cuenta"
            :options="accountTypeOptions"
          />
          <UiInput
            v-model="form.newAccountOpeningBalance"
            label="Saldo adeudado actual"
          />
          <p class="text-muted hint">
            Se registra como pasivo. Usa 0 si aún no hay saldo.
          </p>
        </template>
        <template v-else>
          <UiSelect
            v-model="form.accountId"
            label="Cuenta de pasivo"
            :options="accountOptions"
            :disabled="accountsLoading"
            required
          />
          <p v-if="fieldErrors.accountId" class="field-error">{{ fieldErrors.accountId }}</p>
        </template>
      </div>

      <div class="commitment-form__grid">
        <div>
          <UiInput
            v-model="form.interestRate"
            label="Tasa anual % (opcional)"
            :error="fieldErrors.interestRate"
          />
          <p class="text-muted hint">Ej. 42.5 — nunca 0.425</p>
        </div>
        <UiInput
          v-model="form.minimumPayment"
          label="Pago mínimo"
          :error="fieldErrors.minimumPayment"
        />
        <UiInput v-model="form.scheduledPayment" label="Pago programado" />
        <UiInput v-model="form.creditLimit" label="Límite de crédito" />
        <UiInput
          v-model="form.dueDay"
          label="Día de pago (1–31)"
          :error="fieldErrors.dueDay"
        />
        <UiInput v-model="form.statementDay" label="Día de corte (1–31)" />
      </div>
      <UiInput v-model="form.notes" label="Notas" />
    </template>

    <template v-else-if="mode === 'edit' && editForm">
      <p v-if="lockedTypeLabel" class="text-muted">
        Tipo: {{ lockedTypeLabel }} · Moneda: {{ lockedCurrency }}
      </p>
      <UiInput
        v-model="editForm.name"
        label="Nombre"
        required
        :error="fieldErrors.name"
      />
      <UiInput v-model="editForm.creditor" label="Acreedor" />
      <UiSelect
        v-model="editForm.priority"
        label="Prioridad"
        :options="priorityOptions"
      />
      <div class="commitment-form__grid">
        <UiInput v-model="editForm.interestRate" label="Tasa anual %" />
        <UiInput v-model="editForm.minimumPayment" label="Pago mínimo" />
        <UiInput v-model="editForm.scheduledPayment" label="Pago programado" />
        <UiInput v-model="editForm.creditLimit" label="Límite de crédito" />
        <UiInput
          v-model="editForm.dueDay"
          label="Día de pago"
          :error="fieldErrors.dueDay"
        />
        <UiInput v-model="editForm.statementDay" label="Día de corte" />
      </div>
      <UiInput v-model="editForm.notes" label="Notas" />
    </template>

    <div class="commitment-form__actions cluster">
      <slot name="actions" />
    </div>
  </form>
</template>

<style scoped>
.commitment-form__grid {
  display: grid;
  gap: var(--space-3);
  grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
}

.commitment-form__account {
  display: grid;
  gap: var(--space-3);
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.checkbox {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.hint {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
}

.field-error {
  margin: 0;
  color: var(--color-danger, #b42318);
  font-size: 0.8rem;
}

.commitment-form__actions {
  justify-content: flex-end;
  padding-top: var(--space-2);
}
</style>
