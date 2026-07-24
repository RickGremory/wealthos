<script setup lang="ts">
defineProps<{
  typeLabel: string
  archived?: boolean
}>()
</script>

<template>
  <UiBadge :tone="archived ? 'neutral' : 'teal'">
    {{ archived ? 'Archivada' : typeLabel }}
  </UiBadge>
</template>
