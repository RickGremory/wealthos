import { describe, expect, it } from 'vitest'
import type { CategoryTreeNodeView } from '../../types/categories'
import {
  buildCategoryParentOptions,
  filterCategoryTreeByTab,
  flattenCategoryTree,
  hasActiveChildren,
  sanitizeCategoryTree,
  sortCategoryTree,
} from '../../utils/category-tree'

function node(
  partial: Partial<CategoryTreeNodeView> & Pick<CategoryTreeNodeView, 'id' | 'name'>,
): CategoryTreeNodeView {
  return {
    type: 'expense',
    isSystem: false,
    isArchived: false,
    children: [],
    ...partial,
  }
}

describe('category-tree', () => {
  const tree: CategoryTreeNodeView[] = [
    node({
      id: 'food',
      name: 'Comida',
      children: [
        node({ id: 'restaurants', name: 'Restaurantes', parentId: 'food' }),
        node({ id: 'groceries', name: 'Súper', parentId: 'food' }),
      ],
    }),
    node({
      id: 'salary',
      name: 'Sueldo',
      type: 'income',
    }),
    node({
      id: 'tax',
      name: 'Impuestos',
      isSystem: true,
      type: 'expense',
      children: [node({ id: 'iva', name: 'IVA', isSystem: true, parentId: 'tax' })],
    }),
  ]

  it('builds hierarchy flatten with depth', () => {
    const flat = flattenCategoryTree(tree)
    expect(flat.map(n => `${n.id}:${n.depth}`)).toContain('food:0')
    expect(flat.map(n => `${n.id}:${n.depth}`)).toContain('restaurants:1')
  })

  it('sorts nodes alphabetically', () => {
    const sorted = sortCategoryTree([
      node({ id: 'b', name: 'Beta' }),
      node({ id: 'a', name: 'Alfa' }),
    ])
    expect(sorted.map(n => n.name)).toEqual(['Alfa', 'Beta'])
  })

  it('avoids cycles defensively', () => {
    const cyclic: CategoryTreeNodeView[] = [
      node({
        id: 'a',
        name: 'A',
        children: [
          node({
            id: 'b',
            name: 'B',
            children: [node({ id: 'a', name: 'A-cycle' })],
          }),
        ],
      }),
    ]
    const clean = sanitizeCategoryTree(cyclic)
    const ids = flattenCategoryTree(clean).map(n => n.id)
    expect(ids.filter(id => id === 'a')).toHaveLength(1)
  })

  it('separates system and custom via tab filter', () => {
    const system = filterCategoryTreeByTab(tree, 'system')
    expect(system.every(n => n.isSystem)).toBe(true)
    expect(system.some(n => n.id === 'tax')).toBe(true)
    expect(flattenCategoryTree(system).every(n => n.isSystem)).toBe(true)

    const expense = filterCategoryTreeByTab(tree, 'expense')
    expect(expense.some(n => n.id === 'food')).toBe(true)
    expect(expense.some(n => n.id === 'tax')).toBe(false)

    const income = filterCategoryTreeByTab(tree, 'income')
    expect(income.map(n => n.id)).toEqual(['salary'])
  })

  it('shows custom children nested under system parents in expense tab', () => {
    const nested: CategoryTreeNodeView[] = [
      node({
        id: 'food-sys',
        name: 'Alimentación',
        isSystem: true,
        children: [
          node({
            id: 'custom-resto',
            name: 'Restaurantes premium',
            parentId: 'food-sys',
            isSystem: false,
          }),
          node({
            id: 'sys-child',
            name: 'IVA comida',
            parentId: 'food-sys',
            isSystem: true,
          }),
        ],
      }),
    ]

    const expense = filterCategoryTreeByTab(nested, 'expense')
    expect(expense.map(n => n.id)).toEqual(['food-sys'])
    expect(expense[0]!.children.map(n => n.id)).toEqual(['custom-resto'])

    const system = filterCategoryTreeByTab(nested, 'system')
    expect(system.map(n => n.id)).toEqual(['food-sys'])
    expect(system[0]!.children.map(n => n.id)).toEqual(['sys-child'])
  })

  it('builds parent options excluding descendants', () => {
    const options = buildCategoryParentOptions(tree, {
      categoryType: 'expense',
      excludeId: 'food',
    })
    expect(options.some(o => o.id === 'food')).toBe(false)
    expect(options.some(o => o.id === 'tax')).toBe(true)
  })

  it('detects active children', () => {
    expect(hasActiveChildren(tree[0]!)).toBe(true)
    expect(hasActiveChildren(node({ id: 'leaf', name: 'Hoja' }))).toBe(false)
  })
})
