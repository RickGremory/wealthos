<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const {
  loading,
  error,
  view,
  selectedCurrency,
  applyCurrency,
  load,
} = useDashboard()
const currencyWhyOpen = ref(false)

const selectedCommitmentTotal = computed(() => {
  const groups = view.value?.financialCommitments?.totalsByCurrency ?? []
  return groups.find(g => g.currency === selectedCurrency.value) ?? groups[0] ?? null
})

onMounted(() => {
  void load()
})
</script>

<template>
  <div class="dashboard" data-testid="dashboard-page">
    <DashboardHeader
      :greeting="view?.greeting || 'Dashboard'"
      :subtitle="view?.subtitle || 'Así van tus finanzas hoy.'"
    >
      <template #actions>
        <DashboardCurrencySelector
          v-if="view?.availableCurrencies?.length"
          :currencies="view.availableCurrencies"
          :model-value="selectedCurrency"
          @update:model-value="applyCurrency"
        />
      </template>
    </DashboardHeader>

    <div
      v-if="view?.multiCurrency"
      class="dashboard__currency-note"
      data-testid="dashboard-currency-note"
    >
      <p>
        Mostrando información en <strong>{{ selectedCurrency }}</strong>.
        Los importes se muestran por moneda; WealthOS no convierte saldos entre monedas.
        <button
          type="button"
          class="dashboard__why"
          @click="currencyWhyOpen = !currencyWhyOpen"
        >
          ¿Por qué?
        </button>
      </p>
      <p v-if="currencyWhyOpen" class="dashboard__why-body text-muted">
        Cada moneda se calcula por separado para evitar totales imprecisos.
        La conversión de divisas todavía no forma parte del producto.
      </p>
    </div>

    <UiAlert v-if="error" tone="danger" title="No se pudo cargar el dashboard">
      <p>{{ error }}</p>
      <div style="margin-top: 0.75rem">
        <UiButton size="sm" type="button" @click="load">
          Reintentar
        </UiButton>
      </div>
    </UiAlert>

    <div v-if="view?.widgetErrors?.length" class="dashboard__errors stack">
      <DashboardWidgetError
        v-for="item in view.widgetErrors"
        :key="item.id"
        :title="item.title"
        :message="item.message"
      />
    </div>

    <DashboardMetricGrid
      :metrics="view?.metrics || []"
      :loading="loading"
    />

    <OnboardingChecklist
      v-if="view?.onboarding?.isVisible"
      :onboarding="view.onboarding"
    />

    <AttentionPanel
      v-if="view?.attentionItems?.length"
      :items="view.attentionItems"
    />

    <div class="dashboard__mid">
      <DashboardCashFlowCard
        v-if="view?.cashFlow?.status === 'ready'"
        :cash-flow="view.cashFlow"
      />
      <UpcomingFinancialEvents :items="view?.upcoming || []" />
      <RecentTransactions
        :items="view?.recentTransactions || []"
        :loading="loading"
      />
    </div>

    <div v-if="view" class="dashboard__modules">
      <ModuleSummaryCard v-if="view.budget" :summary="view.budget" />
      <ModuleSummaryCard v-if="view.primaryGoal" :summary="view.primaryGoal" />
      <ModuleSummaryCard v-if="view.debtSummary" :summary="view.debtSummary" />
      <ModuleSummaryCard v-if="view.taxSummary" :summary="view.taxSummary" />
    </div>

    <UiCard
      v-if="view?.financialCommitments?.status === 'ready' || view?.financialCommitments?.status === 'empty'"
      :title="`Obligaciones (${selectedCurrency})`"
      class="dashboard__commitments"
    >
      <template v-if="view.financialCommitments.status === 'empty'">
        <p class="text-muted">
          No hay obligaciones activas en {{ selectedCurrency }}.
        </p>
      </template>
      <template v-else>
        <p class="text-muted">
          {{ view.financialCommitments.activeCount }}
          {{ view.financialCommitments.activeCount === 1 ? 'obligación activa' : 'obligaciones activas' }}
          <template v-if="view.financialCommitments.overdueCount">
            · {{ view.financialCommitments.overdueCount }} vencidas
          </template>
        </p>
        <div v-if="selectedCommitmentTotal" class="commitments-pending">
          <span class="text-muted">Saldo pendiente</span>
          <strong>
            <MoneyValue
              :amount="selectedCommitmentTotal.totalObligations"
              :currency="selectedCommitmentTotal.currency"
              :emphasize-sign="false"
            />
          </strong>
        </div>
      </template>
      <div class="cluster" style="margin-top: 0.75rem">
        <UiButton type="button" variant="secondary" @click="navigateTo('/app/commitments')">
          Ver obligaciones
        </UiButton>
      </div>
    </UiCard>
  </div>
</template>

<style scoped>
.dashboard {
  position: relative;
  padding-bottom: var(--space-12);
}

.dashboard__currency-note {
  margin: calc(var(--space-4) * -1) 0 var(--space-5);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--color-surface-muted, rgba(11, 61, 58, 0.04));
  border: 1px solid var(--color-border);
  font-size: 0.88rem;
}

.dashboard__currency-note p {
  margin: 0;
}

.dashboard__why {
  margin-left: 0.35rem;
  border: 0;
  background: transparent;
  color: var(--color-primary);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.dashboard__why-body {
  margin-top: var(--space-2) !important;
  font-size: 0.84rem;
}

.dashboard__errors {
  margin-top: var(--space-4);
}

.dashboard__mid {
  margin-top: var(--space-6);
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-4);
}

.dashboard__modules {
  margin-top: var(--space-6);
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-4);
}

.dashboard__commitments {
  margin-top: var(--space-6);
}

.commitments-pending {
  margin-top: var(--space-3);
  display: grid;
  gap: 0.2rem;
}

.commitments-pending strong {
  font-size: 1.25rem;
  color: var(--color-teal-900);
}

@media (max-width: 1100px) {
  .dashboard__mid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 1000px) {
  .dashboard__mid,
  .dashboard__modules {
    grid-template-columns: 1fr;
  }
}
</style>
