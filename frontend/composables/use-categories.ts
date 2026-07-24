import { createCategoriesRepository } from '~/repositories/categories.repository'
import type {
  CategoryTabFilter,
  CategoryTreeNodeView,
  CreateCategoryFormModel,
  UpdateCategoryFormModel,
} from '~/types/categories'
import {
  buildCategoryParentOptions,
  filterCategoryTreeByTab,
  hasActiveChildren,
} from '~/utils/category-tree'
import { toUserMessage } from '~/lib/api/errors'

export function useCategories() {
  const organization = useOrganizationStore()
  const { $api } = useNuxtApp()
  const cache = useFinanceCache()
  const toast = useToast()

  const tree = ref<CategoryTreeNodeView[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const activeTab = ref<CategoryTabFilter>('expense')
  const submitting = ref(false)

  const filteredTree = computed(() =>
    filterCategoryTreeByTab(tree.value, activeTab.value),
  )

  const parentOptions = computed(() =>
    buildCategoryParentOptions(tree.value, {
      categoryType: activeTab.value === 'income' ? 'income' : 'expense',
    }),
  )

  async function load() {
    const orgId = organization.currentOrganizationId
    if (!orgId) {
      error.value = 'Selecciona una organización.'
      tree.value = []
      return
    }

    loading.value = true
    error.value = null
    try {
      const repo = createCategoriesRepository($api)
      tree.value = await repo.list(orgId, {
        includeArchived: true,
        tree: true,
      })
    } catch (e) {
      error.value = toUserMessage(e)
      tree.value = []
    } finally {
      loading.value = false
    }
  }

  function parentsFor(
    categoryType: 'income' | 'expense',
    excludeId?: string,
  ) {
    return buildCategoryParentOptions(tree.value, { categoryType, excludeId })
  }

  async function create(input: CreateCategoryFormModel) {
    const orgId = organization.currentOrganizationId
    if (!orgId) throw new Error('No organization')

    submitting.value = true
    try {
      const repo = createCategoriesRepository($api)
      await repo.create(orgId, {
        name: input.name.trim(),
        categoryType: input.categoryType,
        parentId: input.parentId,
        icon: input.icon || null,
        color: input.color || null,
      })
      cache.invalidateCategories()
      toast.success('Categoría creada', input.name.trim())
      await load()
    } finally {
      submitting.value = false
    }
  }

  async function update(categoryId: string, input: UpdateCategoryFormModel) {
    const orgId = organization.currentOrganizationId
    if (!orgId) throw new Error('No organization')

    submitting.value = true
    try {
      const repo = createCategoriesRepository($api)
      await repo.update(orgId, categoryId, {
        name: input.name.trim(),
        icon: input.icon || null,
        color: input.color || null,
      })
      cache.invalidateCategories()
      toast.success('Categoría actualizada')
      await load()
    } finally {
      submitting.value = false
    }
  }

  async function archive(categoryId: string) {
    const orgId = organization.currentOrganizationId
    if (!orgId) throw new Error('No organization')

    submitting.value = true
    try {
      const repo = createCategoriesRepository($api)
      await repo.archive(orgId, categoryId)
      cache.invalidateCategories()
      toast.success('Categoría archivada')
      await load()
    } finally {
      submitting.value = false
    }
  }

  watch(
    () => cache.categoriesVersion.value,
    () => {
      void load()
    },
  )

  return {
    tree,
    filteredTree,
    loading,
    error,
    activeTab,
    submitting,
    parentOptions,
    parentsFor,
    hasActiveChildren,
    load,
    create,
    update,
    archive,
  }
}
