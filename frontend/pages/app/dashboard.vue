<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})

const organization = useOrganizationStore()
const currency = computed(() => organization.currentOrganization?.currency ?? 'MXN')
</script>

<template>
  <div>
    <AppPageHeader
      title="Dashboard"
      description="Vista general de tu patrimonio y flujo de caja."
    />

    <div class="metrics">
      <MetricCard
        label="Patrimonio neto"
        amount="0.00"
        :currency="currency"
        hint="Placeholder — se conectará al resumen real"
      />
      <MetricCard
        label="Disponible"
        amount="0.00"
        :currency="currency"
        hint="Safe-to-spend (próximo)"
      />
      <MetricCard
        label="Variación mes"
      >
        <VarianceIndicator value="0.00" :currency="currency" />
      </MetricCard>
    </div>

    <UiCard title="Actividad reciente" style="margin-top: var(--space-6)">
      <UiEmptyState
        title="Sin movimientos aún"
        description="Cuando registres transacciones, aparecerán aquí."
      />
    </UiCard>
  </div>
</template>

<style scoped>
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
  gap: var(--space-4);
}
</style>
