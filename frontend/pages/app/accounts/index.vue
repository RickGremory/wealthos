<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})
</script>

<template>
  <div>
    <AppPageHeader
      title="Cuentas"
      description="Activos y pasivos de la organización activa."
    />
    <UiCard>
      <UiEmptyState
        title="Sin cuentas"
        description="Crea tu primera cuenta bancaria, efectivo o tarjeta."
      >
        <template #actions>
          <UiButton type="button" disabled>
            Nueva cuenta (próximo)
          </UiButton>
        </template>
      </UiEmptyState>
    </UiCard>
  </div>
</template>
