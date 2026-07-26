<script setup lang="ts">
import {
  toBackendAccountType,
  toOpeningBalancePayload,
  type SimplifiedAccountType,
} from '~/utils/account-type-mapper'
import { createAccountsRepository } from '~/repositories/accounts.repository'
import { toUserMessage } from '~/lib/api/errors'
import { todayLocalIsoDate } from '~/composables/use-date'

definePageMeta({
  layout: 'auth',
  middleware: ['auth', 'organization', 'onboarding'],
})

const organization = useOrganizationStore()
const onboarding = useOnboardingStore()
const { resolveDestination } = useSessionEntry()

const accountType = ref<SimplifiedAccountType>('checking')
const accountName = ref('')
const openingBalance = ref('0.00')
const openingBalanceDate = ref(todayLocalIsoDate())
const institutionName = ref('')
const error = ref('')
const submitting = ref(false)

const balanceLabel = computed(() =>
  accountType.value === 'credit_card'
    ? '¿Cuánto debes actualmente?'
    : 'Saldo inicial',
)

async function createAccount() {
  error.value = ''
  const orgId = organization.currentOrganizationId
  const org = organization.currentOrganization
  if (!orgId || !org) {
    error.value = 'Selecciona una organización primero'
    return
  }
  if (!accountName.value.trim()) {
    error.value = 'El nombre de la cuenta es obligatorio'
    return
  }

  submitting.value = true
  try {
    const { $api } = useNuxtApp()
    const repo = createAccountsRepository($api)
    await repo.create(orgId, {
      name: accountName.value.trim(),
      accountType: toBackendAccountType(accountType.value),
      currency: org.currency || 'MXN',
      openingBalance: toOpeningBalancePayload(accountType.value, openingBalance.value),
      openingBalanceDate: openingBalanceDate.value || null,
      institutionName: institutionName.value.trim() || null,
    })
    const destination = await resolveDestination()
    await navigateTo(
      destination === '/onboarding/account' ? '/onboarding/complete' : destination,
    )
  } catch (e) {
    error.value = toUserMessage(e)
  } finally {
    submitting.value = false
  }
}

async function skip() {
  const orgId = organization.currentOrganizationId
  if (!orgId) return
  onboarding.skipAccount(orgId)
  const destination = await resolveDestination()
  await navigateTo(
    destination === '/onboarding/account' ? '/onboarding/complete' : destination,
  )
}
</script>

<template>
  <UiCard>
    <OnboardingShell
      title="Tu primera cuenta"
      subtitle="Agrega una cuenta para empezar a ver tu panorama financiero."
      :step="3"
      :total-steps="4"
    >
      <form class="stack" @submit.prevent="createAccount">
        <UiAlert v-if="error" tone="danger" title="Error">
          {{ error }}
        </UiAlert>

        <UiInput v-model="accountName" label="Nombre de la cuenta" required />
        <SimplifiedAccountTypeSelector v-model="accountType" />
        <UiInput
          v-model="openingBalance"
          :label="balanceLabel"
          inputmode="decimal"
          required
        />
        <UiInput
          v-model="openingBalanceDate"
          label="Fecha del saldo"
          type="date"
          required
        />
        <UiInput
          v-model="institutionName"
          label="Institución (opcional)"
          placeholder="Banco, caja, etc."
        />
        <p class="text-muted skip-hint">
          Puedes omitir este paso e entrar al Dashboard con información limitada.
        </p>
      </form>

      <template #back>
        <UiButton type="button" variant="ghost" @click="navigateTo('/onboarding/preferences')">
          Atrás
        </UiButton>
      </template>
      <template #continue>
        <div class="cluster">
          <UiButton type="button" variant="secondary" @click="skip">
            Configurar después
          </UiButton>
          <UiButton type="button" :loading="submitting" @click="createAccount">
            Continuar
          </UiButton>
        </div>
      </template>
    </OnboardingShell>
  </UiCard>
</template>

<style scoped>
.skip-hint {
  margin: 0;
  font-size: 0.85rem;
}

.cluster {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: flex-end;
}
</style>
