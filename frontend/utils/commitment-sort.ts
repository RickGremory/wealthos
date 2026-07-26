import type { CommitmentListItemView } from '~/types/commitments'
import { isAttentionStatus } from '~/utils/commitment-status'
import { compareDecimalStrings } from '~/utils/decimal-string'

const PRIORITY_RANK: Record<string, number> = { high: 0, medium: 1, low: 2 }

/** attention desc → next due asc → balance desc → created_at desc */
export function sortCommitments(items: CommitmentListItemView[]): CommitmentListItemView[] {
  return [...items].sort((a, b) => {
    const aAtt = isAttentionStatus(a.displayStatus) ? 0 : 1
    const bAtt = isAttentionStatus(b.displayStatus) ? 0 : 1
    if (aAtt !== bAtt) return aAtt - bAtt

    const aDue = a.daysUntilDue ?? 10_000
    const bDue = b.daysUntilDue ?? 10_000
    if (aDue !== bDue) return aDue - bDue

    const bal = compareDecimalStrings(b.currentBalance, a.currentBalance)
    if (bal !== 0) return bal

    const p = (PRIORITY_RANK[a.priority] ?? 1) - (PRIORITY_RANK[b.priority] ?? 1)
    if (p !== 0) return p

    return a.createdAt < b.createdAt ? 1 : -1
  })
}
