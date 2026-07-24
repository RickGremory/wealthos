export type CategoryType = 'income' | 'expense'

export type CategoryTabFilter = 'expense' | 'income' | 'system' | 'archived'

export interface CategoryFilters {
  type?: CategoryType
  includeArchived?: boolean
  tree?: boolean
}

export interface CategoryTreeNodeView {
  id: string
  name: string
  type: CategoryType | string
  icon?: string
  color?: string
  systemCode?: string
  isSystem: boolean
  isArchived: boolean
  parentId?: string | null
  children: CategoryTreeNodeView[]
}

export interface CategoryParentOption {
  id: string
  name: string
  type: CategoryType | string
  depth: number
  label: string
}

export interface CreateCategoryFormModel {
  name: string
  categoryType: CategoryType
  parentId: string | null
  icon: string
  color: string
}

export interface UpdateCategoryFormModel {
  name: string
  icon: string
  color: string
}

export interface CreateCategoryInput {
  name: string
  categoryType: CategoryType
  parentId?: string | null
  icon?: string | null
  color?: string | null
}

export interface UpdateCategoryInput {
  name?: string
  icon?: string | null
  color?: string | null
}
