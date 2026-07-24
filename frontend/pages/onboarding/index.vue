<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['auth'],
})

const organization = useOrganizationStore()
const selectedId = ref(organization.currentOrganizationId ?? '')

onMounted(async () => {
  if (!organization.hydrated) {
    await organization.hydrate()
  }
  if (!selectedId.value && organization.memberships.length === 1) {
    selectedId.value = organization.memberships[0]!.id
  }
})

const options = computed(() =>
  organization.memberships.map(m => ({
    label: `${m.name} (${m.role})`,
    value: m.id,
  })),
)

async function continueWithOrg() {
  if (!selectedId.value) return
  organization.selectOrg(selectedId.value)
  await navigateTo('/app/dashboard')
}
</script>

<template>
  <UiCard title="Elige tu organización">
    <div class="stack">
      <p class="text-muted">
        Selecciona con qué organización quieres trabajar en esta sesión.
      </p>

      <UiAlert v-if="!organization.memberships.length" tone="warning" title="Sin membresías">
        No encontramos organizaciones vinculadas a tu usuario.
      </UiAlert>

      <UiSelect
        v-if="options.length"
        v-model="selectedId"
        label="Organización"
        :options="options"
      />

      <UiButton
        type="button"
        block
        :disabled="!selectedId"
        @click="continueWithOrg"
      >
        Continuar
      </UiButton>
    </div>
  </UiCard>
</template>
