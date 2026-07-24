<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['auth', 'organization', 'onboarding'],
})

const organization = useOrganizationStore()
const onboarding = useOnboardingStore()
const { resolveDestination } = useSessionEntry()

const INTENT_OPTIONS = [
  { id: 'spend_control', label: 'Controlar mis gastos' },
  { id: 'net_worth', label: 'Conocer mi patrimonio' },
  { id: 'taxes', label: 'Prepararme para impuestos' },
  { id: 'debts', label: 'Pagar deudas' },
  { id: 'savings_goals', label: 'Ahorrar para metas' },
  { id: 'cash_flow', label: 'Planear mi flujo de efectivo' },
] as const

const selected = ref<string[]>([])
const error = ref('')
const submitting = ref(false)

onMounted(async () => {
  if (!organization.hydrated) {
    await organization.loadMemberships()
  }
  const orgId = organization.currentOrganizationId
  if (orgId) {
    const progress = onboarding.loadProgress(orgId)
    selected.value = [...progress.preferences]
  }
})

function toggle(id: string) {
  if (selected.value.includes(id)) {
    selected.value = selected.value.filter(item => item !== id)
  } else {
    selected.value = [...selected.value, id]
  }
}

async function onContinue() {
  error.value = ''
  const orgId = organization.currentOrganizationId
  if (!orgId) {
    error.value = 'Selecciona una organización primero'
    return
  }
  if (selected.value.length === 0) {
    error.value = 'Elige al menos un objetivo'
    return
  }

  submitting.value = true
  try {
    onboarding.savePreferences(orgId, selected.value)
    const destination = await resolveDestination()
    await navigateTo(
      destination === '/onboarding/preferences' ? '/onboarding/account' : destination,
    )
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UiCard>
    <OnboardingShell
      title="¿Qué te importa ahora?"
      subtitle="Elige uno o más objetivos. Podrás cambiarlos después."
      :step="2"
      :total-steps="4"
    >
      <div class="stack">
        <UiAlert v-if="error" tone="danger" title="Error">
          {{ error }}
        </UiAlert>

        <div class="intent-grid">
          <button
            v-for="option in INTENT_OPTIONS"
            :key="option.id"
            type="button"
            class="intent-option"
            :data-selected="selected.includes(option.id)"
            @click="toggle(option.id)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <template #back>
        <UiButton type="button" variant="ghost" @click="navigateTo('/onboarding/organization')">
          Atrás
        </UiButton>
      </template>
      <template #continue>
        <UiButton type="button" :loading="submitting" @click="onContinue">
          Continuar
        </UiButton>
      </template>
    </OnboardingShell>
  </UiCard>
</template>

<style scoped>
.intent-grid {
  display: grid;
  gap: var(--space-2);
}

.intent-option {
  text-align: left;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-weight: 600;
  color: var(--color-ink);
  cursor: pointer;
}

.intent-option[data-selected='true'] {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}
</style>
