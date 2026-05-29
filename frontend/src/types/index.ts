// ── Activity log ──────────────────────────────────────────────────────────────

export interface ActivityLogEntry {
  agent:       string
  status:      string
  summary:     string
  full_output: string
  duration:    number
  step:        number
}

// ── Agent types ───────────────────────────────────────────────────────────────

export type AgentName =
  | 'SupervisorAgent'
  | 'PlannerAgent'
  | 'ResearcherAgent'
  | 'ArchitectAgent'
  | 'CoderAgent'
  | 'UIUXAgent'
  | 'IntegrationAgent'
  | 'ScribeAgent'
  | 'MarketingAgent'
  | 'ValidationAgent'
  // | 'TesterAgent'   // DISABLED — ScribeAgent is now the final pipeline step
  | 'DebugAgent'
  | 'ReviewerAgent'

export type AgentStatus = 'idle' | 'running' | 'success' | 'error'

export interface AgentState {
  name: AgentName
  status: AgentStatus
  description: string
  startedAt: number | null
  finishedAt: number | null
  tokenUsage: number
  logs: LogEntry[]
}

// ── Log types ─────────────────────────────────────────────────────────────────

export type LogLevel = 'info' | 'warn' | 'error' | 'success'

export interface LogEntry {
  id: string
  agent: string
  level: LogLevel
  message: string
  timestamp: number
}

// ── Pipeline event (WebSocket payload) ───────────────────────────────────────

export type PipelineEventType =
  | 'agent_start'
  | 'agent_done'
  | 'log'
  | 'file'
  | 'status'
  | 'complete'
  | 'error'
  | 'ping'

export interface PipelineEvent {
  type: PipelineEventType
  agent: string
  data: Record<string, unknown>
  timestamp: number
}

// ── Execution types ───────────────────────────────────────────────────────────

export type ExecutionStatus = 'idle' | 'running' | 'paused' | 'completed' | 'error'

export interface TokenUsage {
  by_agent: Record<string, { prompt_tokens: number; completion_tokens: number; total_tokens: number }>
  totals:   { prompt_tokens: number; completion_tokens: number; total_tokens: number }
  calls:    number
}

export interface DataFlowEvent {
  from: AgentName
  to:   AgentName
  ts:   number
}

export interface ExecutionState {
  runId:        string
  requirement:  string
  status:       ExecutionStatus
  progress:     number   // 0–100
  startTime:    number
  currentAgent: string
  tokenUsage:   TokenUsage | null
  projectName:  string
  outputPath:   string
  testPassed:   boolean | null
  errorLog:     string
  dataFlow:     DataFlowEvent[]
}

// ── Editor types ──────────────────────────────────────────────────────────────

export interface FileEntry {
  path:     string
  content:  string
  language: string
  modified: boolean
}

export interface EditorState {
  files:        Record<string, FileEntry>
  tabs:         string[]
  activeTab:    string
  selectedFile: string | null
}

// ── SupervisorAgent routing result ───────────────────────────────────────────

export interface SupervisorResult {
  pipelines:         string[]
  confidence:        number
  reason:            string
  tools:             string[]
  complexity:        'LOW' | 'MEDIUM' | 'HIGH'
  estimated_modules: string[]
}

// ── ValidationAgent result ───────────────────────────────────────────────────

export interface ValidationResult {
  report:      string    // full Markdown validation report
  reportPath:  string    // absolute path to validation_report.md
  score:       number    // 0 – 10
  ready:       boolean   // production-ready flag
  issues:      string[]  // first 30 issues
}

// ── IntegrationAgent result ──────────────────────────────────────────────────

export interface IntegrationResult {
  guide: string    // full Markdown integration guide
  notes: string[]  // bullet-point integration notes
  files: string[]  // relative paths of generated integration files
}

// ── History ───────────────────────────────────────────────────────────────────

export interface RunRecord {
  id:           string
  requirement:  string
  status:       string
  project_name: string | null
  output_path:  string | null
  test_passed:  number
  created_at:   string
  completed_at: string | null
}
