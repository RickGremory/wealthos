export interface AppNavItem {
  label: string
  to: string
  flag?: 'planning' | 'taxes' | 'debts' | 'goals'
}

export interface AppNavGroup {
  id: string
  label: string
  items: AppNavItem[]
}

export function useAppNav() {
  const { isEnabled } = useFeatureFlags()

  const groups = computed<AppNavGroup[]>(() => {
    const all: AppNavGroup[] = [
      {
        id: 'overview',
        label: 'Overview',
        items: [
          { label: 'Dashboard', to: '/app/dashboard' },
        ],
      },
      {
        id: 'money',
        label: 'Money',
        items: [
          { label: 'Accounts', to: '/app/accounts' },
          { label: 'Transactions', to: '/app/transactions' },
          { label: 'Categories', to: '/app/categories' },
        ],
      },
      {
        id: 'planning',
        label: 'Planning',
        items: [
          { label: 'Budget', to: '/app/planning', flag: 'planning' },
          { label: 'Cash Flow', to: '/app/planning', flag: 'planning' },
          { label: 'Calendar', to: '/app/calendar' },
        ],
      },
      {
        id: 'growth',
        label: 'Growth',
        items: [
          { label: 'Metas', to: '/app/goals', flag: 'goals' },
          { label: 'Obligaciones', to: '/app/commitments', flag: 'debts' },
        ],
      },
      {
        id: 'taxes',
        label: 'Taxes',
        items: [
          { label: 'Taxes', to: '/app/taxes', flag: 'taxes' },
        ],
      },
      {
        id: 'settings',
        label: 'Settings',
        items: [
          { label: 'Settings', to: '/app/settings' },
        ],
      },
    ]

    return all
      .map(group => ({
        ...group,
        items: group.items.filter(item => !item.flag || isEnabled(item.flag)),
      }))
      .filter(group => group.items.length > 0)
  })

  return { groups }
}
