/**
 * Simple line-level diff generator (no external deps).
 * Returns an array of DiffLine objects suitable for rendering.
 */

export type DiffLineType = 'unchanged' | 'added' | 'removed'

export interface DiffLine {
  type:    DiffLineType
  content: string
  lineNo:  number
}

/** Compute a simple line diff between original and modified strings. */
export function computeDiff(original: string, modified: string): DiffLine[] {
  const origLines = original.split('\n')
  const modLines  = modified.split('\n')

  // Longest common subsequence — O(n*m) but fine for typical file sizes
  const n = origLines.length
  const m = modLines.length
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0))
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      dp[i][j] = origLines[i - 1] === modLines[j - 1]
        ? dp[i - 1][j - 1] + 1
        : Math.max(dp[i - 1][j], dp[i][j - 1])
    }
  }

  const result: DiffLine[] = []
  let i = n, j = m
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && origLines[i - 1] === modLines[j - 1]) {
      result.unshift({ type: 'unchanged', content: origLines[i - 1], lineNo: i })
      i--; j--
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.unshift({ type: 'added',   content: modLines[j - 1],  lineNo: j })
      j--
    } else {
      result.unshift({ type: 'removed', content: origLines[i - 1], lineNo: i })
      i--
    }
  }
  return result
}
