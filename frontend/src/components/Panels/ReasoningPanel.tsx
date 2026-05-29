import { useAgentStore, AGENT_ORDER } from '@/store/agentStore'
import type { AgentName, AgentStatus } from '@/types'

const STATUS_BADGE: Record<AgentStatus, string> = {
  idle:    'text-muted border-muted/30',
  running: 'text-accent border-accent/40 bg-accent/10 animate-pulse',
  success: 'text-success border-success/30 bg-success/5',
  error:   'text-error border-error/30 bg-error/5',
}

const STATUS_DOT: Record<AgentStatus, string> = {
  idle:    'bg-muted',
  running: 'bg-accent animate-pulse',
  success: 'bg-success',
  error:   'bg-error',
}

function duration(start: number | null, end: number | null): string {
  if (!start) return '—'
  const ms = (end ?? Date.now()) - start
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`
}

export default function ReasoningPanel() {
  const { agents, activeAgent, setActiveAgent } = useAgentStore()
  const selected = activeAgent ?? (AGENT_ORDER.find(n => agents[n].status === 'running') ?? null)

  return (
    <div className="flex flex-col h-full">
      {/* agent selector */}
      <div className="flex overflow-x-auto border-b border-[#1e1e32] shrink-0 scrollbar-none">
        {AGENT_ORDER.map(name => {
          const s = agents[name].status
          return (
            <button
              key={name}
              onClick={() => setActiveAgent(name === selected ? null : name as AgentName)}
              className={[
                'flex items-center gap-1.5 px-3 py-2 shrink-0 border-r border-[#1e1e32]',
                'text-[0.62rem] transition-colors',
                name === selected ? 'bg-[#0f0f1e]' : 'hover:bg-[#1a1a2e]',
              ].join(' ')}
            >
              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${STATUS_DOT[s]}`} />
              <span className={name === selected ? 'text-text' : 'text-muted'}>
                {name.replace('Agent', '')}
              </span>
            </button>
          )
        })}
      </div>

      {/* agent detail */}
      {selected ? (
        <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3 text-[0.7rem]">
          {/* header */}
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded border ${STATUS_BADGE[agents[selected].status]}`}>
            <span className={`w-2 h-2 rounded-full ${STATUS_DOT[agents[selected].status]}`} />
            <span className="font-semibold">{selected}</span>
            <span className="ml-auto text-[0.62rem]">{agents[selected].status.toUpperCase()}</span>
          </div>

          {/* timing */}
          <div className="grid grid-cols-2 gap-2">
            <Metric label="Duration" value={duration(agents[selected].startedAt, agents[selected].finishedAt)} />
            <Metric label="Tokens"   value={agents[selected].tokenUsage.toLocaleString()} />
          </div>

          {/* description */}
          <div className="text-muted italic">{agents[selected].description}</div>

          {/* logs for this agent */}
          <div>
            <div className="text-[0.6rem] uppercase tracking-widest text-muted mb-1">Agent Logs</div>
            {agents[selected].logs.length === 0 ? (
              <div className="text-muted italic text-[0.65rem]">No logs yet.</div>
            ) : (
              <div className="space-y-0.5 font-mono text-[0.65rem]">
                {agents[selected].logs.slice(-50).map((l, i) => (
                  <div key={i} className={
                    l.level === 'error'   ? 'text-error'   :
                    l.level === 'success' ? 'text-success' :
                    l.level === 'warn'    ? 'text-warn'    :
                    'text-textDim'
                  }>
                    {l.message}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center text-muted text-[0.72rem]">
          Click an agent to inspect its reasoning
        </div>
      )}
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-[#0f0f1e] border border-[#1e1e32] rounded-lg p-2 text-center">
      <div className="text-text font-semibold">{value}</div>
      <div className="text-muted text-[0.6rem] uppercase tracking-wider">{label}</div>
    </div>
  )
}
