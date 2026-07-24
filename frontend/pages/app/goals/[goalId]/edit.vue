<script setup lang="ts">
import { createGoalsRepository } from '~/repositories/goals.repository'
import { toUserMessage } from '~/lib/api/errors'
import { applyGoalPriorities } from '~/composables/use-goals'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const goalId = computed(() => String(route.params.goalId))
const organization = useOrganizationStore()
const preferences = usePreferencesStore()
const { canWrite } = useOrganizationPermissions()
const { $api } = useNuxtApp()

const {
  form,
  editForm,
  editMeta,
  submitting,
  error,
  fieldErrors,
  currencyOptions,
  linkableAccounts,
  accountsLoading,
  loadEdit,
  loadAccounts,
  submitEdit,
} = useGoalForm('edit')

const loading = ref(true)
const loadError = ref<string | null>(null)
const goalName = ref('')

onMounted(async () => {
  if (!canWrite.value) {
    await navigateTo(`/app/goals/${goalId.value}`)
    return
  }

  const orgId = organization.currentOrganizationId
  if (!orgId) {
    loadError.value = 'Selecciona una organización.'
    loading.value = false
    return
  }

  try {
    const repo = createGoalsRepository($api)
    const raw = await repo.get(orgId, goalId.value)
    const [withPriority] = applyGoalPriorities(
      [raw],
      id => preferences.getGoalPriority(id),
    )
    const goal = withPriority ?? raw
    goalName.value = goal.name
    loadEdit(goal)
    await loadAccounts()
  }
  catch (e) {
    loadError.value = toUserMessage(e)
  }
  finally {
    loading.value = false
  }
})

async function onSubmit() {
  const ok = await submitEdit(goalId.value)
  if (ok) {
    await navigateTo(`/app/goals/${goalId.value}`)
  }
}
</script>

<template>
  <div data-testid="goal-edit-page">
    <AppPageHeader
      :title="goalName ? `Editar · ${goalName}` : 'Editar meta'"
      description="Puedes ajustar nombre, monto, fecha, cuentas vinculadas y prioridad. La estrategia y la moneda no cambian."
    />

    <div v-if="loading">
      <UiSkeleton height="12rem" />
    </div>
    <UiAlert v-else-if="loadError" tone="danger" title="Error">
      {{ loadError }}
    </UiAlert>
    <UiCard v-else>
      <GoalForm
        v-model:form="form"
        v-model:edit-form="editForm"
        mode="edit"
        :currency-options="currencyOptions"
        :accounts="linkableAccounts"
        :accounts-loading="accountsLoading"
        strategy-locked
        :edit-strategy="editMeta.strategy"
        :edit-currency="editMeta.currency"
        :field-errors="fieldErrors"
        :submitting="submitting"
        :error="error"
        @submit="onSubmit"
      >
        <template #actions>
          <UiButton
            type="button"
            variant="ghost"
            :disabled="submitting"
            @click="navigateTo(`/app/goals/${goalId}`)"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting" data-testid="goal-edit-submit">
            Guardar cambios
          </UiButton>
        </template>
      </GoalForm>
    </UiCard>
  </div>
</template>
