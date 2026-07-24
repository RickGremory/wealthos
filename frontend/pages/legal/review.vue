<script setup lang="ts">
import { createLegalRepository } from '~/repositories/legal.repository'
import type { PendingLegalDocument } from '~/repositories/legal.repository'

definePageMeta({
  layout: 'legal',
  middleware: ['auth'],
})

const { $api } = useNuxtApp()
const repo = createLegalRepository($api)
const { resolveDestination } = useSessionEntry()
const toast = useToast()

const pending = ref<PendingLegalDocument[]>([])
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const accepted = ref(false)

onMounted(async () => {
  try {
    const status = await repo.getStatus()
    if (status.isCompliant) {
      const destination = await resolveDestination()
      await navigateTo(destination)
      return
    }
    pending.value = status.pendingDocuments
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudo cargar el estado legal'
  } finally {
    loading.value = false
  }
})

async function onAccept() {
  if (!accepted.value || pending.value.length === 0) return
  error.value = ''
  submitting.value = true
  try {
    await repo.acceptDocuments(
      pending.value.map(doc => ({
        documentType: doc.type,
        version: doc.version,
        accepted: true,
        acknowledged: doc.type === 'privacy_notice' ? true : undefined,
      })),
    )
    toast.success('Documentos aceptados', 'Puedes continuar')
    const destination = await resolveDestination()
    await navigateTo(destination)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'No se pudieron registrar las aceptaciones'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <article class="legal-review">
    <h1>Revisión legal</h1>
    <p class="legal-review__lead">
      Hay documentos actualizados que debes aceptar para continuar usando WealthOS.
    </p>

    <p v-if="loading" class="text-muted">Cargando…</p>
    <UiAlert v-else-if="error" tone="danger" title="Error">
      {{ error }}
    </UiAlert>

    <template v-else>
      <ul class="legal-review__list">
        <li v-for="doc in pending" :key="`${doc.type}-${doc.version}`">
          <a :href="doc.url" target="_blank" rel="noopener noreferrer">
            {{ doc.title }}
          </a>
          <span class="text-muted">v{{ doc.version }}</span>
        </li>
      </ul>

      <label class="legal-review__check">
        <input v-model="accepted" type="checkbox">
        <span>He leído y acepto los documentos pendientes</span>
      </label>

      <UiButton
        type="button"
        block
        :loading="submitting"
        :disabled="!accepted || pending.length === 0"
        @click="onAccept"
      >
        Continuar
      </UiButton>
    </template>
  </article>
</template>

<style scoped>
.legal-review h1 {
  font-family: var(--font-display, Georgia, serif);
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  margin: 0 0 var(--space-3, 0.75rem);
}

.legal-review__lead {
  color: var(--color-slate-600, #475569);
  margin: 0 0 var(--space-5, 1.25rem);
}

.legal-review__list {
  list-style: none;
  padding: 0;
  margin: 0 0 var(--space-5, 1.25rem);
  display: grid;
  gap: var(--space-3, 0.75rem);
}

.legal-review__list li {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3, 0.75rem);
  min-width: 0;
}

.legal-review__check {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2, 0.5rem);
  margin-bottom: var(--space-4, 1rem);
  font-size: 0.9rem;
}

.legal-review__check input {
  margin-top: 0.2rem;
}
</style>
