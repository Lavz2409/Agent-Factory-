import { useRef, useEffect } from 'react'
import { useExecutionStore } from '@/store/executionStore'
import { useLogsStore } from '@/store/logsStore'

export default function TerminalPanel() {
  const { testPassed, errorLog, status } = useExecutionStore()
  const logs = useLogsStore(s => s.logs.filter(l => l.agent === 'TesterAgent'))
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs.length, errorLog])

  return (
    <div className="flex flex-col h-full font-mono bg-[#0a0a14]">
      {/* header bar */}
      <div className="flex items-center gap-2 px-3 py-1.5 border-b border-[#1e1e32] shrink-0">
        <span className="text-[0.6rem] uppercase tracking-widest text-muted">Test Output</span>
        {status !== 'idle' && (
          <span className={[
            'ml-auto text-[0.62rem] px-2 py-0.5 rounded-full border',
            testPassed === true  ? 'text-success border-success/30 bg-success/10' :
            testPassed === false ? 'text-error   border-error/30   bg-error/10'   :
            'text-muted border-[#1e1e32]',
          ].join(' ')}>
            {testPassed === true ? '✓ PASSED' : testPassed === false ? '✗ FAILED' : 'Running…'}
          </span>
        )}
      </div>

      {/* output stream */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 text-[0.68rem] leading-5 space-y-0.5">
        {logs.length === 0 && !errorLog ? (
          <div className="text-muted italic">Test output will appear here…</div>
        ) : (
          logs.map(l => (
            <div
              key={l.id}
              className={
                l.level === 'error'   ? 'text-error'   :
                l.level === 'success' ? 'text-success' :
                l.level === 'warn'    ? 'text-warn'    :
                'text-[#7070a0]'
              }
            >
              {l.message}
            </div>
          ))
        )}

        {errorLog && (
          <div className="mt-2">
            <div className="text-error text-[0.6rem] uppercase tracking-widest mb-1">Error Log</div>
            <pre className="text-error/80 whitespace-pre-wrap text-[0.65rem] bg-error/5 rounded p-2 border border-error/20">
              {errorLog.slice(0, 3000)}
            </pre>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* re-run button placeholder */}
      <div className="px-3 py-2 border-t border-[#1e1e32] shrink-0">
        <button
          className="text-[0.65rem] px-3 py-1 rounded border border-[#1e1e32] text-muted hover:text-text hover:border-accent/30 transition-colors"
          onClick={() => window.location.reload()}
        >
          ↺ Re-run build
        </button>
      </div>
    </div>
  )
}
