<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['auth', 'organization', 'onboarding'],
})

const organization = useOrganizationStore()
const onboarding = useOnboardingStore()
const submitting = ref(false)

const org = computed(() => organization.currentOrganization)
const progress = computed(() => {
  const orgId = organization.currentOrganizationId
  return orgId ? onboarding.getProgress(orgId) : null
})

const preferenceLabels: Record<string, string> = {
  spend_control: 'Controlar mis gastos',
  net_worth: 'Conocer mi patrimonio',
  taxes: 'Prepararme para impuestos',
  debts: 'Pagar deudas',
  savings_goals: 'Ahorrar para metas',
  cash_flow: 'Planear mi flujo de efectivo',
}

const preferenceSummary = computed(() => {
  const intents = progress.value?.preferences ?? []
  if (!intents.length) return 'Sin preferencias guardadas'
  return intents.map(id => preferenceLabels[id] ?? id).join(', ')
})

const accountSummary = computed(() => {
  if (progress.value?.skippedAccount) return 'Omitiste agregar una cuenta por ahora'
  return 'Cuenta inicial configurada'
})

async function goToDashboard() {
  const orgId = organization.currentOrganizationId
  if (!orgId) return
  submitting.value = true
  try {
    onboarding.markComplete(orgId)
    await navigateTo('/app/dashboard')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UiCard>
    <OnboardingShell
      title="Tu espacio está listo"
      subtitle="Ya puedes comenzar a construir una vista clara de tus finanzas."
      :step="4"
      :total-steps="4"
    >
      <div class="stack">
        <div class="summary-row">
          <span class="summary-row__label">Organización</span>
          <span class="summary-row__value">{{ org?.name ?? '—' }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-row__label">Objetivos</span>
          <span class="summary-row__value">{{ preferenceSummary }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-row__label">Cuenta</span>
          <span class="summary-row__value">{{ accountSummary }}</span>
        </div>
      </div>

      <template #back>
        <UiButton type="button" variant="ghost" @click="navigateTo('/onboarding/account')">
          Atrás
        </UiButton>
      </template>
      <template #continue>
        <div class="cluster">
          <UiButton
            type="button"
            variant="secondary"
            @click="goToDashboard"
          >
            Registrar mi primer movimiento
          </UiButton>
          <UiButton type="button" :loading="submitting" @click="goToDashboard">
            Ir al Dashboard
          </UiButton>
        </div>
      </template>
    </OnboardingShell>
  </UiCard>
</template>

<style scoped>
.summary-row {
  display: grid;
  gap: 0.15rem;
  padding: var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-muted);
}

.summary-row__label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text-muted);
}

.summary-row__value {
  font-weight: 600;
  color: var(--color-ink);
}
</style>
