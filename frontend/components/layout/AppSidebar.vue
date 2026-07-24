<script setup lang="ts">
defineEmits<{ navigate: [] }>()

const route = useRoute()
const { groups } = useAppNav()
const organization = useOrganizationStore()

function isActive(to: string) {
  return route.path === to || route.path.startsWith(`${to}/`)
}
</script>

<template>
  <aside class="sidebar" aria-label="Navegación principal">
    <div class="sidebar__brand">
      <NuxtLink to="/app/dashboard" class="sidebar__logo" @click="$emit('navigate')">
        WealthOS
      </NuxtLink>
      <p v-if="organization.currentOrganization" class="sidebar__org">
        {{ organization.currentOrganization.name }}
      </p>
    </div>

    <nav class="sidebar__nav">
      <section v-for="group in groups" :key="group.id" class="sidebar__group">
        <h2 class="sidebar__group-label">{{ group.label }}</h2>
        <ul class="sidebar__list">
          <li v-for="item in group.items" :key="item.to">
            <NuxtLink
              :to="item.to"
              class="sidebar__link"
              :class="{ 'sidebar__link--active': isActive(item.to) }"
              @click="$emit('navigate')"
            >
              {{ item.label }}
            </NuxtLink>
          </li>
        </ul>
      </section>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  background: var(--color-ink);
  color: var(--color-text-inverse);
  padding: var(--space-6) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.sidebar__brand {
  padding: 0 var(--space-2);
}

.sidebar__logo {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: inherit;
  text-decoration: none;
}

.sidebar__org {
  margin: var(--space-2) 0 0;
  font-size: 0.8rem;
  color: rgba(248, 250, 252, 0.65);
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  overflow: auto;
}

.sidebar__group-label {
  font-family: var(--font-ui);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(248, 250, 252, 0.45);
  margin: 0 0 var(--space-2);
  padding: 0 var(--space-2);
}

.sidebar__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar__link {
  display: block;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: rgba(248, 250, 252, 0.82);
  text-decoration: none;
  font-weight: 500;
  transition: background 160ms ease, color 160ms ease;
}

.sidebar__link:hover {
  background: rgba(255, 255, 255, 0.06);
  text-decoration: none;
  color: #fff;
}

.sidebar__link--active {
  background: rgba(42, 157, 148, 0.22);
  color: #fff;
}
</style>
