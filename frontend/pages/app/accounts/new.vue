<script setup lang="ts">
import type { BackendAccountType } from '~/utils/account-type-mapper'
import { ACCOUNT_TYPE_OPTIONS } from '~/utils/account-type-mapper'

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
  balanceLabel,
  currencyOptions,
  resetCreate,
  submitCreate,
  setAccountType,
} = useAccountForm('create')

onMounted(() => {
  if (!canWrite.value) {
    void navigateTo('/app/accounts')
    return
  }
  const typeParam = String(route.query.type ?? '')
  const valid = ACCOUNT_TYPE_OPTIONS.some(o => o.value === typeParam)
  resetCreate({
    accountType: valid ? (typeParam as BackendAccountType) : 'checking',
  })
})

async function onSubmit() {
  const id = await submitCreate()
  if (id) {
    await navigateTo(`/app/accounts/${id}`)
  }
}
</script>

<template>
  <div data-testid="account-new-page">
    <AppPageHeader
      title="Nueva cuenta"
      description="Agrega un lugar donde vive tu dinero o una deuda que quieras seguir."
      back-to="/app/accounts"
      back-label="← Todas las cuentas"
    />

    <UiCard>
      <AccountForm
        v-model:form="form"
        mode="create"
        :balance-label="balanceLabel"
        :currency-options="currencyOptions"
        :field-errors="fieldErrors"
        :submitting="submitting"
        :error="error"
        @update:account-type="setAccountType"
        @submit="onSubmit"
      >
        <template #actions>
          <UiButton
            type="button"
            variant="ghost"
            :disabled="submitting"
            @click="navigateTo('/app/accounts')"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting">
            Crear cuenta
          </UiButton>
        </template>
      </AccountForm>
    </UiCard>
  </div>
</template>
