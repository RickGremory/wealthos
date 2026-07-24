<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['auth'],
})

const { resolveDestination } = useSessionEntry()

const destination = await resolveDestination()
await navigateTo(destination)
</script>

<template>
  <div />
</template>
