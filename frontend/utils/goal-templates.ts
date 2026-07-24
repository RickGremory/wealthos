import type { GoalTemplate } from '~/types/goals'

export const GOAL_TEMPLATES: GoalTemplate[] = [
  {
    id: 'emergency_fund',
    name: 'Fondo de emergencia',
    suggestedTargetAmount: '50000.00',
    emoji: '🛟',
    strategyHint: 'linked_accounts',
    description: '3–6 meses de gastos para imprevistos.',
  },
  {
    id: 'house',
    name: 'Enganche de casa',
    suggestedTargetAmount: '300000.00',
    emoji: '🏠',
    strategyHint: 'linked_accounts',
    description: 'Ahorro hacia el anticipo de tu vivienda.',
  },
  {
    id: 'vacation',
    name: 'Vacaciones',
    suggestedTargetAmount: '25000.00',
    emoji: '✈️',
    strategyHint: 'manual',
    description: 'Viaje o descanso que quieres disfrutar.',
  },
  {
    id: 'car',
    name: 'Auto',
    suggestedTargetAmount: '150000.00',
    emoji: '🚗',
    strategyHint: 'linked_accounts',
    description: 'Enganche o compra de un vehículo.',
  },
  {
    id: 'laptop',
    name: 'Laptop / equipo',
    suggestedTargetAmount: '25000.00',
    emoji: '💻',
    strategyHint: 'manual',
    description: 'Herramientas de trabajo o estudio.',
  },
  {
    id: 'taxes',
    name: 'Reserva de impuestos',
    suggestedTargetAmount: '40000.00',
    emoji: '🧾',
    strategyHint: 'linked_accounts',
    description: 'Aparta lo que vendrá en declaraciones.',
  },
  {
    id: 'retirement',
    name: 'Retiro',
    suggestedTargetAmount: '1000000.00',
    emoji: '🌅',
    strategyHint: 'net_worth_percentage',
    description: 'Patrimonio a largo plazo para tu futuro.',
  },
]

export function getGoalTemplate(id: string): GoalTemplate | undefined {
  return GOAL_TEMPLATES.find(t => t.id === id)
}
