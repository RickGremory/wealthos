<script setup lang="ts">
definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const composer = useTransactionComposerStore()

onMounted(() => {
  composer.openCreate('expense')
  void navigateTo('/app/transactions')
})
</script>

<template>
  <div data-testid="transactions-new-redirect">
    <UiSkeleton style="height: 8rem" />
  </div>
</template>
