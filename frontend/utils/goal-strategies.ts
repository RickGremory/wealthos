import type { GoalStrategy } from '~/types/goals'

export interface GoalStrategyOption {
  value: GoalStrategy
  label: string
  description: string
}

export const GOAL_STRATEGY_OPTIONS: GoalStrategyOption[] = [
  {
    value: 'manual',
    label: 'Progreso manual',
    description: 'Tú registras cuánto has ahorrado. Ideal para metas simples o sin cuentas dedicadas.',
  },
  {
    value: 'linked_accounts',
    label: 'Cuentas vinculadas',
    description: 'El avance se calcula con el saldo de las cuentas de activo que elijas (misma moneda).',
  },
  {
    value: 'net_worth_percentage',
    label: 'Patrimonio neto',
    description: 'El progreso refleja el crecimiento de tu patrimonio neto hacia el objetivo.',
  },
]

export function getGoalStrategyLabel(strategy: GoalStrategy): string {
  return GOAL_STRATEGY_OPTIONS.find(o => o.value === strategy)?.label ?? strategy
}

export function getGoalStrategyDescription(strategy: GoalStrategy): string {
  return GOAL_STRATEGY_OPTIONS.find(o => o.value === strategy)?.description ?? ''
}
