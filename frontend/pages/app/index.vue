<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

await navigateTo('/app/dashboard')
</script>

<template>
  <div />
</template>
