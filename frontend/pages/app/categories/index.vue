<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader
      title="Categorías"
      description="Clasificación de ingresos y egresos."
    />
    <UiCard>
      <UiEmptyState
        title="Sin categorías"
        description="Define categorías para organizar tu flujo de dinero."
      />
    </UiCard>
  </div>
</template>
