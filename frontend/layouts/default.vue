<template>
  <div class="layout-default">
    <slot />
  </div>
</template>

<style scoped>
.layout-default {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: var(--space-6);
}
</style>
