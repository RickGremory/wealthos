<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['guest'],
})

const auth = useAuthStore()
const toast = useToast()
const { resolveDestination } = useSessionEntry()

const displayName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptedTerms = ref(false)
const error = ref('')
const submitting = ref(false)
const passwordTouched = ref(false)

const { rules } = usePasswordRules(password)

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

  submitting.value = true
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      displayName: displayName.value,
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
        <span>Acepto los términos de uso y la política de privacidad</span>
      </label>

      <UiButton type="submit" block :loading="submitting" :disabled="!rules.isValid">
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
</style>
