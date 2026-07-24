<script setup lang="ts">
import { createAccountsRepository } from '~/repositories/accounts.repository'
import { toUserMessage } from '~/lib/api/errors'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const route = useRoute()
const accountId = computed(() => String(route.params.accountId))
const organization = useOrganizationStore()
const { canWrite } = useOrganizationPermissions()
const { $api } = useNuxtApp()

const {
  form,
  editForm,
  submitting,
  error,
  fieldErrors,
  balanceLabel,
  currencyOptions,
  loadEdit,
  submitEdit,
} = useAccountForm('edit')

const loading = ref(true)
const loadError = ref<string | null>(null)
const accountName = ref('')

onMounted(async () => {
  if (!canWrite.value) {
    await navigateTo(`/app/accounts/${accountId.value}`)
    return
  }

  const orgId = organization.currentOrganizationId
  if (!orgId) {
    loadError.value = 'Selecciona una organización.'
    loading.value = false
    return
  }

  try {
    const repo = createAccountsRepository($api)
    const account = await repo.get(orgId, accountId.value)
    accountName.value = account.name
    loadEdit(account)
  } catch (e) {
    loadError.value = toUserMessage(e)
  } finally {
    loading.value = false
  }
})

async function onSubmit() {
  const ok = await submitEdit(accountId.value)
  if (ok) {
    await navigateTo(`/app/accounts/${accountId.value}`)
  }
}
</script>

<template>
  <div data-testid="account-edit-page">
    <AppPageHeader
      :title="accountName ? `Editar · ${accountName}` : 'Editar cuenta'"
      description="Actualiza el nombre y datos de identificación. El saldo se ajusta con una operación dedicada."
    />

    <div v-if="loading">
      <UiSkeleton height="12rem" />
    </div>
    <UiAlert v-else-if="loadError" tone="danger" title="Error">
      {{ loadError }}
    </UiAlert>
    <UiCard v-else>
      <AccountForm
        v-model:form="form"
        v-model:edit-form="editForm"
        mode="edit"
        :balance-label="balanceLabel"
        :currency-options="currencyOptions"
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
            @click="navigateTo(`/app/accounts/${accountId}`)"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting">
            Guardar cambios
          </UiButton>
        </template>
      </AccountForm>
    </UiCard>
  </div>
</template>
