<script setup lang="ts">
import { createLegalRepository } from '~/repositories/legal.repository'
import type { RegistrationRequirements } from '~/repositories/legal.repository'

definePageMeta({
  layout: 'auth',
  middleware: ['guest'],
})

const auth = useAuthStore()
const toast = useToast()
const { resolveDestination } = useSessionEntry()
const { $api } = useNuxtApp()
const legalRepo = createLegalRepository($api)

const displayName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptedTerms = ref(false)
const marketingConsent = ref(false)
const error = ref('')
const submitting = ref(false)
const passwordTouched = ref(false)
const requirements = ref<RegistrationRequirements | null>(null)

const { rules } = usePasswordRules(password)

const termsDoc = computed(() =>
  requirements.value?.documents.find(d => d.type === 'terms_of_service') ?? null,
)
const privacyDoc = computed(() =>
  requirements.value?.documents.find(d => d.type === 'privacy_notice') ?? null,
)

const canSubmit = computed(() =>
  rules.value.isValid && acceptedTerms.value && !submitting.value,
)

onMounted(async () => {
  try {
    requirements.value = await legalRepo.getRegistrationRequirements()
  } catch {
    // Fallback links if API unavailable.
    requirements.value = {
      documents: [
        {
          type: 'terms_of_service',
          version: '1.0',
          title: 'Términos de servicio',
          url: '/legal/terms',
          acceptance_required: true,
        },
        {
          type: 'privacy_notice',
          version: '1.0',
          title: 'Aviso de privacidad',
          url: '/legal/privacy',
          acknowledgement_required: true,
        },
      ],
      marketingConsent: { available: true, required: false },
    }
  }
})

async function onSubmit() {
  error.value = ''
  passwordTouched.value = true

  if (!rules.value.isValid) {
    error.value = 'La contraseña no cumple los requisitos'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }

  if (!acceptedTerms.value) {
    error.value = 'Debes aceptar los términos para continuar'
    return
  }

  if (!termsDoc.value || !privacyDoc.value) {
    error.value = 'No se pudieron cargar los documentos legales'
    return
  }

  submitting.value = true
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      displayName: displayName.value,
      legalAcceptances: [
        {
          documentType: termsDoc.value.type,
          version: termsDoc.value.version,
          accepted: true,
        },
        {
          documentType: privacyDoc.value.type,
          version: privacyDoc.value.version,
          acknowledged: true,
        },
      ],
      marketingConsent: marketingConsent.value,
    })

    const organization = useOrganizationStore()
    await organization.loadMemberships()
    if (organization.memberships.length === 1) {
      organization.selectOrganization(organization.memberships[0]!.id)
    }

    toast.success('Cuenta creada', 'Continuemos con tu configuración')
    const destination = await resolveDestination()
    await navigateTo(destination)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudo registrar'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <UiCard title="Crear cuenta">
    <form class="stack" @submit.prevent="onSubmit">
      <UiAlert v-if="error" tone="danger" title="Error">
        {{ error }}
      </UiAlert>

      <UiInput
        v-model="displayName"
        label="Nombre"
        required
        autocomplete="name"
      />
      <UiInput
        v-model="email"
        label="Correo"
        type="email"
        required
        autocomplete="email"
      />
      <PasswordInput
        v-model="password"
        label="Contraseña"
        autocomplete="new-password"
        required
        @update:model-value="passwordTouched = true"
      />
      <PasswordRequirements :rules="rules" :visible="passwordTouched" />
      <PasswordInput
        v-model="confirmPassword"
        label="Confirmar contraseña"
        autocomplete="new-password"
        required
      />

      <label class="register-terms">
        <input v-model="acceptedTerms" type="checkbox" required>
        <span>
          Acepto los
          <a
            :href="termsDoc?.url ?? '/legal/terms'"
            target="_blank"
            rel="noopener noreferrer"
          >términos de servicio</a>
        </span>
      </label>

      <p class="register-privacy">
        Al crear tu cuenta confirmas que has leído el
        <a
          :href="privacyDoc?.url ?? '/legal/privacy'"
          target="_blank"
          rel="noopener noreferrer"
        >Aviso de privacidad</a>.
      </p>

      <label v-if="requirements?.marketingConsent.available" class="register-terms">
        <input v-model="marketingConsent" type="checkbox">
        <span>Quiero recibir novedades y consejos de producto (opcional)</span>
      </label>

      <UiButton type="submit" block :loading="submitting" :disabled="!canSubmit">
        Crear cuenta
      </UiButton>
    </form>

    <template #footer>
      <p class="text-muted">
        ¿Ya tienes cuenta?
        <NuxtLink to="/login">Inicia sesión</NuxtLink>
      </p>
    </template>
  </UiCard>
</template>

<style scoped>
.register-terms {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  font-size: 0.875rem;
  color: var(--color-slate-700);
}

.register-terms input {
  margin-top: 0.2rem;
}

.register-privacy {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-slate-700);
  line-height: 1.45;
}
</style>
