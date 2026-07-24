<script setup lang="ts">
withDefaults(
  defineProps<{
    width?: string
    height?: string
    rounded?: boolean
  }>(),
  {
    width: '100%',
    height: '1rem',
    rounded: false,
  },
)
</script>

<template>
  <div
    class="ui-skeleton"
    :class="{ 'ui-skeleton--rounded': rounded }"
    :style="{ width, height }"
    aria-hidden="true"
  />
</template>

<style scoped>
.ui-skeleton {
  background: linear-gradient(
    90deg,
    var(--color-slate-200) 0%,
    var(--color-slate-100) 50%,
    var(--color-slate-200) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: var(--radius-sm);
}

.ui-skeleton--rounded {
  border-radius: 999px;
}

@keyframes shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</style>
