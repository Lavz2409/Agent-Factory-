import { useState, useCallback, useRef } from 'react'
import type {
  PipelineEvent, AgentName, TokenUsage, ActivityLogEntry,
  SupervisorResult, ValidationResult, IntegrationResult,
} from '@/types'
import { useWebSocket } from './useWebSocket'
import { useAgentStore, AGENT_ORDER } from '@/store/agentStore'
import { useEditorStore } from '@/store/editorStore'
import { useExecutionStore } from '@/store/executionStore'
import { useLogsStore } from '@/store/logsStore'

const API = '/api'

// Map full agent class name → short display name used in ActivityLog
const DISPLAY_NAME: Record<string, string> = {
  SupervisorAgent:  'Supervisor',
  PlannerAgent:     'Planner',
  ResearcherAgent:  'Researcher',
  ArchitectAgent:   'Architect',
  CoderAgent:       'Coder',
  UIUXAgent:        'UI/UX',
  IntegrationAgent: 'Integration',
  ScribeAgent:      'Scribe',
  MarketingAgent:   'Marketing',
  ValidationAgent:  'Validation',
}

export function usePipeline() {
  const [wsUrl, setWsUrl] = useState<string | null>(null)
  const { close: closeWs } = useWebSocket(wsUrl, { onEvent: handleEvent })

  const agentStore     = useAgentStore()
  const editorStore    = useEditorStore()
  const executionStore = useExecutionStore()
  const logsStore      = useLogsStore()

  // ── Client-side activity log accumulation ──────────────────────────────────
  // Built from agent_start / log / agent_done events so the button works
  // even if the backend's complete payload has an empty activity_log.
  const agentStartTs   = useRef<Record<string, number>>({})
  const agentLogLines  = useRef<Record<string, string[]>>({})
  const clientActLog   = useRef<ActivityLogEntry[]>([])

  // Resolve agents that finished before current one
  const markPreviousDone = useCallback((currentAgent: string) => {
    const idx = AGENT_ORDER.indexOf(currentAgent as AgentName)
    AGENT_ORDER.slice(0, idx).forEach(name => {
      const s = agentStore.agents[name].status
      if (s !== 'success' && s !== 'error') agentStore.setAgentStatus(name, 'success')
    })
  }, [agentStore])

  // ── WebSocket event handler ─────────────────────────────────────────────────

  function handleEvent(event: PipelineEvent) {
    const agent = event.agent as AgentName

    switch (event.type) {

      case 'agent_start':
        agentStore.setAgentStatus(agent, 'running')
        agentStore.setActiveAgent(agent)
        executionStore.setCurrentAgent(event.agent)
        markPreviousDone(event.agent)
        // Start timing for this agent
        agentStartTs.current[event.agent]  = Date.now()
        agentLogLines.current[event.agent] = []
        break

      case 'agent_done': {
        agentStore.setAgentStatus(agent, 'success')
        // Build an activity log entry from accumulated log lines + timing
        const startMs   = agentStartTs.current[event.agent] ?? Date.now()
        const duration  = Math.round((Date.now() - startMs) / 100) / 10
        const lines     = agentLogLines.current[event.agent] ?? []
        const stepIdx   = AGENT_ORDER.indexOf(event.agent as AgentName)
        clientActLog.current.push({
          agent:       DISPLAY_NAME[event.agent] ?? event.agent.replace('Agent', ''),
          status:      'success',
          summary:     lines[lines.length - 1] ?? `${event.agent} completed`,
          full_output: lines.join('\n') || `${event.agent} completed in ${duration}s`,
          duration,
          step:        stepIdx >= 0 ? stepIdx + 1 : clientActLog.current.length + 1,
        })
        break
      }

      case 'log': {
        const d = event.data as { message: string; level: string }
        const entry = {
          agent:     event.agent,
          level:     (d.level ?? 'info') as import('@/types').LogLevel,
          message:   d.message ?? '',
          timestamp: event.timestamp,
        }
        logsStore.addLog(entry)
        if (AGENT_ORDER.includes(agent)) agentStore.addAgentLog(agent, { ...entry, id: '' })
        // Accumulate for activity log
        if (event.agent && event.agent !== 'pipeline') {
          if (!agentLogLines.current[event.agent]) agentLogLines.current[event.agent] = []
          agentLogLines.current[event.agent].push(d.message ?? '')
        }
        break
      }

      case 'file': {
        const d = event.data as { filename: string; content: string }
        if (d.filename) editorStore.addFile(d.filename, d.content ?? '')
        break
      }

      case 'status': {
        const d = event.data as { token_usage?: TokenUsage }
        if (d.token_usage) executionStore.setTokenUsage(d.token_usage)
        break
      }

      case 'complete': {
        const d = event.data as {
          project_name:            string
          output_path:             string
          test_passed:             boolean
          error_log:               string
          token_usage:             TokenUsage | null
          generated_files:         string[]
          // SupervisorAgent routing result
          supervisor_pipelines:    string[]
          supervisor_confidence:   number
          supervisor_reason:       string
          supervisor_tools:        string[]
          supervisor_complexity:   string
          supervisor_modules:      string[]
          // MarketingAgent output
          marketing_report:        string
          marketing_report_path:   string
          // UIUXAgent output
          ui_design_system:        string
          ui_files:                string[]
          // IntegrationAgent output
          integration_guide:       string
          integration_notes:       string[]
          integration_files:       string[]
          // ValidationAgent output
          validation_report:       string
          validation_report_path:  string
          validation_score:        number
          validation_ready:        boolean
          validation_issues:       string[]
          // ScribeAgent output (TesterAgent disabled — ScribeAgent handles final step)
          scribe_output:           string
          scribe_readme_path:      string
          scribe_walkthrough_path: string
          scribe_saved_files:      string[]
          scribe_output_dir:       string
          scribe_run_commands:     string[]
          activity_log:            ActivityLogEntry[]
        }
        // Add walkthrough.md to the editor files panel
        if (d.scribe_output) {
          editorStore.addFile('walkthrough.md', d.scribe_output)
        }
        // Compose supervisor result if present
        const supervisorResult: SupervisorResult | null =
          d.supervisor_pipelines?.length > 0
            ? {
                pipelines:         d.supervisor_pipelines,
                confidence:        d.supervisor_confidence ?? 0,
                reason:            d.supervisor_reason     ?? '',
                tools:             d.supervisor_tools      ?? [],
                complexity:        (d.supervisor_complexity ?? 'MEDIUM') as SupervisorResult['complexity'],
                estimated_modules: d.supervisor_modules    ?? [],
              }
            : null
        // Prefer client-side log (built from events) over backend payload
        // — the client-side log is always populated even if backend sends []
        const finalActivityLog =
          clientActLog.current.length > 0
            ? [...clientActLog.current]
            : (d.activity_log ?? [])
        const validationResult: ValidationResult | null =
          d.validation_report
            ? {
                report:     d.validation_report,
                reportPath: d.validation_report_path ?? '',
                score:      d.validation_score      ?? 0,
                ready:      Boolean(d.validation_ready),
                issues:     d.validation_issues     ?? [],
              }
            : null

        const integrationResult: IntegrationResult | null =
          (d.integration_guide || d.integration_files?.length)
            ? {
                guide: d.integration_guide ?? '',
                notes: d.integration_notes ?? [],
                files: d.integration_files ?? [],
              }
            : null

        executionStore.setComplete({
          projectName:           d.project_name            ?? '',
          outputPath:            d.output_path             ?? '',
          testPassed:            Boolean(d.test_passed),
          errorLog:              d.error_log               ?? '',
          tokenUsage:            d.token_usage             ?? null,
          supervisorResult,
          marketingReport:       d.marketing_report        ?? '',
          marketingReportPath:   d.marketing_report_path   ?? '',
          uiDesignSystem:        d.ui_design_system        ?? '',
          uiFiles:               d.ui_files                ?? [],
          integrationResult,
          validationResult,
          scribeOutput:          d.scribe_output           ?? '',
          scribeReadmePath:      d.scribe_readme_path      ?? '',
          scribeWalkthroughPath: d.scribe_walkthrough_path ?? '',
          scribeSavedFiles:      d.scribe_saved_files      ?? [],
          scribeOutputDir:       d.scribe_output_dir       ?? '',
          scribeRunCommands:     d.scribe_run_commands     ?? [],
          activityLog:           finalActivityLog,
        })
        AGENT_ORDER.forEach(n => {
          if (agentStore.agents[n].status === 'running')
            agentStore.setAgentStatus(n, 'success')
        })
        agentStore.setActiveAgent(null)
        setWsUrl(null)   // disconnect
        break
      }

      case 'error': {
        const d = event.data as { message: string }
        executionStore.setError(d.message ?? 'Unknown error')
        logsStore.addLog({ agent: 'pipeline', level: 'error', message: d.message ?? '', timestamp: event.timestamp })
        const cur = executionStore.currentAgent as AgentName
        if (cur) agentStore.setAgentStatus(cur, 'error')
        setWsUrl(null)
        break
      }
    }
  }

  // ── public actions ──────────────────────────────────────────────────────────

  const run = useCallback(async (requirement: string) => {
    if (!requirement.trim()) return

    // Reset everything
    agentStore.resetAll()
    editorStore.clearFiles()
    logsStore.clearLogs()
    executionStore.reset()
    // Reset client-side activity log accumulators
    agentStartTs.current  = {}
    agentLogLines.current = {}
    clientActLog.current  = []

    try {
      const res  = await fetch(`${API}/pipeline/start`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ requirement }),
      })
      const json = await res.json() as { run_id: string; ws_url: string }
      executionStore.startRun(json.run_id, requirement)
      setWsUrl(`ws://localhost:8000${json.ws_url}`)
    } catch (err) {
      executionStore.setError(String(err))
    }
  }, [agentStore, editorStore, logsStore, executionStore])

  const cancel = useCallback(() => {
    closeWs()
    executionStore.setError('Cancelled by user.')
  }, [closeWs, executionStore])

  return { run, cancel }
}
