<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization'],
})

await navigateTo('/app/dashboard')
</script>

<template>
  <div />
</template>
