<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { canWrite } = useOrganizationPermissions()
const {
  form,
  submitting,
  error,
  fieldErrors,
  currencyOptions,
  liabilityAccounts,
  accountsLoading,
  resetCreate,
  loadAccounts,
  onDebtTypeChange,
  submitCreate,
} = useCommitmentForm('create')

onMounted(async () => {
  if (!canWrite.value) {
    await navigateTo('/app/commitments')
    return
  }
  resetCreate()
  await loadAccounts()
})

async function onSubmit() {
  const id = await submitCreate()
  if (id) {
    await navigateTo(`/app/commitments/${id}`)
  }
}
</script>

<template>
  <div data-testid="commitment-new-page">
    <AppPageHeader
      title="Nueva obligación"
      description="Vincula una cuenta de pasivo. El saldo siempre vive en la cuenta."
      back-to="/app/commitments"
      back-label="← Todas las obligaciones"
    />

    <UiCard>
      <CommitmentForm
        v-model:form="form"
        mode="create"
        :currency-options="currencyOptions"
        :accounts="liabilityAccounts"
        :accounts-loading="accountsLoading"
        :field-errors="fieldErrors"
        :submitting="submitting"
        :error="error"
        @debt-type-change="onDebtTypeChange"
        @submit="onSubmit"
      >
        <template #actions>
          <UiButton
            type="button"
            variant="ghost"
            :disabled="submitting"
            @click="navigateTo('/app/commitments')"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting" data-testid="commitment-create-submit">
            Crear obligación
          </UiButton>
        </template>
      </CommitmentForm>
    </UiCard>
  </div>
</template>
