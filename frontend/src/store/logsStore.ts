import { create } from 'zustand'
import type { LogEntry, LogLevel } from '@/types'

let _id = 0
const uid = () => `log-${++_id}`

const MAX_LOGS = 2000

interface LogFilter {
  level:  LogLevel[]
  agents: string[]
}

interface LogsStore {
  logs:       LogEntry[]
  filters:    LogFilter
  searchTerm: string
  // actions
  addLog:       (entry: Omit<LogEntry, 'id'>) => void
  setFilter:    (filters: Partial<LogFilter>) => void
  setSearch:    (term: string) => void
  clearLogs:    () => void
  filteredLogs: () => LogEntry[]
}

export const useLogsStore = create<LogsStore>((set, get) => ({
  logs:       [],
  filters:    { level: [], agents: [] },
  searchTerm: '',

  addLog: (entry) =>
    set(s => {
      const logs = [...s.logs, { ...entry, id: uid() }]
      return { logs: logs.length > MAX_LOGS ? logs.slice(-MAX_LOGS) : logs }
    }),

  setFilter:  (f)    => set(s => ({ filters: { ...s.filters, ...f } })),
  setSearch:  (term) => set({ searchTerm: term }),
  clearLogs:  ()     => set({ logs: [] }),

  filteredLogs: () => {
    const { logs, filters, searchTerm } = get()
    return logs.filter(l => {
      if (filters.level.length  && !filters.level.includes(l.level))    return false
      if (filters.agents.length && !filters.agents.includes(l.agent))   return false
      if (searchTerm && !l.message.toLowerCase().includes(searchTerm.toLowerCase())) return false
      return true
    })
  },
}))
