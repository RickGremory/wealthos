<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader
      title="Planificación"
      description="Presupuesto y asignación de flujo."
    />
    <UiCard>
      <UiEmptyState
        title="Sin plan activo"
        description="La planificación mensual llegará en un sprint siguiente."
      />
    </UiCard>
  </div>
</template>
