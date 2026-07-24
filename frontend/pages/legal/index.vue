<script setup lang="ts">
definePageMeta({
  layout: 'legal',
})
</script>

<template>
  <article class="legal-index">
    <h1>Información legal</h1>
    <p class="legal-index__lead">
      Documentos públicos de WealthOS. Los textos actuales son borradores pendientes de revisión jurídica.
    </p>
    <ul class="legal-index__list">
      <li>
        <NuxtLink to="/legal/terms">Términos de servicio</NuxtLink>
      </li>
      <li>
        <NuxtLink to="/legal/privacy">Aviso de privacidad</NuxtLink>
      </li>
      <li>
        <NuxtLink to="/legal/cookies">Política de cookies</NuxtLink>
      </li>
    </ul>
  </article>
</template>

<style scoped>
.legal-index h1 {
  font-family: var(--font-display, Georgia, serif);
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  margin: 0 0 var(--space-3, 0.75rem);
}

.legal-index__lead {
  color: var(--color-slate-600, #475569);
  margin: 0 0 var(--space-6, 1.5rem);
}

.legal-index__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: var(--space-3, 0.75rem);
}

.legal-index__list a {
  font-weight: 600;
}
</style>
