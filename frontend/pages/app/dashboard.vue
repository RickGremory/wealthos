<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const preferences = usePreferencesStore()
const { loading, error, view, load } = useDashboard()
const cache = useFinanceCache()
const composer = useTransactionComposerStore()
const { canWrite } = useOrganizationPermissions()

function openNewTransaction() {
  composer.openCreate('expense')
}

onMounted(() => {
  void load()
})

watch(
  () => useOrganizationStore().currentOrganizationId,
  () => {
    void load()
  },
)

watch(
  () => cache.dashboardVersion.value,
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
          v-if="canWrite"
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

@media (max-width: 1000px) {
  .dashboard__mid,
  .dashboard__modules {
    grid-template-columns: 1fr;
  }
}
</style>
