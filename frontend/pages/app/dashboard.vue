<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})

const preferences = usePreferencesStore()
const { loading, error, view, load } = useDashboard()

onMounted(() => {
  void load()
})

watch(
  () => useOrganizationStore().currentOrganizationId,
  () => {
    void load()
  },
)
</script>

<template>
  <div class="dashboard" data-testid="dashboard-page">
    <DashboardHeader
      :greeting="view?.greeting || 'Dashboard'"
      :subtitle="view?.subtitle || 'Así están tus finanzas hoy.'"
    >
      <template #actions>
        <UiButton
          variant="ghost"
          size="sm"
          type="button"
          @click="preferences.toggleHideBalances()"
        >
          {{ preferences.hideBalances ? 'Mostrar montos' : 'Ocultar montos' }}
        </UiButton>
        <UiButton
          variant="primary"
          size="sm"
          type="button"
          @click="navigateTo('/app/transactions')"
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

    <DashboardMetricGrid
      :metrics="view?.metrics || []"
      :loading="loading"
    />

    <OnboardingChecklist
      v-if="view && !view.onboarding.completed"
      :onboarding="view.onboarding"
    />

    <AttentionPanel
      v-if="view?.attentionItems?.length"
      :items="view.attentionItems"
    />

    <div class="dashboard__mid">
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

    <button
      type="button"
      class="dashboard__fab"
      aria-label="Nueva transacción"
      @click="navigateTo('/app/transactions')"
    >
      +
    </button>
  </div>
</template>

<style scoped>
.dashboard {
  position: relative;
  padding-bottom: var(--space-12);
}

.dashboard__mid {
  margin-top: var(--space-6);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.dashboard__modules {
  margin-top: var(--space-6);
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-4);
}

.dashboard__fab {
  display: none;
  position: fixed;
  right: 1.25rem;
  bottom: 1.25rem;
  width: 3.25rem;
  height: 3.25rem;
  border: 0;
  border-radius: 999px;
  background: var(--color-primary);
  color: white;
  font-size: 1.75rem;
  line-height: 1;
  box-shadow: var(--shadow-lg);
  cursor: pointer;
  z-index: 30;
}

@media (max-width: 1000px) {
  .dashboard__mid,
  .dashboard__modules {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .dashboard__fab {
    display: inline-grid;
    place-items: center;
  }
}
</style>
