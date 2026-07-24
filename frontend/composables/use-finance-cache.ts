/**
 * Lightweight cache invalidation for finance pages.
 * Pages watch version counters and reload when they change.
 */

const accountsVersion = ref(0)
const categoriesVersion = ref(0)
const dashboardVersion = ref(0)
const transactionsVersion = ref(0)
const goalsVersion = ref(0)

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
    transactionsVersion.value += 1
    accountsVersion.value += 1
    dashboardVersion.value += 1
  }

  function invalidateGoals() {
    goalsVersion.value += 1
    dashboardVersion.value += 1
  }

  function invalidateAll() {
    accountsVersion.value += 1
    categoriesVersion.value += 1
    dashboardVersion.value += 1
    transactionsVersion.value += 1
    goalsVersion.value += 1
  }

  return {
    accountsVersion: readonly(accountsVersion),
    categoriesVersion: readonly(categoriesVersion),
    dashboardVersion: readonly(dashboardVersion),
    transactionsVersion: readonly(transactionsVersion),
    goalsVersion: readonly(goalsVersion),
    invalidateAccounts,
    invalidateCategories,
    invalidateDashboard,
    invalidateTransactions,
    invalidateGoals,
    invalidateAll,
  }
}
