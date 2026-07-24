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
          { label: 'Cuentas', to: '/app/accounts' },
          { label: 'Movimientos', to: '/app/transactions' },
          { label: 'Categorías', to: '/app/categories' },
        ],
      },
      {
        id: 'plan',
        label: 'Plan',
        items: [
          { label: 'Presupuesto', to: '/app/planning', flag: 'planning' },
          { label: 'Flujo de caja', to: '/app/planning', flag: 'planning' },
          { label: 'Calendario', to: '/app/calendar' },
        ],
      },
      {
        id: 'grow',
        label: 'Grow',
        items: [
          { label: 'Metas', to: '/app/goals', flag: 'goals' },
          { label: 'Deudas', to: '/app/debts', flag: 'debts' },
        ],
      },
      {
        id: 'taxes',
        label: 'Taxes',
        items: [
          { label: 'Impuestos', to: '/app/taxes', flag: 'taxes' },
        ],
      },
      {
        id: 'settings',
        label: 'Settings',
        items: [
          { label: 'Ajustes', to: '/app/settings' },
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
