<script setup lang="ts">
import { createCommitmentsRepository } from '~/repositories/commitments.repository'
import { toUserMessage } from '~/lib/api/errors'
import { getCommitmentTypeLabel } from '~/utils/commitment-types'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const commitmentId = computed(() => String(route.params.commitmentId))
const organization = useOrganizationStore()
const { canWrite } = useOrganizationPermissions()
const { $api } = useNuxtApp()

const {
  editForm,
  editMeta,
  submitting,
  error,
  fieldErrors,
  currencyOptions,
  loadEdit,
  submitEdit,
} = useCommitmentForm('edit')

const loading = ref(true)
const loadError = ref<string | null>(null)

onMounted(async () => {
  if (!canWrite.value) {
    await navigateTo(`/app/commitments/${commitmentId.value}`)
    return
  }
  const orgId = organization.currentOrganizationId
  if (!orgId) {
    loadError.value = 'Selecciona una organización.'
    loading.value = false
    return
  }
  try {
    const repo = createCommitmentsRepository($api)
    const item = await repo.get(orgId, commitmentId.value)
    loadEdit(item)
  }
  catch (e) {
    loadError.value = toUserMessage(e)
  }
  finally {
    loading.value = false
  }
})

async function onSubmit() {
  const ok = await submitEdit(commitmentId.value)
  if (ok) {
    await navigateTo(`/app/commitments/${commitmentId.value}`)
  }
}
</script>

<template>
  <div data-testid="commitment-edit-page">
    <AppPageHeader
      title="Editar obligación"
      back-to="/app/commitments"
      back-label="← Obligaciones"
    />

    <div v-if="loading">
      <UiSkeleton height="16rem" />
    </div>
    <UiAlert v-else-if="loadError" tone="danger" title="No se pudo cargar">
      {{ loadError }}
    </UiAlert>
    <UiCard v-else>
      <CommitmentForm
        v-model:edit-form="editForm"
        mode="edit"
        :currency-options="currencyOptions"
        :field-errors="fieldErrors"
        :submitting="submitting"
        :error="error"
        :locked-currency="editMeta.currency"
        :locked-type-label="getCommitmentTypeLabel(editMeta.debtType)"
        @submit="onSubmit"
      >
        <template #actions>
          <UiButton
            type="button"
            variant="ghost"
            :disabled="submitting"
            @click="navigateTo(`/app/commitments/${commitmentId}`)"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting">
            Guardar cambios
          </UiButton>
        </template>
      </CommitmentForm>
    </UiCard>
  </div>
</template>
