<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader title="Deudas" description="Saldos, pagos y plan de liquidación." />
    <UiCard>
      <UiEmptyState
        title="Sin deudas registradas"
        description="Agrega créditos o préstamos para ver el resumen."
      />
    </UiCard>
  </div>
</template>
