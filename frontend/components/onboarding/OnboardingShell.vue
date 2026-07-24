<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string
    step?: number
    totalSteps?: number
    subtitle?: string
  }>(),
  {
    step: undefined,
    totalSteps: undefined,
    subtitle: undefined,
  },
)
</script>

<template>
  <div class="onboarding-shell stack-lg">
    <header class="onboarding-shell__header stack-sm">
      <p class="onboarding-shell__brand">WealthOS</p>
      <p v-if="step && totalSteps" class="onboarding-shell__step text-muted">
        Paso {{ step }} de {{ totalSteps }}
      </p>
      <h1 class="onboarding-shell__title">{{ title }}</h1>
      <p v-if="subtitle" class="onboarding-shell__subtitle text-muted">
        {{ subtitle }}
      </p>
    </header>

    <div class="onboarding-shell__body">
      <slot />
    </div>

    <footer v-if="$slots.actions || $slots.back || $slots.continue" class="onboarding-shell__footer">
      <slot name="actions">
        <div class="onboarding-shell__nav">
          <div class="onboarding-shell__back">
            <slot name="back" />
          </div>
          <div class="onboarding-shell__continue">
            <slot name="continue" />
          </div>
        </div>
      </slot>
    </footer>
  </div>
</template>

<style scoped>
.onboarding-shell__brand {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--color-teal-800);
}

.onboarding-shell__step {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.onboarding-shell__title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--color-ink);
}

.onboarding-shell__subtitle {
  margin: 0;
  line-height: 1.45;
}

.onboarding-shell__nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.onboarding-shell__continue {
  margin-left: auto;
}
</style>
