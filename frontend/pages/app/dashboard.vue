<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const preferences = usePreferencesStore()
const {
  loading,
  error,
  view,
  selectedCurrency,
  applyCurrency,
  load,
} = useDashboard()
const composer = useTransactionComposerStore()
const { canWrite } = useOrganizationPermissions()

function openNewTransaction() {
  composer.openCreate('expense')
}

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
        <UiButton
          class="hide-on-mobile"
          variant="ghost"
          size="sm"
          type="button"
          @click="preferences.toggleHideBalances()"
        >
          {{ preferences.hideBalances ? 'Mostrar montos' : 'Ocultar montos' }}
        </UiButton>
        <UiButton
          v-if="canWrite"
          class="hide-on-mobile"
          variant="primary"
          size="sm"
          type="button"
          @click="openNewTransaction"
        >
          + Nueva transacción
        </UiButton>
      </template>
    </DashboardHeader>

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
      v-if="view?.financialCommitments?.status === 'ready'"
      title="Obligaciones"
      class="dashboard__commitments"
    >
      <p class="text-muted">
        {{ view.financialCommitments.activeCount }} activas
        <template v-if="view.financialCommitments.overdueCount">
          · {{ view.financialCommitments.overdueCount }} vencidas
        </template>
      </p>
      <ul
        v-if="view.financialCommitments.totalsByCurrency.length"
        class="commitments-totals"
      >
        <li
          v-for="group in view.financialCommitments.totalsByCurrency"
          :key="group.currency"
        >
          <CurrencyBadge :currency="group.currency" />
          <MoneyValue
            :amount="group.totalObligations"
            :currency="group.currency"
            :emphasize-sign="false"
          />
        </li>
      </ul>
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

.commitments-totals {
  list-style: none;
  margin: var(--space-3) 0 0;
  padding: 0;
  display: grid;
  gap: var(--space-2);
}

.commitments-totals li {
  display: flex;
  gap: var(--space-2);
  align-items: center;
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
