<script setup lang="ts">
defineProps<{
  currency: string
}>()
</script>

<template>
  <UiBadge tone="teal">{{ currency }}</UiBadge>
</template>
