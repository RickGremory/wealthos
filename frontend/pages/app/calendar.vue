<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader
      title="Calendario"
      description="Vencimientos, pagos y hitos."
    />
    <UiCard>
      <UiEmptyState
        title="Calendario vacío"
        description="Aquí verás fechas clave de deudas, impuestos y metas."
      />
    </UiCard>
  </div>
</template>
