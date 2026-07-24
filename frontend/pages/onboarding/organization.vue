<script setup lang="ts">
import { slugify } from '~/utils/slugify'

type WorkspaceType = 'personal' | 'freelance' | 'business' | 'family'

definePageMeta({
  layout: 'auth',
  middleware: ['auth', 'onboarding'],
})

const organization = useOrganizationStore()
const { resolveDestination } = useSessionEntry()

const name = ref('')
const workspaceType = ref<WorkspaceType>('freelance')
const country = ref('MX')
const currency = ref('MXN')
const timezone = ref(
  typeof Intl !== 'undefined'
    ? Intl.DateTimeFormat().resolvedOptions().timeZone || 'America/Mexico_City'
    : 'America/Mexico_City',
)
const error = ref('')
const submitting = ref(false)
const showCreateForm = ref(false)

onMounted(async () => {
  if (!organization.hydrated) {
    await organization.loadMemberships()
  }
  if (!name.value && organization.currentOrganization) {
    name.value = organization.currentOrganization.name
  }
  showCreateForm.value = organization.memberships.length === 0
})

const hasExistingOrg = computed(() => organization.memberships.length > 0)
const existingOrg = computed(
  () => organization.currentOrganization ?? organization.memberships[0] ?? null,
)

async function goNext() {
  const destination = await resolveDestination()
  if (destination === '/onboarding/organization') {
    await navigateTo('/onboarding/preferences')
    return
  }
  await navigateTo(destination)
}

async function continueExisting() {
  if (!existingOrg.value) return
  organization.selectOrganization(existingOrg.value.id)
  await goNext()
}

async function onSubmit() {
  error.value = ''
  if (!name.value.trim()) {
    error.value = 'El nombre es obligatorio'
    return
  }

  submitting.value = true
  try {
    const suffix = workspaceType.value === 'personal' ? 'personal' : workspaceType.value
    const baseSlug = slugify(`${name.value}-${suffix}`)
    await organization.createOrganization({
      name: name.value.trim(),
      slug: baseSlug,
      currency: currency.value,
      timezone: timezone.value,
      locale: 'es-MX',
    })
    await goNext()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudo crear la organización'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UiCard>
    <OnboardingShell
      title="Tu organización"
      subtitle="Define el espacio financiero donde vivirán tus cuentas y movimientos."
      :step="1"
      :total-steps="4"
    >
      <div v-if="hasExistingOrg && existingOrg && !showCreateForm" class="stack">
        <UiAlert tone="success" title="Organización lista">
          Ya tienes <strong>{{ existingOrg.name }}</strong>. Continúa con la configuración
          o crea otra organización.
        </UiAlert>
      </div>

      <form v-else class="stack" @submit.prevent="onSubmit">
        <UiAlert v-if="error" tone="danger" title="Error">
          {{ error }}
        </UiAlert>

        <UiInput v-model="name" label="Nombre de la organización" required />
        <WorkspaceTypeSelector v-model="workspaceType" />
        <UiSelect
          v-model="country"
          label="País"
          :options="[{ label: 'México', value: 'MX' }]"
        />
        <UiSelect
          v-model="currency"
          label="Moneda"
          :options="[{ label: 'MXN — Peso mexicano', value: 'MXN' }]"
        />
        <UiInput v-model="timezone" label="Zona horaria" required />
      </form>

      <template #back>
        <UiButton
          v-if="hasExistingOrg && showCreateForm"
          type="button"
          variant="ghost"
          @click="showCreateForm = false"
        >
          Atrás
        </UiButton>
      </template>

      <template #continue>
        <template v-if="hasExistingOrg && existingOrg && !showCreateForm">
          <div class="cluster">
            <UiButton type="button" variant="secondary" @click="showCreateForm = true">
              Crear otra
            </UiButton>
            <UiButton type="button" @click="continueExisting">
              Continuar
            </UiButton>
          </div>
        </template>
        <UiButton v-else type="button" :loading="submitting" @click="onSubmit">
          Continuar
        </UiButton>
      </template>
    </OnboardingShell>
  </UiCard>
</template>
