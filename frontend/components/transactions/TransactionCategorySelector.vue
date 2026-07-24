<script setup lang="ts">
import { createCategoriesRepository } from '~/repositories/categories.repository'
import type { CategoryTreeNodeView, CategoryType } from '~/types/categories'
import { toUserMessage } from '~/lib/api/errors'

const model = defineModel<string>({ default: '' })

const props = defineProps<{
  categories: CategoryTreeNodeView[]
  categoryType: CategoryType
  label?: string
  error?: string
  disabled?: boolean
  allowQuickCreate?: boolean
}>()

const emit = defineEmits<{
  created: [category: CategoryTreeNodeView]
}>()

const search = ref('')
const showCreate = ref(false)
const createName = ref('')
const creating = ref(false)
const createError = ref<string | null>(null)

interface FlatOption {
  id: string
  label: string
  name: string
}

function flatten(
  nodes: CategoryTreeNodeView[],
  parentName: string | null = null,
  out: FlatOption[] = [],
): FlatOption[] {
  for (const node of nodes) {
    if (node.isArchived) continue
    if (node.type !== props.categoryType) continue
    const label = parentName ? `${parentName} / ${node.name}` : node.name
    out.push({ id: node.id, label, name: node.name })
    if (node.children?.length) flatten(node.children, node.name, out)
  }
  return out
}

const options = computed(() => {
  const q = search.value.trim().toLowerCase()
  const all = flatten(props.categories)
  if (!q) return all
  return all.filter(o => o.label.toLowerCase().includes(q))
})

const selectedLabel = computed(() => {
  const all = flatten(props.categories)
  return all.find(o => o.id === model.value)?.label ?? ''
})

async function quickCreate() {
  const name = createName.value.trim()
  if (name.length < 2) {
    createError.value = 'El nombre debe tener al menos 2 caracteres.'
    return
  }
  const orgId = useOrganizationStore().currentOrganizationId
  if (!orgId) return
  creating.value = true
  createError.value = null
  try {
    const repo = createCategoriesRepository(useNuxtApp().$api)
    const created = await repo.create(orgId, {
      name,
      categoryType: props.categoryType,
    })
    useFinanceCache().invalidateCategories()
    emit('created', created)
    model.value = created.id
    showCreate.value = false
    createName.value = ''
  } catch (e) {
    createError.value = toUserMessage(e)
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <div class="category-selector stack-sm" data-testid="transaction-category-selector">
    <span class="category-selector__label">{{ label || 'Categoría' }}</span>
    <UiInput
      v-model="search"
      placeholder="Buscar categoría…"
      :disabled="disabled"
    />
    <select
      v-model="model"
      class="category-selector__select"
      :disabled="disabled"
      required
    >
      <option value="">
        {{ selectedLabel || 'Selecciona una categoría' }}
      </option>
      <option v-for="opt in options" :key="opt.id" :value="opt.id">
        {{ opt.label }}
      </option>
    </select>
    <p v-if="error" class="field-error">{{ error }}</p>

    <template v-if="allowQuickCreate !== false">
      <button
        type="button"
        class="category-selector__toggle"
        @click="showCreate = !showCreate"
      >
        {{ showCreate ? 'Cancelar' : '+ Nueva categoría' }}
      </button>
      <div v-if="showCreate" class="category-selector__create cluster-sm">
        <UiInput
          v-model="createName"
          placeholder="Nombre"
          :disabled="creating"
        />
        <UiButton
          type="button"
          size="sm"
          :loading="creating"
          @click="quickCreate"
        >
          Crear
        </UiButton>
      </div>
      <p v-if="createError" class="field-error">{{ createError }}</p>
    </template>
  </div>
</template>

<style scoped>
.category-selector__label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-slate-700);
}

.category-selector__select {
  width: 100%;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.category-selector__toggle {
  border: 0;
  background: transparent;
  color: var(--color-teal-800);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0;
  align-self: flex-start;
}

.category-selector__create {
  align-items: flex-end;
}

.field-error {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-danger);
}
</style>
