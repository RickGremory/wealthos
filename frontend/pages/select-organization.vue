<script setup lang="ts">
definePageMeta({
  layout: 'auth',
  middleware: ['auth', 'legal'],
})

const organization = useOrganizationStore()
const { resolveDestination } = useSessionEntry()
const loading = ref(true)

onMounted(async () => {
  if (!organization.hydrated) {
    await organization.loadMemberships()
  }
  loading.value = false
})

async function choose(organizationId: string) {
  organization.selectOrganization(organizationId)
  const destination = await resolveDestination()
  await navigateTo(destination)
}
</script>

<template>
  <UiCard title="Elige tu organización">
    <div class="stack">
      <p class="text-muted">
        Selecciona con qué espacio financiero quieres trabajar en esta sesión.
      </p>

      <UiAlert v-if="!loading && !organization.memberships.length" tone="warning" title="Sin organizaciones">
        No encontramos organizaciones vinculadas a tu usuario.
      </UiAlert>

      <ul v-if="organization.memberships.length" class="org-list">
        <li v-for="item in organization.memberships" :key="item.id">
          <button type="button" class="org-list__item" @click="choose(item.id)">
            <span class="org-list__name">{{ item.name }}</span>
            <span class="org-list__meta text-muted">{{ item.role }} · {{ item.currency }}</span>
          </button>
        </li>
      </ul>

      <NuxtLink class="org-create" to="/onboarding/organization">
        Crear nueva organización
      </NuxtLink>
    </div>
  </UiCard>
</template>

<style scoped>
.org-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--space-2);
}

.org-list__item {
  width: 100%;
  text-align: left;
  display: grid;
  gap: 0.15rem;
  padding: var(--space-3);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
}

.org-list__item:hover {
  border-color: var(--color-teal-700);
  background: var(--color-teal-50);
}

.org-list__name {
  font-weight: 600;
  color: var(--color-ink);
}

.org-list__meta {
  font-size: 0.8rem;
}

.org-create {
  font-size: 0.9rem;
  font-weight: 600;
}
</style>
