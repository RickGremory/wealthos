import type { ApiClient } from '~/lib/api/types'
import type {
  CategoryFilters,
  CategoryTreeNodeView,
  CreateCategoryInput,
  UpdateCategoryInput,
} from '~/types/categories'
import { sanitizeCategoryTree, sortCategoryTree } from '~/utils/category-tree'

interface CategoryDto {
  id: string
  organization_id: string
  name: string
  category_type: string
  parent_id: string | null
  icon: string | null
  color: string | null
  is_system: boolean
  is_active: boolean
  system_code?: string | null
  created_at?: string
  updated_at?: string
  archived_at?: string | null
  children?: CategoryDto[]
}

interface CategoryListDto {
  items: CategoryDto[]
  total: number
}

function mapNode(dto: CategoryDto): CategoryTreeNodeView {
  return {
    id: dto.id,
    name: dto.name,
    type: dto.category_type,
    icon: dto.icon ?? undefined,
    color: dto.color ?? undefined,
    systemCode: dto.system_code ?? undefined,
    isSystem: dto.is_system,
    isArchived: !dto.is_active,
    parentId: dto.parent_id,
    children: (dto.children ?? []).map(mapNode),
  }
}

function mapFlatToTree(items: CategoryDto[]): CategoryTreeNodeView[] {
  const byId = new Map<string, CategoryTreeNodeView>()
  for (const item of items) {
    byId.set(item.id, { ...mapNode({ ...item, children: [] }), children: [] })
  }

  const roots: CategoryTreeNodeView[] = []
  for (const item of items) {
    const node = byId.get(item.id)!
    if (item.parent_id && byId.has(item.parent_id)) {
      byId.get(item.parent_id)!.children.push(node)
    } else {
      roots.push(node)
    }
  }
  return roots
}

export function createCategoriesRepository(api: ApiClient) {
  return {
    async list(
      organizationId: string,
      filters?: CategoryFilters,
    ): Promise<CategoryTreeNodeView[]> {
      const params = new URLSearchParams()
      if (filters?.type) params.set('type', filters.type)
      if (filters?.includeArchived) params.set('include_archived', 'true')
      if (filters?.tree !== false) params.set('tree', 'true')

      const qs = params.toString()
      const path = `/organizations/${organizationId}/categories${qs ? `?${qs}` : ''}`
      const dto = await api.get<CategoryListDto>(path)
      const items = dto.items ?? []

      const asTree = filters?.tree !== false
      let nodes: CategoryTreeNodeView[]
      if (asTree && items.some(item => Array.isArray(item.children))) {
        nodes = items.map(mapNode)
      } else if (asTree) {
        nodes = mapFlatToTree(items)
      } else {
        nodes = items.map(item => mapNode({ ...item, children: [] }))
      }

      return sortCategoryTree(sanitizeCategoryTree(nodes))
    },

    async create(
      organizationId: string,
      input: CreateCategoryInput,
    ): Promise<CategoryTreeNodeView> {
      const dto = await api.post<CategoryDto>(
        `/organizations/${organizationId}/categories`,
        {
          name: input.name,
          category_type: input.categoryType,
          parent_id: input.parentId ?? null,
          icon: input.icon ?? null,
          color: input.color ?? null,
        },
      )
      return mapNode({ ...dto, children: [] })
    },

    async update(
      organizationId: string,
      categoryId: string,
      input: UpdateCategoryInput,
    ): Promise<CategoryTreeNodeView> {
      const body: Record<string, unknown> = {}
      if (input.name !== undefined) body.name = input.name
      if (input.icon !== undefined) body.icon = input.icon
      if (input.color !== undefined) body.color = input.color

      const dto = await api.patch<CategoryDto>(
        `/organizations/${organizationId}/categories/${categoryId}`,
        body,
      )
      return mapNode({ ...dto, children: [] })
    },

    async archive(
      organizationId: string,
      categoryId: string,
    ): Promise<CategoryTreeNodeView> {
      const dto = await api.post<CategoryDto>(
        `/organizations/${organizationId}/categories/${categoryId}/archive`,
        {},
      )
      return mapNode({ ...dto, children: [] })
    },
  }
}

export type CategoriesRepository = ReturnType<typeof createCategoriesRepository>
