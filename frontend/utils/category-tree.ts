import type { CategoryTreeNodeView, CategoryParentOption, CategoryType } from '~/types/categories'

export function flattenCategoryTree(
  nodes: CategoryTreeNodeView[],
  depth = 0,
): Array<CategoryTreeNodeView & { depth: number }> {
  const result: Array<CategoryTreeNodeView & { depth: number }> = []
  for (const node of nodes) {
    result.push({ ...node, depth })
    if (node.children?.length) {
      result.push(...flattenCategoryTree(node.children, depth + 1))
    }
  }
  return result
}

/** Sort tree nodes alphabetically by name (recursive). */
export function sortCategoryTree(nodes: CategoryTreeNodeView[]): CategoryTreeNodeView[] {
  return [...nodes]
    .map(node => ({
      ...node,
      children: sortCategoryTree(node.children ?? []),
    }))
    .sort((a, b) => a.name.localeCompare(b.name, 'es'))
}

/**
 * Build parent select options from a tree.
 * Excludes the node itself and its descendants (when editing).
 * Only depth-0 nodes can be parents (backend max depth = 2).
 */
export function buildCategoryParentOptions(
  nodes: CategoryTreeNodeView[],
  options?: {
    categoryType?: CategoryType | string
    excludeId?: string
  },
): CategoryParentOption[] {
  const exclude = new Set<string>()
  if (options?.excludeId) {
    const flat = flattenCategoryTree(nodes)
    const target = flat.find(n => n.id === options.excludeId)
    if (target) {
      exclude.add(target.id)
      const collect = (children: CategoryTreeNodeView[]) => {
        for (const child of children) {
          exclude.add(child.id)
          collect(child.children ?? [])
        }
      }
      collect(target.children ?? [])
    }
  }

  const result: CategoryParentOption[] = []

  for (const node of nodes) {
    if (exclude.has(node.id)) continue
    if (node.isArchived) continue
    if (options?.categoryType && node.type !== options.categoryType) continue

    // Only roots (or depth 0) can be parents — children already at max depth.
    result.push({
      id: node.id,
      name: node.name,
      type: node.type,
      depth: 0,
      label: node.name,
    })
  }

  return result.sort((a, b) => a.label.localeCompare(b.label, 'es'))
}

export function filterCategoryTreeByTab(
  nodes: CategoryTreeNodeView[],
  tab: 'expense' | 'income' | 'system' | 'archived',
): CategoryTreeNodeView[] {
  if (tab === 'archived') {
    return filterArchivedOnly(nodes)
  }

  if (tab === 'system') {
    // Only system categories (seeded). Custom children belong in Gasto/Ingreso.
    const filterSystem = (list: CategoryTreeNodeView[]): CategoryTreeNodeView[] =>
      list
        .filter(node => !node.isArchived && node.isSystem)
        .map(node => ({
          ...node,
          children: filterSystem(node.children ?? []),
        }))
    return filterSystem(nodes)
  }

  // Gasto / Ingreso: user categories, including those nested under a system parent.
  // Keep system ancestors only as structural shells when they wrap custom descendants.
  const wantedType = tab

  const hasVisibleCustom = (node: CategoryTreeNodeView): boolean => {
    if (node.isArchived || node.type !== wantedType) return false
    if (!node.isSystem) return true
    return (node.children ?? []).some(hasVisibleCustom)
  }

  const filterTyped = (list: CategoryTreeNodeView[]): CategoryTreeNodeView[] =>
    list
      .filter((node) => {
        if (node.isArchived || node.type !== wantedType) return false
        if (!node.isSystem) return true
        return hasVisibleCustom(node)
      })
      .map(node => ({
        ...node,
        children: filterTyped(node.children ?? []),
      }))
      .filter(node => !node.isSystem || (node.children?.length ?? 0) > 0)

  return filterTyped(nodes)
}

function filterArchivedOnly(nodes: CategoryTreeNodeView[]): CategoryTreeNodeView[] {
  const result: CategoryTreeNodeView[] = []
  for (const node of nodes) {
    const children = filterArchivedOnly(node.children ?? [])
    if (node.isArchived) {
      result.push({ ...node, children })
    } else if (children.length) {
      // Keep structure if descendants are archived
      result.push({ ...node, children, isArchived: false })
    }
  }
  return result
}

/** Defensive: drop children that would create a cycle (id already in ancestors). */
export function sanitizeCategoryTree(
  nodes: CategoryTreeNodeView[],
  ancestors: Set<string> = new Set(),
): CategoryTreeNodeView[] {
  return nodes
    .filter(node => !ancestors.has(node.id))
    .map((node) => {
      const next = new Set(ancestors)
      next.add(node.id)
      return {
        ...node,
        children: sanitizeCategoryTree(node.children ?? [], next),
      }
    })
}

export function countCategoryNodes(nodes: CategoryTreeNodeView[]): number {
  return flattenCategoryTree(nodes).length
}

export function hasActiveChildren(node: CategoryTreeNodeView): boolean {
  return (node.children ?? []).some(child => !child.isArchived)
}
