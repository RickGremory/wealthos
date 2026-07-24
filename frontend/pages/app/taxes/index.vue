<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader
      title="Impuestos"
      description="Perfiles, periodos y reservas fiscales."
    />
    <UiCard>
      <UiEmptyState
        title="Sin perfil fiscal"
        description="Configura un perfil para estimar obligaciones."
      />
    </UiCard>
  </div>
</template>
