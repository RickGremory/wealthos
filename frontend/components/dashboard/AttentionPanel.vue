<script setup lang="ts">
import type { DashboardAttentionItem } from '~/types/dashboard'

defineProps<{
  items: DashboardAttentionItem[]
}>()
</script>

<template>
  <section v-if="items.length" class="attention" aria-label="Necesita tu atención">
    <div class="attention__header">
      <h2 class="attention__title">Necesita tu atención</h2>
      <NuxtLink to="/app/calendar" class="attention__all text-muted">
        Ver todas las alertas
      </NuxtLink>
    </div>

    <ul class="attention__list">
      <li
        v-for="item in items"
        :key="item.id"
        class="attention__item"
        :data-severity="item.severity"
      >
        <div class="stack-sm">
          <p class="attention__item-title">{{ item.title }}</p>
          <p class="attention__item-message text-muted">{{ item.message }}</p>
          <p
            v-if="item.amount != null && item.currency"
            class="attention__amount"
          >
            <MoneyValue :amount="item.amount" :currency="item.currency" />
          </p>
        </div>
        <NuxtLink class="attention__action" :to="item.actionTo">
          {{ item.actionLabel }}
        </NuxtLink>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.attention {
  margin-top: var(--space-6);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
}

.attention__header {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  align-items: baseline;
  margin-bottom: var(--space-4);
}

.attention__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.25rem;
}

.attention__all {
  font-size: 0.85rem;
  text-decoration: none;
}

.attention__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.attention__item {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  align-items: center;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface-muted);
}

.attention__item[data-severity='warning'] {
  border-color: color-mix(in srgb, var(--color-warning) 45%, var(--color-border));
}

.attention__item[data-severity='critical'] {
  border-color: color-mix(in srgb, var(--color-danger) 45%, var(--color-border));
}

.attention__item-title {
  margin: 0;
  font-weight: 700;
}

.attention__item-message,
.attention__amount {
  margin: 0;
}

.attention__action {
  flex-shrink: 0;
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
  font-size: 0.875rem;
}

@media (max-width: 700px) {
  .attention__item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
