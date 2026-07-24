<script setup lang="ts">
defineProps<{
  title: string
  message: string
}>()
</script>

<template>
  <UiAlert tone="warning" :title="title" data-testid="dashboard-widget-error">
    <p>{{ message }}</p>
  </UiAlert>
</template>
