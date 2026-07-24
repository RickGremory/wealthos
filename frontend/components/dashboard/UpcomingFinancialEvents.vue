<script setup lang="ts">
defineProps<{
  items: Array<{
    id: string
    dateLabel: string
    description: string
    amount: string
    currency: string
    status: string
  }>
}>()
</script>

<template>
  <UiCard title="Próximos 30 días">
    <UiEmptyState
      v-if="!items.length"
      title="Sin compromisos próximos"
      description="Agrega pagos recurrentes o un cash plan para anticipar tu flujo de caja."
    >
      <template #actions>
        <UiButton type="button" variant="secondary" @click="navigateTo('/app/calendar')">
          Abrir calendario
        </UiButton>
      </template>
    </UiEmptyState>

    <ul v-else class="upcoming__list">
      <li v-for="item in items" :key="item.id" class="upcoming__item">
        <span class="upcoming__date">{{ item.dateLabel }}</span>
        <span class="upcoming__desc">{{ item.description }}</span>
        <MoneyValue :amount="item.amount" :currency="item.currency" />
      </li>
    </ul>
  </UiCard>
</template>

<style scoped>
.upcoming__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-3);
}

.upcoming__item {
  display: grid;
  grid-template-columns: 4.5rem 1fr auto;
  gap: var(--space-3);
  align-items: center;
  font-size: 0.92rem;
}

.upcoming__date {
  font-weight: 700;
  color: var(--color-text-muted);
  font-size: 0.78rem;
  letter-spacing: 0.04em;
}

.upcoming__desc {
  font-weight: 600;
}
</style>
