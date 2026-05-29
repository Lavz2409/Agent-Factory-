import { useCallback } from 'react'

const API = '/api'

export function useAgent() {
  const runAgent = useCallback(async (agentName: string, input: string, context: Record<string, unknown> = {}) => {
    const res = await fetch(`${API}/agents/${agentName}/run`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ input, context }),
    })
    return res.json()
  }, [])

  const analyzeCode = useCallback(async (files: Record<string, string>, error: string) => {
    const res = await fetch(`${API}/analyze`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ files, error }),
    })
    return res.json()
  }, [])

  return { runAgent, analyzeCode }
}
