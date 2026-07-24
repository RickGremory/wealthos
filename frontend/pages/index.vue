<script setup lang="ts">
const auth = useAuthStore()

await navigateTo(auth.isAuthenticated ? '/app' : '/login')
</script>

<template>
  <div />
</template>
