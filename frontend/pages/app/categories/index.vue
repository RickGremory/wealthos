<script setup lang="ts">
import type {
  CategoryTreeNodeView,
  CreateCategoryFormModel,
  UpdateCategoryFormModel,
} from '~/types/categories'
import { toUserMessage } from '~/lib/api/errors'

definePageMeta({
  layout: 'app',
  middleware: ['auth', 'organization', 'onboarding'],
})

const { canWrite, canArchive } = useOrganizationPermissions()
// Backend: create = canWrite (member+); update/archive = owner/admin → canArchive
const canEditCategory = canArchive

const {
  filteredTree,
  loading,
  error,
  activeTab,
  submitting,
  parentsFor,
  load,
  create,
  update,
  archive,
} = useCategories()

const toast = useToast()

const modalOpen = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const editingId = ref<string | null>(null)
const formError = ref<string | null>(null)

const createForm = reactive<CreateCategoryFormModel>({
  name: '',
  categoryType: 'expense',
  parentId: null,
  icon: '🛒',
  color: '#0f524e',
})

const editForm = reactive<UpdateCategoryFormModel>({
  name: '',
  icon: '',
  color: '',
})

const archiveOpen = ref(false)
const archiveTarget = ref<CategoryTreeNodeView | null>(null)

const parentOptions = computed(() =>
  parentsFor(
    modalMode.value === 'create' ? createForm.categoryType : 'expense',
    editingId.value ?? undefined,
  ),
)

const modalTitle = computed(() =>
  modalMode.value === 'create' ? 'Nueva categoría' : 'Editar categoría',
)

onMounted(() => {
  void load()
})

watch(activeTab, (tab) => {
  if (tab === 'income' || tab === 'expense') {
    createForm.categoryType = tab
  }
})

function openCreate() {
  modalMode.value = 'create'
  editingId.value = null
  formError.value = null
  createForm.name = ''
  createForm.categoryType = activeTab.value === 'income' ? 'income' : 'expense'
  createForm.parentId = null
  createForm.icon = '🛒'
  createForm.color = '#0f524e'
  modalOpen.value = true
}

function openEdit(node: CategoryTreeNodeView) {
  modalMode.value = 'edit'
  editingId.value = node.id
  formError.value = null
  editForm.name = node.name
  editForm.icon = node.icon ?? ''
  editForm.color = node.color ?? '#0f524e'
  modalOpen.value = true
}

function openArchive(node: CategoryTreeNodeView) {
  archiveTarget.value = node
  archiveOpen.value = true
}

async function submitForm() {
  formError.value = null
  try {
    if (modalMode.value === 'create') {
      if (!createForm.name.trim() || createForm.name.trim().length < 2) {
        formError.value = 'El nombre debe tener al menos 2 caracteres.'
        return
      }
      await create(createForm)
    } else if (editingId.value) {
      if (!editForm.name.trim() || editForm.name.trim().length < 2) {
        formError.value = 'El nombre debe tener al menos 2 caracteres.'
        return
      }
      await update(editingId.value, editForm)
    }
    modalOpen.value = false
  } catch (e) {
    formError.value = toUserMessage(e)
    toast.error('No se pudo guardar', formError.value)
  }
}

async function confirmArchive() {
  if (!archiveTarget.value) return
  try {
    await archive(archiveTarget.value.id)
    archiveOpen.value = false
    archiveTarget.value = null
  } catch (e) {
    toast.error('No se pudo archivar', toUserMessage(e))
  }
}
</script>

<template>
  <div data-testid="categories-page">
    <AppPageHeader
      title="Categorías"
      description="Organiza cómo clasificarás ingresos y gastos al registrar movimientos."
    >
      <template v-if="canWrite" #actions>
        <UiButton type="button" @click="openCreate">
          Nueva categoría
        </UiButton>
      </template>
    </AppPageHeader>

    <CategoryTabs v-model="activeTab" />

    <div class="categories-body">
      <div v-if="loading" class="stack">
        <UiSkeleton height="2.5rem" />
        <UiSkeleton height="2.5rem" />
        <UiSkeleton height="2.5rem" />
      </div>
      <UiAlert v-else-if="error" tone="danger" title="No se pudieron cargar las categorías">
        {{ error }}
      </UiAlert>
      <UiCard v-else>
        <CategoryTree
          :nodes="filteredTree"
          :can-edit="canEditCategory"
          :can-archive="canArchive"
          @edit="openEdit"
          @archive="openArchive"
        />
      </UiCard>
    </div>

    <UiModal v-model:open="modalOpen" :title="modalTitle">
      <UiAlert v-if="formError" tone="danger">
        {{ formError }}
      </UiAlert>
      <CategoryForm
        v-if="modalMode === 'create'"
        v-model:form="createForm"
        mode="create"
        :parent-options="parentOptions"
        :field-error="formError ?? undefined"
        :submitting="submitting"
        @submit="submitForm"
      >
        <template #actions>
          <UiButton
            type="button"
            variant="ghost"
            :disabled="submitting"
            @click="modalOpen = false"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting">
            Crear
          </UiButton>
        </template>
      </CategoryForm>
      <CategoryForm
        v-else
        v-model:form="editForm"
        mode="edit"
        :parent-options="parentOptions"
        :field-error="formError ?? undefined"
        :submitting="submitting"
        @submit="submitForm"
      >
        <template #actions>
          <UiButton
            type="button"
            variant="ghost"
            :disabled="submitting"
            @click="modalOpen = false"
          >
            Cancelar
          </UiButton>
          <UiButton type="submit" :loading="submitting">
            Guardar
          </UiButton>
        </template>
      </CategoryForm>
    </UiModal>

    <ArchiveCategoryDialog
      v-model:open="archiveOpen"
      :category="archiveTarget"
      :loading="submitting"
      @confirm="confirmArchive"
    />
  </div>
</template>

<style scoped>
.categories-body {
  margin-top: var(--space-5);
  min-width: 0;
}

.categories-body :deep(.ui-card) {
  min-width: 0;
  overflow: hidden;
}

.categories-body :deep(.ui-card__body) {
  min-width: 0;
}

@media (max-width: 640px) {
  .categories-body :deep(.ui-card--padded) {
    padding: var(--space-3);
  }
}
</style>
