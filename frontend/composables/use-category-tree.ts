import type { CategoryTabFilter, CategoryTreeNodeView } from '~/types/categories'
import {
  buildCategoryParentOptions,
  countCategoryNodes,
  filterCategoryTreeByTab,
  flattenCategoryTree,
  hasActiveChildren,
  sanitizeCategoryTree,
  sortCategoryTree,
} from '~/utils/category-tree'

/**
 * Pure tree helpers exposed as a composable for Vue templates.
 * Prefer importing from utils/category-tree in unit tests.
 */
export function useCategoryTree() {
  function filterByTab(nodes: CategoryTreeNodeView[], tab: CategoryTabFilter) {
    return filterCategoryTreeByTab(nodes, tab)
  }

  return {
    filterByTab,
    flatten: flattenCategoryTree,
    sort: sortCategoryTree,
    sanitize: sanitizeCategoryTree,
    buildParentOptions: buildCategoryParentOptions,
    countNodes: countCategoryNodes,
    hasActiveChildren,
  }
}
