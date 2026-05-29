import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Brain, BarChart3, Terminal as TerminalIcon, Code, Diff, Activity, Upload } from 'lucide-react'
import AgentUniverse  from '@/components/3D/AgentUniverse'
import PromptInput    from '@/components/Input/PromptInput'
import AgentControls  from '@/components/Input/AgentControls'
import CodeUpload     from '@/components/Input/CodeUpload'
import CodeEditor     from '@/components/Editor/CodeEditor'
import FileTabs       from '@/components/Editor/FileTabs'
import FileExplorer   from '@/components/Editor/FileExplorer'
import DiffViewer     from '@/components/Editor/DiffViewer'
import LogsPanel      from '@/components/Panels/LogsPanel'
import ReasoningPanel from '@/components/Panels/ReasoningPanel'
import ObservabilityPanel from '@/components/Panels/ObservabilityPanel'
import TerminalPanel  from '@/components/Panels/TerminalPanel'
import GlassmorphPanel from './GlassmorphPanel'
import ActivityLog    from '@/components/ActivityLog'
import SettingsButton from '@/components/Settings/SettingsButton'
import SettingsPanel  from '@/components/Settings/SettingsPanel'
import { usePipeline } from '@/hooks/usePipeline'
import { useExecutionStore } from '@/store/executionStore'
import { useThemeStore } from '@/store/themeStore'
import { useEffect } from 'react'

type RightTab  = 'logs' | 'reasoning' | 'observability' | 'terminal'
type BottomTab = 'editor' | 'diff'

const RIGHT_TABS: { id: RightTab; label: string; Icon: React.ElementType }[] = [
  { id: 'logs',          label: 'Logs',        Icon: FileText    },
  { id: 'reasoning',     label: 'Reasoning',   Icon: Brain       },
  { id: 'observability', label: 'Observe',     Icon: BarChart3   },
  { id: 'terminal',      label: 'Terminal',    Icon: TerminalIcon },
]

const BOTTOM_TABS: { id: BottomTab; label: string; Icon: React.ElementType }[] = [
  { id: 'editor', label: 'Code', Icon: Code },
  { id: 'diff',   label: 'Diff', Icon: Diff },
]

export default function MainLayout() {
  const [rightTab,        setRightTab]        = useState<RightTab>('logs')
  const [bottomTab,       setBottomTab]       = useState<BottomTab>('editor')
  const [showActivityLog, setShowActivityLog] = useState(false)
  const [showSettings,    setShowSettings]    = useState(false)
  const { run, cancel }   = usePipeline()
  const status            = useExecutionStore(s => s.status)
  const activityLog       = useExecutionStore(s => s.activityLog)
  const initSystemSync    = useThemeStore(s => s.initSystemSync)

  // Listen for OS-level theme changes when the user has selected "System".
  useEffect(() => initSystemSync(), [initSystemSync])

  return (
    <div className="flex flex-col h-screen w-screen bg-bg text-text font-ui overflow-hidden select-none">

      {/* ── top bar ─────────────────────────────────────────────── */}
      <header
        className="flex items-center gap-4 px-5 py-2.5 border-b shrink-0 z-10"
        style={{
          borderColor: 'rgb(var(--c-hairline) / var(--a-hairline))',
          background:  'rgb(var(--c-app-shell) / 0.92)',
          backdropFilter: 'blur(12px)',
        }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-6 h-6 rounded-md flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #06b6d4, #8b5cf6)' }}
          >
            <span className="text-[0.6rem] font-black text-white">AF</span>
          </div>
          <span className="gradient-text font-bold tracking-wide text-sm">AGENT FACTORY</span>
          <span
            className="text-[0.55rem] px-1.5 py-0.5 rounded-full font-medium uppercase tracking-widest"
            style={{ background: 'rgba(99,102,241,0.12)', color: '#818cf8', border: '1px solid rgba(99,102,241,0.2)' }}
          >
            IDE v2.0
          </span>
        </div>

        <div className="ml-auto flex items-center gap-2">
          <StatusBadge status={status} />

          {/* Agent Activity button */}
          <motion.button
            whileHover={activityLog.length > 0 ? { scale: 1.03 } : {}}
            whileTap={activityLog.length > 0 ? { scale: 0.97 } : {}}
            onClick={() => activityLog.length > 0 && setShowActivityLog(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[0.68rem] font-medium transition-all"
            style={{
              background: activityLog.length > 0 ? 'rgba(99,102,241,0.12)' : 'rgba(255,255,255,0.03)',
              color:      activityLog.length > 0 ? '#a78bfa' : '#2d2d4a',
              border:     `1px solid ${activityLog.length > 0 ? 'rgba(99,102,241,0.35)' : 'rgba(255,255,255,0.05)'}`,
              cursor:     activityLog.length > 0 ? 'pointer' : 'not-allowed',
              boxShadow:  activityLog.length > 0 ? '0 0 12px rgba(99,102,241,0.15)' : 'none',
            }}
            title={activityLog.length === 0 ? 'Run the pipeline first' : 'View per-agent execution details'}
          >
            <Activity size={12} />
            Agent Activity
          </motion.button>

          <CodeUpload />

          <SettingsButton
            open={showSettings}
            onClick={() => setShowSettings(v => !v)}
          />
        </div>
      </header>

      {/* ── Settings drawer ─────────────────────────────────────── */}
      <SettingsPanel
        open={showSettings}
        onClose={() => setShowSettings(false)}
      />

      {/* ── Activity Log modal ──────────────────────────────────── */}
      {showActivityLog && (
        <ActivityLog
          activityLog={activityLog}
          onClose={() => setShowActivityLog(false)}
        />
      )}

      {/* ── main grid ───────────────────────────────────────────── */}
      <div className="flex flex-1 min-h-0">

        {/* LEFT — 3D + prompt ──────────────────────────── */}
        <aside
          className="w-72 flex flex-col shrink-0"
          style={{
            borderRight: '1px solid rgb(var(--c-hairline) / var(--a-hairline))',
            background:  'rgb(var(--c-rail))',
          }}
        >
          <div
            className="h-56 shrink-0"
            style={{ borderBottom: '1px solid rgb(var(--c-hairline) / var(--a-hairline))' }}
          >
            <AgentUniverse />
          </div>
          <div className="flex flex-col flex-1 min-h-0 p-3 gap-3 overflow-y-auto">
            <PromptInput onRun={run} running={status === 'running'} />
            <AgentControls running={status === 'running'} onCancel={cancel} />
          </div>
        </aside>

        {/* CENTRE — file explorer + editor ─────────────── */}
        <main className="flex flex-1 min-w-0 flex-col">
          {/* tab switcher */}
          <div
            className="flex border-b shrink-0"
            style={{ borderColor: 'rgb(var(--c-hairline) / var(--a-hairline))' }}
          >
            {BOTTOM_TABS.map(({ id, label, Icon }) => (
              <TabBtn key={id} active={bottomTab === id} onClick={() => setBottomTab(id)} Icon={Icon}>
                {label}
              </TabBtn>
            ))}
          </div>

          <div className="flex flex-1 min-h-0">
            {/* file explorer */}
            <div
              className="w-44 shrink-0 overflow-y-auto"
              style={{ borderRight: '1px solid rgb(var(--c-hairline) / var(--a-hairline))' }}
            >
              <FileExplorer />
            </div>

            {/* editor area */}
            <div className="flex flex-col flex-1 min-w-0">
              <FileTabs />
              <div className="flex-1 min-h-0">
                {bottomTab === 'editor' ? <CodeEditor /> : <DiffViewer />}
              </div>
            </div>
          </div>
        </main>

        {/* RIGHT — logs + panels ────────────────────────── */}
        <aside
          className="w-80 flex flex-col shrink-0"
          style={{
            borderLeft: '1px solid rgb(var(--c-hairline) / var(--a-hairline))',
            background: 'rgb(var(--c-rail))',
          }}
        >
          <div
            className="flex border-b shrink-0"
            style={{ borderColor: 'rgb(var(--c-hairline) / var(--a-hairline))' }}
          >
            {RIGHT_TABS.map(({ id, label, Icon }) => (
              <TabBtn key={id} active={rightTab === id} onClick={() => setRightTab(id)} Icon={Icon}>
                {label}
              </TabBtn>
            ))}
          </div>
          <div className="flex-1 min-h-0 overflow-hidden">
            {rightTab === 'logs'          && <LogsPanel />}
            {rightTab === 'reasoning'     && <ReasoningPanel />}
            {rightTab === 'observability' && <ObservabilityPanel />}
            {rightTab === 'terminal'      && <TerminalPanel />}
          </div>
        </aside>
      </div>
    </div>
  )
}

function TabBtn({
  children, active, onClick, Icon,
}: {
  children: React.ReactNode
  active:   boolean
  onClick:  () => void
  Icon?:    React.ElementType
}) {
  return (
    <button
      onClick={onClick}
      className={`relative px-3 py-2 text-[0.65rem] font-medium uppercase tracking-wider transition-colors flex items-center gap-1.5 ${
        active ? 'text-text' : 'text-textDim'
      }`}
    >
      {Icon && <Icon size={11} style={{ color: active ? '#06b6d4' : 'inherit' }} />}
      {children}
      {active && (
        <motion.div
          layoutId="activeTab"
          className="absolute bottom-0 left-0 right-0 h-0.5 rounded-t"
          style={{ background: 'linear-gradient(90deg, #06b6d4, #3b82f6)' }}
          transition={{ type: 'spring', stiffness: 400, damping: 35 }}
        />
      )}
    </button>
  )
}

function StatusBadge({ status }: { status: string }) {
  const cfg: Record<string, { bg: string; color: string; pulse?: boolean }> = {
    idle:      { bg: 'rgba(255,255,255,0.04)', color: '#3d3d5c' },
    running:   { bg: 'rgba(0,217,255,0.12)',   color: '#22d3ee', pulse: true },
    completed: { bg: 'rgba(34,197,94,0.12)',   color: '#4ade80' },
    error:     { bg: 'rgba(239,68,68,0.12)',   color: '#f87171' },
    paused:    { bg: 'rgba(250,204,21,0.12)',  color: '#fbbf24' },
  }
  const s = cfg[status] ?? cfg.idle
  return (
    <span
      className={`text-[0.58rem] px-2.5 py-1 rounded-full font-semibold uppercase tracking-wider ${s.pulse ? 'animate-pulse' : ''}`}
      style={{ background: s.bg, color: s.color, border: `1px solid ${s.color}30` }}
    >
      {status}
    </span>
  )
}
