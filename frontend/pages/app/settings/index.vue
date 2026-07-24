<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const preferences = usePreferencesStore()
const organization = useOrganizationStore()
</script>

<template>
  <div>
    <AppPageHeader
      title="Ajustes"
      description="Preferencias de la sesión y de la organización."
    />

    <div class="stack">
      <UiCard title="Preferencias">
        <div class="stack">
          <UiInput v-model="preferences.locale" label="Locale" />
          <label class="cluster">
            <input v-model="preferences.hideBalances" type="checkbox">
            <span>Ocultar montos por defecto</span>
          </label>
        </div>
      </UiCard>

      <UiCard title="Organización activa">
        <p v-if="organization.currentOrganization">
          {{ organization.currentOrganization.name }}
          <CurrencyBadge :currency="organization.currentOrganization.currency" />
        </p>
        <p v-else class="text-muted">Ninguna seleccionada</p>
        <template #footer>
          <NuxtLink to="/select-organization">Cambiar organización</NuxtLink>
        </template>
      </UiCard>

      <UiCard title="Privacidad y legal">
        <p class="text-muted">
          Documentos aceptados, consentimiento de marketing y derechos ARCO.
        </p>
        <template #footer>
          <NuxtLink to="/app/settings/privacy">Abrir privacidad</NuxtLink>
          <span aria-hidden="true"> · </span>
          <NuxtLink to="/legal/cookies">Cookies</NuxtLink>
        </template>
      </UiCard>
    </div>
  </div>
</template>
