import { useEffect, useRef, useState } from 'react'
import { useLogsStore } from '@/store/logsStore'
import type { LogLevel } from '@/types'

const LEVEL_COLOR: Record<LogLevel, string> = {
  info:    'text-[#7070a0]',
  warn:    'text-warn',
  error:   'text-error',
  success: 'text-success',
}

const LEVEL_PREFIX: Record<LogLevel, string> = {
  info:    '  ',
  warn:    '⚠ ',
  error:   '✗ ',
  success: '✓ ',
}

function fmt(ts: number): string {
  const d = new Date(ts * 1000)
  return d.toLocaleTimeString('en', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

export default function LogsPanel() {
  const { filteredLogs, searchTerm, setSearch, clearLogs, filters, setFilter } = useLogsStore()
  const logs      = filteredLogs()
  const bottomRef = useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = useState(true)

  useEffect(() => {
    if (autoScroll) bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs.length, autoScroll])

  const exportLogs = () => {
    const text = logs.map(l => `[${fmt(l.timestamp)}] [${l.agent}] ${l.message}`).join('\n')
    const blob  = new Blob([text], { type: 'text/plain' })
    const a     = document.createElement('a')
    a.href      = URL.createObjectURL(blob)
    a.download  = 'agent-factory.log'
    a.click()
  }

  return (
    <div className="flex flex-col h-full font-mono">
      {/* toolbar */}
      <div className="flex items-center gap-1.5 px-2 py-1.5 border-b border-[#1e1e32] shrink-0 flex-wrap">
        <input
          className="flex-1 min-w-[80px] bg-[#0f0f1e] border border-[#1e1e32] rounded px-2 py-0.5 text-[0.65rem] text-text placeholder-muted outline-none focus:border-accent"
          placeholder="Search…"
          value={searchTerm}
          onChange={e => setSearch(e.target.value)}
        />
        {(['info', 'warn', 'error', 'success'] as LogLevel[]).map(lvl => (
          <button
            key={lvl}
            onClick={() => {
              const active = filters.level.includes(lvl)
              setFilter({ level: active ? filters.level.filter(l => l !== lvl) : [...filters.level, lvl] })
            }}
            className={[
              'text-[0.58rem] px-1.5 py-0.5 rounded border transition-colors',
              filters.level.includes(lvl)
                ? `${LEVEL_COLOR[lvl]} border-current bg-current/10`
                : 'text-muted border-[#1e1e32]',
            ].join(' ')}
          >
            {lvl}
          </button>
        ))}
        <button onClick={exportLogs} title="Export" className="text-muted hover:text-text text-[0.65rem] px-1">↓</button>
        <button onClick={clearLogs}  title="Clear"  className="text-muted hover:text-error text-[0.65rem] px-1">✕</button>
      </div>

      {/* auto-scroll toggle */}
      <div className="flex items-center gap-1 px-2 py-0.5 border-b border-[#1e1e32] shrink-0">
        <label className="flex items-center gap-1 cursor-pointer text-[0.6rem] text-muted">
          <input
            type="checkbox"
            checked={autoScroll}
            onChange={e => setAutoScroll(e.target.checked)}
            className="accent-accent w-2.5 h-2.5"
          />
          Auto-scroll
        </label>
        <span className="ml-auto text-[0.58rem] text-muted">{logs.length} lines</span>
      </div>

      {/* log stream */}
      <div className="flex-1 min-h-0 overflow-y-auto px-2 py-1 space-y-0.5 text-[0.65rem] leading-5">
        {logs.length === 0 ? (
          <div className="text-muted italic mt-4 text-center">Waiting for pipeline…</div>
        ) : (
          logs.map(l => (
            <div key={l.id} className={`flex gap-2 ${LEVEL_COLOR[l.level]}`}>
              <span className="text-[#3a3a5a] shrink-0">{fmt(l.timestamp)}</span>
              <span className="text-muted shrink-0 w-24 truncate">[{l.agent}]</span>
              <span className="break-all">{LEVEL_PREFIX[l.level]}{l.message}</span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
