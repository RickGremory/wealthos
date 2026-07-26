/**
 * Lightweight cache invalidation for finance pages.
 * Pages watch version counters and reload when they change.
 */

const accountsVersion = ref(0)
const categoriesVersion = ref(0)
const dashboardVersion = ref(0)
const transactionsVersion = ref(0)
const goalsVersion = ref(0)
const commitmentsVersion = ref(0)
const planningVersion = ref(0)
const calendarVersion = ref(0)

export function useFinanceCache() {
  function invalidateAccounts() {
    accountsVersion.value += 1
    dashboardVersion.value += 1
  }

  function invalidateCategories() {
    categoriesVersion.value += 1
  }

  function invalidateDashboard() {
    dashboardVersion.value += 1
  }

  function invalidateTransactions() {
    // Transfers/payments can change liabilities, goals progress, and dashboard.
    transactionsVersion.value += 1
    accountsVersion.value += 1
    dashboardVersion.value += 1
    commitmentsVersion.value += 1
    goalsVersion.value += 1
    planningVersion.value += 1
    calendarVersion.value += 1
  }

  function invalidateGoals() {
    goalsVersion.value += 1
    dashboardVersion.value += 1
  }

  function invalidateCommitments() {
    commitmentsVersion.value += 1
    accountsVersion.value += 1
    dashboardVersion.value += 1
  }

  /** Explicit payment side-effects (same as invalidateTransactions today). */
  function invalidateAfterPayment() {
    invalidateTransactions()
  }

  function invalidateAll() {
    accountsVersion.value += 1
    categoriesVersion.value += 1
    dashboardVersion.value += 1
    transactionsVersion.value += 1
    goalsVersion.value += 1
    commitmentsVersion.value += 1
    planningVersion.value += 1
    calendarVersion.value += 1
  }

  return {
    accountsVersion: readonly(accountsVersion),
    categoriesVersion: readonly(categoriesVersion),
    dashboardVersion: readonly(dashboardVersion),
    transactionsVersion: readonly(transactionsVersion),
    goalsVersion: readonly(goalsVersion),
    commitmentsVersion: readonly(commitmentsVersion),
    planningVersion: readonly(planningVersion),
    calendarVersion: readonly(calendarVersion),
    invalidateAccounts,
    invalidateCategories,
    invalidateDashboard,
    invalidateTransactions,
    invalidateGoals,
    invalidateCommitments,
    invalidateAfterPayment,
    invalidateAll,
  }
}
