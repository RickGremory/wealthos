import { describe, expect, it } from 'vitest'
import { presentAccount } from '../../utils/account-type-mapper'

describe('account presentation', () => {
  it('checking muestra saldo disponible (saldo actual)', () => {
    const p = presentAccount({
      accountType: 'checking',
      currentBalance: '1000.00',
      currency: 'MXN',
      isActive: true,
      name: 'Principal',
    })
    expect(p.balanceLabel).toBe('Saldo actual')
    expect(p.balancePresentation).toBe('asset')
  })

  it('credit_card muestra deuda con Debes', () => {
    const p = presentAccount({
      accountType: 'credit_card',
      currentBalance: '-200.00',
      currency: 'MXN',
      isActive: true,
      name: 'Visa',
    })
    expect(p.balancePrefix).toBe('Debes')
    expect(p.displayBalance).toBe('200.00')
  })

  it('loan muestra saldo pendiente', () => {
    const p = presentAccount({
      accountType: 'loan',
      currentBalance: '-50.00',
      currency: 'MXN',
      isActive: true,
      name: 'Auto',
    })
    expect(p.balanceLabel).toBe('Saldo pendiente')
  })

  it('inversión muestra valor actual', () => {
    const p = presentAccount({
      accountType: 'investment',
      currentBalance: '10.00',
      currency: 'USD',
      isActive: true,
      name: 'Broker',
    })
    expect(p.balanceLabel).toBe('Valor actual')
  })

  it('cuenta archivada muestra estado', () => {
    const p = presentAccount({
      accountType: 'cash',
      currentBalance: '5.00',
      currency: 'MXN',
      isActive: false,
      name: 'Caja',
    })
    expect(p.isArchived).toBe(true)
    expect(p.groupLabel).toBe('Archivadas')
  })
})
