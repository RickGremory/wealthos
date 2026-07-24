<script setup lang="ts">
import { createLegalRepository } from '~/repositories/legal.repository'
import type { UserLegalDocuments } from '~/repositories/legal.repository'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { $api } = useNuxtApp()
const repo = createLegalRepository($api)
const toast = useToast()
const cookies = useCookiePreferencesStore()

const data = ref<UserLegalDocuments | null>(null)
const loading = ref(true)
const error = ref('')
const marketingSaving = ref(false)

onMounted(async () => {
  try {
    data.value = await repo.getMyDocuments()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudo cargar la privacidad'
  } finally {
    loading.value = false
  }
})

async function onMarketingToggle(value: boolean) {
  if (!data.value) return
  marketingSaving.value = true
  try {
    const result = await repo.setMarketingConsent(value)
    data.value = {
      ...data.value,
      marketingConsent: {
        optedIn: result.optedIn,
        updatedAt: result.updatedAt,
      },
    }
    toast.success(
      value ? 'Marketing activado' : 'Marketing desactivado',
      'Preferencia actualizada',
    )
  } catch (e) {
    toast.error('Error', e instanceof Error ? e.message : 'No se pudo guardar')
  } finally {
    marketingSaving.value = false
  }
}

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return new Intl.DateTimeFormat('es-MX', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}
</script>

<template>
  <div>
    <AppPageHeader
      title="Privacidad"
      description="Documentos aceptados, marketing y derechos ARCO."
    />

    <div class="stack">
      <UiAlert v-if="error" tone="danger" title="Error">
        {{ error }}
      </UiAlert>

      <UiCard title="Documentos aceptados">
        <p v-if="loading" class="text-muted">Cargando…</p>
        <ul v-else-if="data?.documents.length" class="privacy-docs">
          <li v-for="doc in data.documents" :key="`${doc.type}-${doc.version}`">
            <div>
              <NuxtLink :to="doc.url">{{ doc.title }}</NuxtLink>
              <span class="text-muted"> v{{ doc.version }}</span>
            </div>
            <span class="text-muted">{{ formatDate(doc.acceptedAt) }}</span>
          </li>
        </ul>
        <p v-else class="text-muted">Sin aceptaciones registradas.</p>
      </UiCard>

      <UiCard title="Marketing">
        <label class="cluster">
          <input
            type="checkbox"
            :checked="data?.marketingConsent.optedIn ?? false"
            :disabled="marketingSaving || loading"
            @change="onMarketingToggle(($event.target as HTMLInputElement).checked)"
          >
          <span>Recibir novedades y consejos de producto</span>
        </label>
        <p v-if="data?.marketingConsent.updatedAt" class="text-muted privacy-meta">
          Última actualización: {{ formatDate(data.marketingConsent.updatedAt) }}
        </p>
      </UiCard>

      <UiCard title="Preferencias de cookies (dispositivo)">
        <p class="text-muted">
          Las cookies esenciales siempre están activas. Analítica y marketing permanecen
          desactivadas por defecto; no mostramos banner mientras no se habiliten.
        </p>
        <div class="stack privacy-cookies">
          <label class="cluster">
            <input type="checkbox" checked disabled>
            <span>Esenciales (siempre activas)</span>
          </label>
          <label class="cluster">
            <input v-model="cookies.analytics" type="checkbox">
            <span>Analítica</span>
          </label>
          <label class="cluster">
            <input v-model="cookies.marketing" type="checkbox">
            <span>Marketing</span>
          </label>
        </div>
        <template #footer>
          <NuxtLink to="/legal/cookies">Política de cookies</NuxtLink>
        </template>
      </UiCard>

      <UiCard title="Derechos ARCO">
        <p>
          Para ejercer acceso, rectificación, cancelación u oposición, escribe a
          <a href="mailto:privacy@wealthos.app">privacy@wealthos.app</a>.
        </p>
        <p class="text-muted privacy-meta">
          El flujo completo de ARCO y eliminación de cuenta vía API se habilitará en una versión posterior.
        </p>
      </UiCard>
    </div>
  </div>
</template>

<style scoped>
.privacy-docs {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: var(--space-3);
}

.privacy-docs li {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  min-width: 0;
  flex-wrap: wrap;
}

.privacy-meta {
  margin: var(--space-2) 0 0;
  font-size: 0.875rem;
}

.privacy-cookies {
  margin-top: var(--space-3);
}
</style>
