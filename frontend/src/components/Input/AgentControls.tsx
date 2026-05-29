import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain, Search, Layers, Code2, FileText,
  Bug, CheckCircle, ChevronRight,
} from 'lucide-react'
import { useAgentStore, AGENT_ORDER } from '@/store/agentStore'
import { useExecutionStore } from '@/store/executionStore'
import type { AgentStatus } from '@/types'

interface Props {
  running:  boolean
  onCancel: () => void
}

const AGENT_ICON: Record<string, React.ElementType> = {
  PlannerAgent:    Brain,
  ResearcherAgent: Search,
  ArchitectAgent:  Layers,
  CoderAgent:      Code2,
  ScribeAgent:     FileText,
  DebugAgent:      Bug,
  ReviewerAgent:   CheckCircle,
}

const AGENT_COLOR: Record<string, string> = {
  PlannerAgent:    '#6366f1',
  ResearcherAgent: '#0ea5e9',
  ArchitectAgent:  '#f59e0b',
  CoderAgent:      '#10b981',
  ScribeAgent:     '#a78bfa',
  DebugAgent:      '#f43f5e',
  ReviewerAgent:   '#22d3ee',
}

const STATUS_RING: Record<AgentStatus, string> = {
  idle:    'border-white/10',
  running: 'border-cyan-400/60 agent-running',
  success: 'border-emerald-500/60 agent-success',
  error:   'border-red-500/60 agent-error',
}

const STATUS_BG: Record<AgentStatus, string> = {
  idle:    'bg-white/3',
  running: 'bg-cyan-500/10',
  success: 'bg-emerald-500/10',
  error:   'bg-red-500/10',
}

export default function AgentControls({ running, onCancel }: Props) {
  const { agents }               = useAgentStore()
  const { progress, tokenUsage } = useExecutionStore()
  const totalTokens              = tokenUsage?.totals?.total_tokens ?? 0

  return (
    <div className="flex flex-col gap-3">

      {/* Progress bar */}
      <AnimatePresence>
        {running && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="flex justify-between text-[0.6rem] text-muted mb-1.5">
              <span className="uppercase tracking-widest">Progress</span>
              <span className="text-cyan-400 font-medium">{progress}%</span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
              <motion.div
                className="h-full rounded-full"
                style={{ background: 'linear-gradient(90deg, #06b6d4, #3b82f6, #8b5cf6)' }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Agent pipeline — connected nodes */}
      <div className="flex flex-col gap-1">
        <div className="text-[0.58rem] uppercase tracking-widest text-muted mb-1">Agent Pipeline</div>
        {AGENT_ORDER.map((name, i) => {
          const s    = agents[name].status
          const Icon = AGENT_ICON[name] ?? Brain
          const col  = AGENT_COLOR[name] ?? '#6366f1'
          const isActive = s === 'running'

          return (
            <div key={name}>
              <motion.div
                animate={isActive ? { scale: [1, 1.02, 1] } : { scale: 1 }}
                transition={isActive ? { repeat: Infinity, duration: 2, ease: 'easeInOut' } : {}}
                className={[
                  'flex items-center gap-2.5 px-2.5 py-2 rounded-lg border transition-all duration-300 cursor-default',
                  STATUS_RING[s], STATUS_BG[s],
                ].join(' ')}
              >
                {/* Icon */}
                <div
                  className="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
                  style={{
                    background: s === 'idle' ? 'rgba(255,255,255,0.04)' : `${col}22`,
                    color: s === 'idle' ? '#4a4a6a' : col,
                  }}
                >
                  {s === 'running' ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
                    >
                      <Icon size={12} />
                    </motion.div>
                  ) : s === 'success' ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 400 }}
                    >
                      <CheckCircle size={12} color="#22c55e" />
                    </motion.div>
                  ) : (
                    <Icon size={12} />
                  )}
                </div>

                {/* Name */}
                <span
                  className="text-[0.68rem] font-medium flex-1 truncate"
                  style={{ color: s === 'idle' ? '#4a4a6a' : s === 'running' ? '#e2e8f0' : s === 'success' ? '#86efac' : '#fca5a5' }}
                >
                  {name.replace('Agent', '')}
                </span>

                {/* Status badge */}
                {s !== 'idle' && (
                  <span
                    className="text-[0.55rem] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded-full"
                    style={{
                      background: s === 'running' ? 'rgba(0,217,255,0.12)' : s === 'success' ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
                      color:      s === 'running' ? '#22d3ee' : s === 'success' ? '#4ade80' : '#f87171',
                    }}
                  >
                    {s}
                  </span>
                )}
              </motion.div>

              {/* Connector line between nodes */}
              {i < AGENT_ORDER.length - 1 && (
                <div className="flex justify-center py-0.5">
                  <div
                    className="w-px h-3 transition-all duration-500"
                    style={{
                      background: agents[AGENT_ORDER[i]].status === 'success'
                        ? 'linear-gradient(180deg, #22c55e, #3b82f6)'
                        : 'rgba(255,255,255,0.07)',
                    }}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Controls row */}
      <div className="flex items-center gap-2">
        {running && (
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={onCancel}
            className="flex-1 text-[0.65rem] font-medium px-3 py-1.5 rounded-lg border border-red-500/25 text-red-400 hover:bg-red-500/10 transition-colors"
          >
            ✕ Cancel
          </motion.button>
        )}
        {totalTokens > 0 && (
          <motion.span
            key={totalTokens}
            initial={{ color: '#06b6d4', scale: 1.1 }}
            animate={{ color: '#4a4a6a', scale: 1 }}
            transition={{ duration: 0.6 }}
            className="text-[0.6rem] ml-auto tabular-nums"
          >
            {totalTokens.toLocaleString()} tokens
          </motion.span>
        )}
      </div>
    </div>
  )
}
