import { describe, expect, it } from 'vitest'
import {
  ACCOUNT_TYPE_OPTIONS,
  presentAccount,
  toBackendAccountType,
  toOpeningBalancePayload,
  toSimplifiedAccountType,
} from '../../utils/account-type-mapper'

describe('account-type-mapper', () => {
  it('exposes all eight account types', () => {
    const values = ACCOUNT_TYPE_OPTIONS.map(o => o.value)
    expect(values).toEqual([
      'checking',
      'cash',
      'digital_wallet',
      'savings',
      'investment',
      'credit_card',
      'loan',
      'other',
    ])
  })

  it('maps simplified types to backend types', () => {
    expect(toBackendAccountType('checking')).toBe('checking')
    expect(toBackendAccountType('credit_card')).toBe('credit_card')
    expect(toBackendAccountType('other')).toBe('other')
  })

  it('maps backend types back to simplified types', () => {
    expect(toSimplifiedAccountType('savings')).toBe('savings')
    expect(toSimplifiedAccountType('investment')).toBe('other')
    expect(toSimplifiedAccountType('loan')).toBe('other')
    expect(toSimplifiedAccountType('unknown')).toBe('other')
  })

  it('keeps asset opening balances as positive decimal strings', () => {
    expect(toOpeningBalancePayload('checking', '1500.50')).toBe('1500.50')
    expect(toOpeningBalancePayload('cash', '100')).toBe('100.00')
    expect(toOpeningBalancePayload('investment', '42.5')).toBe('42.5')
  })

  it('sends negative opening_balance for credit card debt entered as positive', () => {
    expect(toOpeningBalancePayload('credit_card', '2500.00')).toBe('-2500.00')
    expect(toOpeningBalancePayload('credit_card', '800')).toBe('-800.00')
  })

  it('sends negative opening_balance for loan debt entered as positive', () => {
    expect(toOpeningBalancePayload('loan', '126000.00')).toBe('-126000.00')
    expect(toOpeningBalancePayload('loan', '500')).toBe('-500.00')
  })

  it('keeps zero credit card and loan balances at 0.00', () => {
    expect(toOpeningBalancePayload('credit_card', '0')).toBe('0.00')
    expect(toOpeningBalancePayload('loan', '0.00')).toBe('0.00')
  })
})

describe('presentAccount', () => {
  it('presents checking as asset with saldo actual', () => {
    const view = presentAccount({
      accountType: 'checking',
      currentBalance: '28450.00',
      currency: 'MXN',
      isActive: true,
      institutionName: 'HSBC',
      name: 'Cuenta principal',
    })
    expect(view.balancePresentation).toBe('asset')
    expect(view.balanceLabel).toBe('Saldo actual')
    expect(view.displayBalance).toBe('28450.00')
    expect(view.balancePrefix).toBeNull()
    expect(view.group).toBe('cash_banks')
    expect(view.isLiquid).toBe(true)
  })

  it('presents credit_card with Debes prefix', () => {
    const view = presentAccount({
      accountType: 'credit_card',
      currentBalance: '-8500.00',
      currency: 'MXN',
      isActive: true,
      name: 'Tarjeta NU',
    })
    expect(view.balancePresentation).toBe('liability')
    expect(view.balancePrefix).toBe('Debes')
    expect(view.displayBalance).toBe('8500.00')
    expect(view.group).toBe('credit_debts')
  })

  it('presents loan with saldo pendiente and no Debes prefix', () => {
    const view = presentAccount({
      accountType: 'loan',
      currentBalance: '-126000.00',
      currency: 'MXN',
      isActive: true,
      name: 'Crédito automotriz',
    })
    expect(view.balanceLabel).toBe('Saldo pendiente')
    expect(view.balancePrefix).toBeNull()
    expect(view.displayBalance).toBe('126000.00')
  })

  it('presents investment with valor actual', () => {
    const view = presentAccount({
      accountType: 'investment',
      currentBalance: '42000.00',
      currency: 'MXN',
      isActive: true,
      name: 'CETES',
    })
    expect(view.balanceLabel).toBe('Valor actual')
    expect(view.group).toBe('investments')
    expect(view.isLiquid).toBe(false)
  })

  it('marks archived accounts', () => {
    const view = presentAccount({
      accountType: 'checking',
      currentBalance: '100.00',
      currency: 'MXN',
      isActive: false,
      name: 'Vieja',
    })
    expect(view.isArchived).toBe(true)
    expect(view.group).toBe('archived')
    expect(view.isLiquid).toBe(false)
  })
})
