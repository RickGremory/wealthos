<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

await navigateTo('/app/commitments', { replace: true })
</script>

<template>
  <div />
</template>
