import { create } from 'zustand'
import type { AgentName, AgentState, AgentStatus } from '@/types'

export const AGENT_ORDER: AgentName[] = [
  'SupervisorAgent',
  'PlannerAgent',
  'ResearcherAgent',
  'ArchitectAgent',
  'CoderAgent',
  'UIUXAgent',
  'IntegrationAgent',
  'ScribeAgent',
  'MarketingAgent',
  'ValidationAgent',
  // 'TesterAgent',  // DISABLED — ScribeAgent is now the final pipeline step
  'DebugAgent',
  'ReviewerAgent',
]

const AGENT_DESCRIPTIONS: Record<AgentName, string> = {
  SupervisorAgent:  'Routing requirement to the best pipeline',
  PlannerAgent:     'Analysing input & decomposing into tasks',
  ResearcherAgent:  'Gathering libraries & patterns',
  ArchitectAgent:   'Designing system architecture',
  CoderAgent:       'Writing production code file by file',
  UIUXAgent:        'Designing dark + light mode UI system',
  IntegrationAgent: 'Wiring frontend ⇄ backend integration',
  ScribeAgent:      'Generating project walkthrough & saving files',
  MarketingAgent:   'Generating marketing intelligence report',
  ValidationAgent:  'Running quality gate & validation report',
  // TesterAgent:   'Running tests in isolated venv',  // DISABLED
  DebugAgent:       'Diagnosing and fixing errors',
  ReviewerAgent:    'Evaluating code quality',
}

const defaultAgent = (name: AgentName): AgentState => ({
  name,
  status:     'idle',
  description: AGENT_DESCRIPTIONS[name],
  startedAt:  null,
  finishedAt: null,
  tokenUsage: 0,
  logs:       [],
})

interface AgentStore {
  agents:      Record<AgentName, AgentState>
  activeAgent: AgentName | null
  // actions
  setAgentStatus: (name: AgentName, status: AgentStatus) => void
  setActiveAgent: (name: AgentName | null) => void
  addAgentLog:    (name: AgentName, log: import('@/types').LogEntry) => void
  addTokens:      (name: AgentName, tokens: number) => void
  resetAll:       () => void
}

const initialAgents = () =>
  Object.fromEntries(
    AGENT_ORDER.map(n => [n, defaultAgent(n)])
  ) as Record<AgentName, AgentState>

export const useAgentStore = create<AgentStore>((set) => ({
  agents:      initialAgents(),
  activeAgent: null,

  setAgentStatus: (name, status) =>
    set(s => ({
      agents: {
        ...s.agents,
        [name]: {
          ...s.agents[name],
          status,
          startedAt:  status === 'running'                    ? Date.now() : s.agents[name].startedAt,
          finishedAt: status === 'success' || status === 'error' ? Date.now() : s.agents[name].finishedAt,
        },
      },
    })),

  setActiveAgent: (name) => set({ activeAgent: name }),

  addAgentLog: (name, log) =>
    set(s => ({
      agents: {
        ...s.agents,
        [name]: {
          ...s.agents[name],
          logs: [...s.agents[name].logs, log],
        },
      },
    })),

  addTokens: (name, tokens) =>
    set(s => ({
      agents: {
        ...s.agents,
        [name]: {
          ...s.agents[name],
          tokenUsage: s.agents[name].tokenUsage + tokens,
        },
      },
    })),

  resetAll: () => set({ agents: initialAgents(), activeAgent: null }),
}))
