<script setup lang="ts">
import type {
  CreateGoalFormModel,
  GoalAccountOption,
  GoalStrategy,
  UpdateGoalFormModel,
} from '~/types/goals'
import { GOAL_PRIORITY_OPTIONS } from '~/utils/goal-priority'

const form = defineModel<CreateGoalFormModel>('form', { required: true })
const editForm = defineModel<UpdateGoalFormModel | undefined>('editForm')

const props = withDefaults(
  defineProps<{
    mode: 'create' | 'edit'
    currencyOptions: Array<{ label: string, value: string }>
    accounts?: GoalAccountOption[]
    accountsLoading?: boolean
    strategyLocked?: boolean
    editStrategy?: GoalStrategy
    editCurrency?: string
    fieldErrors?: Record<string, string>
    submitting?: boolean
    error?: string | null
  }>(),
  {
    accounts: () => [],
    accountsLoading: false,
    strategyLocked: false,
    editStrategy: 'manual',
    editCurrency: 'MXN',
    fieldErrors: () => ({}),
    submitting: false,
    error: null,
  },
)

const emit = defineEmits<{
  submit: []
  'select-template': [templateId: string]
}>()

const createStrategy = computed({
  get: () => form.value.strategy,
  set: (value: GoalStrategy) => {
    form.value.strategy = value
    if (value !== 'linked_accounts') {
      form.value.linkedAccountIds = []
    }
  },
})

const createLinked = computed({
  get: () => form.value.linkedAccountIds,
  set: (value: string[]) => {
    form.value.linkedAccountIds = value
  },
})

const editLinked = computed({
  get: () => editForm.value?.linkedAccountIds ?? [],
  set: (value: string[]) => {
    if (editForm.value) editForm.value.linkedAccountIds = value
  },
})

const editStrategyModel = computed({
  get: () => props.editStrategy,
  set: () => {},
})

const priorityModel = computed({
  get: () =>
    String(props.mode === 'create' ? form.value.priority : (editForm.value?.priority ?? 2)),
  set: (value: string) => {
    const n = Number(value) as 1 | 2 | 3
    if (props.mode === 'create') {
      form.value.priority = n
    }
    else if (editForm.value) {
      editForm.value.priority = n
    }
  },
})

const priorityOptions = GOAL_PRIORITY_OPTIONS.map(o => ({
  label: o.label,
  value: String(o.value),
}))

function onTemplate(id: string) {
  emit('select-template', id)
}
</script>

<template>
  <form class="goal-form stack" data-testid="goal-form" @submit.prevent="emit('submit')">
    <UiAlert v-if="error" tone="danger" title="No se pudo guardar">
      {{ error }}
    </UiAlert>

    <template v-if="mode === 'create'">
      <GoalTemplatePicker
        v-model="form.templateId"
        @select="onTemplate"
      />

      <UiInput
        v-model="form.name"
        label="Nombre"
        required
        :error="fieldErrors.name"
        placeholder="Ej. Fondo de emergencia"
        :disabled="submitting"
      />

      <MoneyInput
        v-model="form.targetAmount"
        label="Monto objetivo"
        :currency="form.currency"
        :error="fieldErrors.targetAmount"
        :disabled="submitting"
      />

      <UiSelect
        v-model="form.currency"
        label="Moneda"
        :options="currencyOptions"
        :disabled="submitting"
        required
      />

      <UiInput
        v-model="form.targetDate"
        label="Fecha objetivo (opcional)"
        type="date"
        :error="fieldErrors.targetDate"
        :disabled="submitting"
      />

      <GoalStrategySelector
        v-model:strategy="createStrategy"
        v-model:linked-account-ids="createLinked"
        :accounts="accounts"
        :accounts-loading="accountsLoading"
        :disabled="submitting"
        :error="fieldErrors.linkedAccountIds"
      />

      <UiSelect
        v-model="priorityModel"
        label="Prioridad"
        :options="priorityOptions"
        :disabled="submitting"
      />
    </template>

    <template v-else-if="editForm">
      <UiInput
        v-model="editForm.name"
        label="Nombre"
        required
        :error="fieldErrors.name"
        :disabled="submitting"
      />

      <MoneyInput
        v-model="editForm.targetAmount"
        label="Monto objetivo"
        :currency="editCurrency"
        :error="fieldErrors.targetAmount"
        :disabled="submitting"
      />

      <UiInput
        :model-value="editCurrency"
        label="Moneda"
        disabled
      />

      <UiInput
        v-model="editForm.targetDate"
        label="Fecha objetivo (opcional)"
        type="date"
        :error="fieldErrors.targetDate"
        :disabled="submitting"
      />

      <GoalStrategySelector
        v-model:strategy="editStrategyModel"
        v-model:linked-account-ids="editLinked"
        :accounts="accounts"
        :accounts-loading="accountsLoading"
        :disabled="submitting"
        locked
        :error="fieldErrors.linkedAccountIds"
      />

      <UiSelect
        v-model="priorityModel"
        label="Prioridad"
        :options="priorityOptions"
        :disabled="submitting"
      />
    </template>

    <div class="goal-form__actions cluster">
      <slot name="actions" />
    </div>
  </form>
</template>

<style scoped>
.goal-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
</style>
