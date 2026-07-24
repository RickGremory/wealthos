<script setup lang="ts">
import type { DashboardOnboarding } from '~/types/dashboard'

defineProps<{
  onboarding: DashboardOnboarding
}>()
</script>

<template>
  <section
    v-if="!onboarding.completed"
    id="onboarding"
    class="onboarding"
    aria-label="Comienza a construir tu panorama financiero"
  >
    <div class="onboarding__intro stack-sm">
      <h2 class="onboarding__title">Comienza a construir tu panorama financiero</h2>
      <p class="text-muted">
        Completa estos pasos para que WealthOS pueda mostrarte tu patrimonio,
        flujo de caja y dinero disponible.
      </p>
      <p class="onboarding__progress">
        {{ onboarding.completedSteps }} de {{ onboarding.totalSteps }} pasos completados
      </p>
    </div>

    <ol class="onboarding__list">
      <li
        v-for="step in onboarding.steps"
        :key="step.id"
        class="onboarding__step"
        :data-completed="step.completed"
      >
        <span class="onboarding__check" aria-hidden="true">
          {{ step.completed ? '✓' : '○' }}
        </span>
        <div class="stack-sm">
          <NuxtLink class="onboarding__label" :to="step.to">
            {{ step.label }}
          </NuxtLink>
          <p class="text-muted">{{ step.description }}</p>
        </div>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.onboarding {
  margin-top: var(--space-6);
  padding: var(--space-6);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background:
    linear-gradient(135deg, rgba(11, 61, 58, 0.06), transparent 55%),
    var(--color-surface);
}

.onboarding__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.4rem;
}

.onboarding__progress {
  margin: 0;
  font-weight: 700;
  color: var(--color-primary);
  font-size: 0.9rem;
}

.onboarding__list {
  list-style: none;
  margin: var(--space-5) 0 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.onboarding__step {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--space-3);
  align-items: start;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.8);
}

.onboarding__step[data-completed='true'] {
  opacity: 0.72;
}

.onboarding__check {
  width: 1.5rem;
  height: 1.5rem;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  background: var(--color-surface-muted);
  color: var(--color-primary);
  font-weight: 700;
}

.onboarding__label {
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
}

.onboarding__label:hover {
  color: var(--color-primary);
}
</style>
