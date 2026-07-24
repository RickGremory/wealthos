<script setup lang="ts">
import type { AccountListItemView } from '~/types/accounts'

defineProps<{
  account: AccountListItemView
  canWrite?: boolean
  canArchive?: boolean
}>()

const emit = defineEmits<{
  edit: []
  archive: []
}>()
</script>

<template>
  <header class="detail-header" data-testid="account-detail-header">
    <div class="stack-sm">
      <NuxtLink to="/app/accounts" class="detail-header__back">
        ← Todas las cuentas
      </NuxtLink>
      <div class="detail-header__badges">
        <AccountTypeBadge
          :type-label="account.displayType"
          :archived="account.isArchived"
        />
        <CurrencyBadge :currency="account.currency" />
      </div>
      <h1 class="detail-header__title">{{ account.name }}</h1>
      <p class="text-muted detail-header__subtitle">
        {{ account.subtitle }}
        <span v-if="account.lastFour"> · ••{{ account.lastFour }}</span>
      </p>
      <AccountBalanceValue
        :amount="account.balance"
        :currency="account.currency"
        :prefix="account.balancePrefix"
        :presentation="account.balancePresentation"
        :label="account.balanceLabel"
      />
    </div>

    <div class="detail-header__actions">
      <UiButton
        type="button"
        variant="secondary"
        disabled
        title="Próximamente"
      >
        Registrar movimiento
      </UiButton>
      <UiButton
        type="button"
        variant="ghost"
        disabled
        title="Próximamente"
      >
        Transferir
      </UiButton>
      <UiButton
        v-if="canWrite && !account.isArchived"
        type="button"
        variant="secondary"
        @click="emit('edit')"
      >
        Editar
      </UiButton>
      <AccountActionsMenu
        :account="account"
        :can-write="canWrite"
        :can-archive="canArchive"
        @view="() => {}"
        @edit="emit('edit')"
        @archive="emit('archive')"
      />
    </div>
  </header>
</template>

<style scoped>
.detail-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.detail-header__back {
  display: inline-flex;
  width: fit-content;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
}

.detail-header__back:hover {
  color: var(--color-primary);
}

.detail-header__badges {
  display: flex;
  gap: var(--space-2);
}

.detail-header__title {
  margin: 0;
  font-size: clamp(1.5rem, 2.5vw, 1.9rem);
}

.detail-header__subtitle {
  margin: 0;
}

.detail-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: flex-start;
}
</style>
