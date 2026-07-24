<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader
      title="Movimientos"
      description="Ingresos, gastos y transferencias."
    />
    <UiCard>
      <UiEmptyState
        title="Sin movimientos"
        description="Los movimientos aparecerán cuando empieces a registrar transacciones."
      />
    </UiCard>
  </div>
</template>
