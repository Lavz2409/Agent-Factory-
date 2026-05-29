import { create } from 'zustand'
import type {
  ExecutionStatus, TokenUsage, DataFlowEvent, ActivityLogEntry,
  SupervisorResult, ValidationResult, IntegrationResult,
} from '@/types'
import { AGENT_ORDER } from './agentStore'

interface ExecutionStore {
  runId:              string
  requirement:        string
  status:             ExecutionStatus
  progress:           number
  startTime:          number
  currentAgent:       string
  tokenUsage:         TokenUsage | null
  projectName:        string
  outputPath:         string
  testPassed:         boolean | null
  errorLog:           string
  dataFlow:           DataFlowEvent[]
  // SupervisorAgent routing result
  supervisorResult:   SupervisorResult | null
  // MarketingAgent output
  marketingReport:      string   // full Markdown marketing intelligence report
  marketingReportPath:  string   // absolute path to marketing_report.md
  // UIUXAgent output
  uiDesignSystem:       string   // UI_DESIGN_SYSTEM.md body
  uiFiles:              string[] // generated component/style file paths
  // IntegrationAgent output
  integrationResult:    IntegrationResult | null
  // ValidationAgent output
  validationResult:     ValidationResult | null
  // ScribeAgent output
  scribeOutput:           string    // full Markdown walkthrough
  scribeReadmePath:       string    // kept for compat (always "" now)
  scribeWalkthroughPath:  string    // absolute path to walkthrough.md
  scribeSavedFiles:       string[]  // absolute paths of all written files
  scribeOutputDir:        string    // directory where files were saved
  scribeRunCommands:      string[]  // ready-to-run terminal commands
  // Activity log
  activityLog:            ActivityLogEntry[]
  // actions
  startRun:               (runId: string, requirement: string) => void
  setCurrentAgent:        (agent: string) => void
  setTokenUsage:          (usage: TokenUsage) => void
  setSupervisorResult:    (result: SupervisorResult) => void
  setComplete:            (data: {
    projectName:            string
    outputPath:             string
    testPassed:             boolean
    errorLog:               string
    tokenUsage:             TokenUsage | null
    supervisorResult:       SupervisorResult | null
    marketingReport:        string
    marketingReportPath:    string
    uiDesignSystem:         string
    uiFiles:                string[]
    integrationResult:      IntegrationResult | null
    validationResult:       ValidationResult | null
    scribeOutput:           string
    scribeReadmePath:       string
    scribeWalkthroughPath:  string
    scribeSavedFiles:       string[]
    scribeOutputDir:        string
    scribeRunCommands:      string[]
    activityLog:            ActivityLogEntry[]
  }) => void
  setError:           (msg: string) => void
  addDataFlow:        (event: DataFlowEvent) => void
  reset:              () => void
}

const initial = {
  runId:             '',
  requirement:       '',
  status:            'idle' as ExecutionStatus,
  progress:          0,
  startTime:         0,
  currentAgent:      '',
  tokenUsage:        null,
  projectName:       '',
  outputPath:        '',
  testPassed:        null,
  errorLog:          '',
  dataFlow:          [],
  // SupervisorAgent routing result
  supervisorResult:  null as SupervisorResult | null,
  // MarketingAgent output
  marketingReport:     '',
  marketingReportPath: '',
  // UIUXAgent output
  uiDesignSystem:      '',
  uiFiles:             [] as string[],
  // IntegrationAgent output
  integrationResult:   null as IntegrationResult | null,
  // ValidationAgent output
  validationResult:    null as ValidationResult | null,
  // ScribeAgent output
  scribeOutput:          '',
  scribeReadmePath:      '',
  scribeWalkthroughPath: '',
  scribeSavedFiles:      [] as string[],
  scribeOutputDir:       '',
  scribeRunCommands:     [] as string[],
  // Activity log
  activityLog:           [] as ActivityLogEntry[],
}

function agentProgress(agentName: string): number {
  const idx = AGENT_ORDER.indexOf(agentName as never)
  if (idx < 0) return 0
  return Math.round(((idx + 1) / AGENT_ORDER.length) * 90)
}

export const useExecutionStore = create<ExecutionStore>((set) => ({
  ...initial,

  startRun: (runId, requirement) =>
    set({ ...initial, runId, requirement, status: 'running', startTime: Date.now() }),

  setCurrentAgent: (agent) =>
    set({ currentAgent: agent, progress: agentProgress(agent) }),

  setTokenUsage: (usage) =>
    set({ tokenUsage: usage }),

  setSupervisorResult: (result) =>
    set({ supervisorResult: result }),

  setComplete: ({
    projectName, outputPath, testPassed, errorLog, tokenUsage,
    supervisorResult,
    marketingReport, marketingReportPath,
    uiDesignSystem, uiFiles,
    integrationResult, validationResult,
    scribeOutput, scribeReadmePath, scribeWalkthroughPath,
    scribeSavedFiles, scribeOutputDir, scribeRunCommands,
    activityLog,
  }) =>
    set({
      status:                'completed',
      progress:              100,
      projectName,
      outputPath,
      testPassed,
      errorLog,
      tokenUsage:            tokenUsage ?? null,
      currentAgent:          '',
      supervisorResult:      supervisorResult       ?? null,
      marketingReport:       marketingReport        ?? '',
      marketingReportPath:   marketingReportPath    ?? '',
      uiDesignSystem:        uiDesignSystem         ?? '',
      uiFiles:               uiFiles                ?? [],
      integrationResult:     integrationResult      ?? null,
      validationResult:      validationResult       ?? null,
      scribeOutput:          scribeOutput           ?? '',
      scribeReadmePath:      scribeReadmePath       ?? '',
      scribeWalkthroughPath: scribeWalkthroughPath  ?? '',
      scribeSavedFiles:      scribeSavedFiles       ?? [],
      scribeOutputDir:       scribeOutputDir        ?? '',
      scribeRunCommands:     scribeRunCommands       ?? [],
      activityLog:           activityLog            ?? [],
    }),

  setError: (msg) =>
    set({ status: 'error', errorLog: msg, currentAgent: '', progress: 0 }),

  addDataFlow: (event) =>
    set(s => ({ dataFlow: [...s.dataFlow, event] })),

  reset: () => set(initial),
}))
