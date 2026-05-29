import { useState } from 'react'
import type { ActivityLogEntry } from '@/types'

interface Props {
  activityLog: ActivityLogEntry[]
  onClose: () => void
}

const AGENT_COLORS: Record<string, string> = {
  Planner:    '#6366f1',
  Researcher: '#0ea5e9',
  Architect:  '#f59e0b',
  Coder:      '#10b981',
  Scribe:     '#a78bfa',
}

function dot(agent: string) {
  return AGENT_COLORS[agent] ?? '#6366f1'
}

export default function ActivityLog({ activityLog, onClose }: Props) {
  const [selected, setSelected] = useState(0)

  const entry = activityLog[selected]

  return (
    <div style={{
      position:       'fixed',
      inset:          0,
      background:     'rgba(0,0,0,0.88)',
      zIndex:         2000,
      display:        'flex',
      flexDirection:  'column',
      fontFamily:     'monospace',
    }}>
      {/* Header */}
      <div style={{
        display:        'flex',
        justifyContent: 'space-between',
        alignItems:     'center',
        padding:        '14px 24px',
        borderBottom:   '1px solid #1e293b',
        background:     '#0f172a',
        flexShrink:     0,
      }}>
        <h2 style={{ color: '#e2e8f0', margin: 0, fontSize: '15px' }}>
          🔍 Agent Activity Log
        </h2>
        <button
          onClick={onClose}
          style={{
            background:   'none',
            border:       '1px solid #334155',
            color:        '#94a3b8',
            padding:      '5px 12px',
            borderRadius: '4px',
            cursor:       'pointer',
            fontFamily:   'monospace',
            fontSize:     '12px',
          }}
        >
          ✕ Close
        </button>
      </div>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', minHeight: 0 }}>

        {/* Left — step list */}
        <div style={{
          width:      '220px',
          borderRight:'1px solid #1e293b',
          background: '#0f172a',
          overflowY:  'auto',
          padding:    '10px 0',
          flexShrink: 0,
        }}>
          {activityLog.map((e, i) => (
            <div
              key={i}
              onClick={() => setSelected(i)}
              style={{
                padding:    '11px 16px',
                cursor:     'pointer',
                background: selected === i ? '#1e293b' : 'transparent',
                borderLeft: `3px solid ${selected === i ? dot(e.agent) : 'transparent'}`,
                transition: 'all 0.12s',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{
                  width: '8px', height: '8px', borderRadius: '50%',
                  background: dot(e.agent), flexShrink: 0,
                }} />
                <span style={{ color: '#e2e8f0', fontSize: '13px' }}>
                  {e.agent}
                </span>
              </div>
              <div style={{
                display:        'flex',
                justifyContent: 'space-between',
                marginTop:      '4px',
                paddingLeft:    '16px',
              }}>
                <span style={{ fontSize: '11px', color: e.status === 'error' ? '#f87171' : '#4ade80' }}>
                  {e.status === 'error' ? '✗ error' : '✓ success'}
                </span>
                <span style={{ fontSize: '11px', color: '#64748b' }}>
                  {e.duration}s
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Right — full output */}
        <div style={{
          flex:       1,
          padding:    '20px 24px',
          overflowY:  'auto',
          background: '#0d1117',
        }}>
          {entry ? (
            <>
              <div style={{
                display:    'flex',
                alignItems: 'center',
                gap:        '12px',
                marginBottom: '16px',
              }}>
                <span style={{
                  width: '12px', height: '12px', borderRadius: '50%',
                  background: dot(entry.agent),
                }} />
                <h3 style={{ color: '#e2e8f0', margin: 0, fontSize: '14px' }}>
                  Step {entry.step} — {entry.agent} Agent
                </h3>
                <span style={{ fontSize: '11px', color: '#64748b', marginLeft: 'auto' }}>
                  ⏱ {entry.duration}s
                </span>
              </div>
              <pre style={{
                whiteSpace:   'pre-wrap',
                fontFamily:   'monospace',
                fontSize:     '13px',
                color:        '#d4d4d4',
                background:   '#1e1e1e',
                padding:      '16px',
                borderRadius: '8px',
                lineHeight:   '1.6',
                border:       '1px solid #2d2d2d',
                maxHeight:    'calc(100vh - 180px)',
                overflowY:    'auto',
                margin:       0,
              }}>
                {entry.full_output || 'No output captured.'}
              </pre>
            </>
          ) : (
            <p style={{ color: '#4a4a6a', fontSize: '13px' }}>
              Select an agent step to view its output.
            </p>
          )}
        </div>

      </div>
    </div>
  )
}
