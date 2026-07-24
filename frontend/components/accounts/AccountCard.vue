<script setup lang="ts">
import type { AccountListItemView } from '~/types/accounts'

const props = defineProps<{
  account: AccountListItemView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  view: []
  edit: []
  archive: []
}>()

const { formatRelativeDay } = useDate()

const updatedLabel = computed(() => {
  if (!props.account.updatedAt) return null
  return formatRelativeDay(props.account.updatedAt)
})
</script>

<template>
  <article
    class="account-card"
    :class="{ 'account-card--archived': account.isArchived }"
    data-testid="account-card"
    @click="emit('view')"
  >
    <div class="account-card__main">
      <div class="stack-sm">
        <div class="account-card__title-row">
          <h3 class="account-card__name">{{ account.name }}</h3>
          <AccountTypeBadge
            :type-label="account.displayType"
            :archived="account.isArchived"
          />
        </div>
        <p class="account-card__subtitle text-muted">
          {{ account.subtitle }}
          <span v-if="account.lastFour"> · ••{{ account.lastFour }}</span>
        </p>
      </div>
      <AccountBalanceValue
        :amount="account.balance"
        :currency="account.currency"
        :prefix="account.balancePrefix"
        :presentation="account.balancePresentation"
        :label="account.balanceLabel"
      />
    </div>
    <footer class="account-card__footer">
      <span v-if="updatedLabel" class="text-muted account-card__meta">
        Actualizada {{ updatedLabel }}
      </span>
      <span v-else class="text-muted account-card__meta">{{ account.currency }}</span>
      <AccountActionsMenu
        :account="account"
        :can-write="canWrite"
        :can-archive="canArchive"
        @view="emit('view')"
        @edit="emit('edit')"
        @archive="emit('archive')"
      />
    </footer>
  </article>
</template>

<style scoped>
.account-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  cursor: pointer;
  transition: border-color 140ms ease, box-shadow 140ms ease;
}

.account-card:hover {
  border-color: var(--color-teal-600);
  box-shadow: var(--shadow-sm);
}

.account-card--archived {
  opacity: 0.75;
}

.account-card__main {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  align-items: flex-start;
}

.account-card__title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-2);
}

.account-card__name {
  margin: 0;
  font-size: 1.05rem;
}

.account-card__subtitle {
  margin: 0;
  font-size: 0.85rem;
}

.account-card__footer {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.account-card__meta {
  font-size: 0.8rem;
}
</style>
