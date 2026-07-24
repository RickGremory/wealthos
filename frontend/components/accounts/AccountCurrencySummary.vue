<script setup lang="ts">
import type { AccountCurrencySummaryView } from '~/types/accounts'

defineProps<{
  summary: AccountCurrencySummaryView
}>()
</script>

<template>
  <UiCard class="currency-summary" data-testid="account-currency-summary">
    <header class="currency-summary__header">
      <CurrencyBadge :currency="summary.currency" />
      <span class="currency-summary__label">{{ summary.currency }}</span>
    </header>
    <dl class="currency-summary__grid">
      <div>
        <dt>Activos líquidos</dt>
        <dd>
          <MoneyValue :amount="summary.liquidAssets" :currency="summary.currency" />
        </dd>
      </div>
      <div>
        <dt>Ahorro</dt>
        <dd>
          <MoneyValue :amount="summary.savings" :currency="summary.currency" />
        </dd>
      </div>
      <div>
        <dt>Inversiones</dt>
        <dd>
          <MoneyValue :amount="summary.investments" :currency="summary.currency" />
        </dd>
      </div>
      <div>
        <dt>Pasivos</dt>
        <dd>
          <MoneyValue :amount="summary.liabilities" :currency="summary.currency" />
        </dd>
      </div>
      <div class="currency-summary__net">
        <dt>Patrimonio neto</dt>
        <dd>
          <MoneyValue :amount="summary.netWorth" :currency="summary.currency" />
        </dd>
      </div>
    </dl>
  </UiCard>
</template>

<style scoped>
.currency-summary__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.currency-summary__label {
  font-weight: 700;
  color: var(--color-ink);
}

.currency-summary__grid {
  display: grid;
  gap: var(--space-3);
  margin: 0;
}

.currency-summary__grid dt {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.currency-summary__grid dd {
  margin: 0.15rem 0 0;
  font-size: 1rem;
}

.currency-summary__net {
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.currency-summary__net dd {
  font-size: 1.15rem;
}

@media (min-width: 640px) {
  .currency-summary__grid {
    grid-template-columns: 1fr 1fr;
  }

  .currency-summary__net {
    grid-column: 1 / -1;
  }
}
</style>
