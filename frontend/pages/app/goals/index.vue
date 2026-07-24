<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader title="Metas" description="Objetivos de ahorro y progreso." />
    <UiCard>
      <UiEmptyState
        title="Sin metas"
        description="Define una meta para empezar a medir avance."
      />
    </UiCard>
  </div>
</template>
