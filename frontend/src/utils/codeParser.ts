/**
 * Extract fenced code blocks from LLM markdown output.
 * Returns an array of { language, code } pairs.
 */
export function extractCodeBlocks(text: string): { language: string; code: string }[] {
  const regex = /```(\w*)\n([\s\S]*?)```/g
  const results: { language: string; code: string }[] = []
  let match: RegExpExecArray | null
  while ((match = regex.exec(text)) !== null) {
    results.push({ language: match[1] || 'plaintext', code: match[2] })
  }
  return results
}

/** Detect programming language from file extension. */
export function langFromPath(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() ?? ''
  const map: Record<string, string> = {
    py: 'python', ts: 'typescript', tsx: 'typescript',
    js: 'javascript', jsx: 'javascript', json: 'json',
    md: 'markdown', sh: 'shell', css: 'css', html: 'html',
    yaml: 'yaml', yml: 'yaml', txt: 'plaintext',
  }
  return map[ext] ?? 'plaintext'
}

/** Truncate long content for display, adding ellipsis. */
export function truncate(text: string, maxChars = 500): string {
  return text.length > maxChars ? `${text.slice(0, maxChars)}…` : text
}
