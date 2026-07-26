<script setup lang="ts">
defineProps<{
  canWrite?: boolean
}>()

function goNew() {
  return navigateTo('/app/commitments/new')
}
</script>

<template>
  <UiCard data-testid="commitment-empty-state">
    <UiEmptyState
      title="Sin obligaciones todavía"
      description="Registra tarjetas, préstamos u otras deudas vinculadas a una cuenta de pasivo. El saldo siempre viene de la cuenta."
    >
      <template v-if="canWrite" #actions>
        <UiButton type="button" @click="goNew()">
          Nueva obligación
        </UiButton>
      </template>
    </UiEmptyState>
  </UiCard>
</template>
