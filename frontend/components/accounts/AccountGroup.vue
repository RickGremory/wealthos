<script setup lang="ts">
import type { AccountGroupView } from '~/types/accounts'

defineProps<{
  group: AccountGroupView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  view: [id: string]
  edit: [id: string]
  archive: [id: string]
}>()
</script>

<template>
  <section class="account-group" :data-group="group.key">
    <header class="account-group__header">
      <h2 class="account-group__title">{{ group.label }}</h2>
      <span class="account-group__count text-muted">{{ group.accounts.length }}</span>
    </header>
    <div class="account-group__list">
      <AccountCard
        v-for="account in group.accounts"
        :key="account.id"
        :account="account"
        :can-write="canWrite"
        :can-archive="canArchive"
        @view="emit('view', account.id)"
        @edit="emit('edit', account.id)"
        @archive="emit('archive', account.id)"
      />
    </div>
  </section>
</template>

<style scoped>
.account-group {
  display: grid;
  gap: var(--space-3);
}

.account-group__header {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
}

.account-group__title {
  margin: 0;
  font-size: 1rem;
  color: var(--color-slate-800);
}

.account-group__count {
  font-size: 0.85rem;
}

.account-group__list {
  display: grid;
  gap: var(--space-3);
}
</style>
