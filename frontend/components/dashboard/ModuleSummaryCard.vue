<script setup lang="ts">
import type { DashboardModuleSummary } from '~/types/dashboard'

defineProps<{
  summary: DashboardModuleSummary
}>()

const { format } = useMoney()
const organization = useOrganizationStore()
const currency = computed(() => organization.currentOrganization?.currency ?? 'MXN')

function displayValue(value: string): string {
  if (/^-?\d+(\.\d+)?$/.test(value)) {
    return format(value, currency.value)
  }
  return value
}
</script>

<template>
  <UiCard :title="summary.title">
    <div v-if="summary.status === 'error'" class="stack">
      <p class="text-muted">No se pudo cargar este bloque.</p>
      <NuxtLink v-if="summary.ctaTo" class="module-cta" :to="summary.ctaTo">
        {{ summary.ctaLabel || 'Reintentar en el módulo' }}
      </NuxtLink>
    </div>
    <div v-else-if="summary.status === 'not_configured'" class="stack">
      <p class="text-muted">{{ summary.hint }}</p>
      <NuxtLink v-if="summary.ctaTo" class="module-cta" :to="summary.ctaTo">
        {{ summary.ctaLabel }}
      </NuxtLink>
    </div>
    <div v-else class="stack">
      <div
        v-for="line in summary.lines"
        :key="line.label"
        class="module-line"
      >
        <span>{{ line.label }}</span>
        <strong>{{ displayValue(line.value) }}</strong>
      </div>
      <p v-if="summary.hint" class="text-muted">{{ summary.hint }}</p>
      <NuxtLink v-if="summary.ctaTo" class="module-cta" :to="summary.ctaTo">
        {{ summary.ctaLabel }}
      </NuxtLink>
    </div>
  </UiCard>
</template>

<style scoped>
.module-line {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: 0.92rem;
}

.module-cta {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
  font-size: 0.875rem;
}

.module-cta:hover {
  text-decoration: underline;
}
</style>
