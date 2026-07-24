<script setup lang="ts">
const { resolveDestination } = useSessionEntry()

const destination = await resolveDestination()
await navigateTo(destination)
</script>

<template>
  <div />
</template>
