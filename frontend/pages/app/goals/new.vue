<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const { canWrite } = useOrganizationPermissions()
const {
  form,
  submitting,
  error,
  fieldErrors,
  currencyOptions,
  linkableAccounts,
  accountsLoading,
  resetCreate,
  applyTemplate,
  loadAccounts,
  submitCreate,
} = useGoalForm('create')

onMounted(async () => {
  if (!canWrite.value) {
    await navigateTo('/app/goals')
    return
  }
  resetCreate()
  await loadAccounts()
  const templateId = String(route.query.template ?? '')
  if (templateId) {
    applyTemplate(templateId)
  }
})

async function onSubmit() {
  const id = await submitCreate()
  if (id) {
    await navigateTo(`/app/goals/${id}`)
  }
}

function onSelectTemplate(id: string) {
  applyTemplate(id)
}
</script>

<template>
  <div data-testid="goal-new-page">
    <AppPageHeader
      title="Nueva meta"
      description="Define un objetivo claro y elige cómo medirás el avance."
      back-to="/app/goals"
      back-label="← Todas las metas"
    />

    <UiCard>
      <GoalForm
        v-model:form="form"
        mode="create"
        :currency-options="currencyOptions"
        :accounts="linkableAccounts"
        :accounts-loading="accountsLoading"
        :field-errors="fieldErrors"
        :submitting="submitting"
        :error="error"
        @select-template="onSelectTemplate"
        @submit="onSubmit"
      >
        <template #actions>
          <UiButton
            type="button"
            variant="ghost"
            :disabled="submitting"
            @click="navigateTo('/app/goals')"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting" data-testid="goal-create-submit">
            Crear meta
          </UiButton>
        </template>
      </GoalForm>
    </UiCard>
  </div>
</template>
