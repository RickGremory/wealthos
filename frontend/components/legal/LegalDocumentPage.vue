<script setup lang="ts">
import { createLegalRepository } from '~/repositories/legal.repository'

const props = defineProps<{
  documentType: string
  fallbackTitle: string
}>()

const { $api } = useNuxtApp()
const repo = createLegalRepository($api)

const { data, error, pending } = await useAsyncData(
  `legal-doc-${props.documentType}`,
  () => repo.getDocument(props.documentType),
)

const title = computed(() => data.value?.title ?? props.fallbackTitle)

useSeoMeta({
  title: () => `${title.value} · WealthOS`,
})
</script>

<template>
  <article class="legal-doc">
    <p v-if="pending" class="text-muted">Cargando documento…</p>
    <UiAlert v-else-if="error" tone="danger" title="No se pudo cargar">
      Intenta de nuevo más tarde.
    </UiAlert>
    <template v-else-if="data">
      <h1>{{ data.title }}</h1>
      <p class="legal-doc__meta">
        Versión {{ data.version }}
      </p>
      <pre class="legal-doc__body">{{ data.contentMarkdown }}</pre>
    </template>
  </article>
</template>

<style scoped>
.legal-doc h1 {
  font-family: var(--font-display, Georgia, serif);
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  margin: 0 0 var(--space-2, 0.5rem);
}

.legal-doc__meta {
  margin: 0 0 var(--space-4, 1rem);
  color: var(--color-slate-600, #475569);
  font-size: 0.875rem;
}

.legal-doc__body {
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.65;
}
</style>
