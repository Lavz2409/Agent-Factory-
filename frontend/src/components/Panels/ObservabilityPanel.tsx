import { useExecutionStore } from '@/store/executionStore'
import { useAgentStore, AGENT_ORDER } from '@/store/agentStore'
import { useState } from 'react'
import TerminalPanel from '../TerminalPanel'
import type { SupervisorResult, ValidationResult, IntegrationResult } from '@/types'

function fmt(ms: number) {
  return ms < 1000 ? `${ms}ms` : `${(ms / 1000).toFixed(1)}s`
}

function Bar({ pct, color }: { pct: number; color: string }) {
  return (
    <div className="h-1.5 rounded-full bg-[#1e1e32] overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-500"
        style={{ width: `${Math.min(100, pct)}%`, background: color }}
      />
    </div>
  )
}

export default function ObservabilityPanel() {
  const {
    tokenUsage, status, progress, startTime, projectName,
    supervisorResult,
    marketingReport, marketingReportPath,
    integrationResult, validationResult,
    scribeOutput, scribeReadmePath, scribeWalkthroughPath,
    scribeSavedFiles, scribeOutputDir, scribeRunCommands,
  } = useExecutionStore()

  const btnStyle = (bg: string): React.CSSProperties => ({
    display:        'inline-block',
    padding:        '8px 16px',
    background:     bg,
    color:          '#fff',
    borderRadius:   '6px',
    fontSize:       '13px',
    fontFamily:     'monospace',
    textDecoration: 'none',
    cursor:         'pointer',
    border:         'none',
    whiteSpace:     'nowrap',
  })
  const { agents } = useAgentStore()

  const [scribeExpanded, setScribeExpanded] = useState(false)
  const [saveDir, setSaveDir]               = useState('')
  const [saveStatus, setSaveStatus]         = useState<string | null>(null)
  const [saving, setSaving]                 = useState(false)

  const elapsed = startTime ? Date.now() - startTime : 0
  const totals   = tokenUsage?.totals
  const byAgent  = tokenUsage?.by_agent ?? {}
  const totalTokens = totals?.total_tokens ?? 0
  const calls = tokenUsage?.calls ?? 0

  const handleSaveFiles = async () => {
    const dir = saveDir.trim()
    if (!dir) {
      setSaveStatus('❌ Please enter a folder path first.')
      return
    }
    if (!scribeOutput) {
      setSaveStatus('❌ No files to save yet. Run the pipeline first.')
      return
    }
    setSaving(true)
    setSaveStatus(null)
    try {
      const files = [{ filename: 'README.md', content: scribeOutput }]
      const res = await fetch('http://localhost:8000/api/save-files', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ output_dir: dir, files }),
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.detail ?? 'Save failed')
      setSaveStatus(`✅ Saved ${json.count ?? json.saved?.length ?? 1} file(s) to: ${json.output_dir}`)
    } catch (err: unknown) {
      setSaveStatus(`❌ ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-4 text-[0.7rem]">

      {/* run summary */}
      <section>
        <Label>Run Summary</Label>
        <div className="grid grid-cols-2 gap-2 mt-1">
          <Metric label="Status"  value={status.toUpperCase()} color={
            status === 'completed' ? '#00ff88' :
            status === 'error'     ? '#ff0055' :
            status === 'running'   ? '#00d9ff' : '#4a4a6a'
          } />
          <Metric label="Elapsed"   value={startTime ? fmt(elapsed) : '—'} />
          <Metric label="Progress"  value={`${progress}%`} />
          <Metric label="LLM Calls" value={String(calls)} />
        </div>
        <div className="mt-1.5">
          <Bar pct={progress} color="#00d9ff" />
        </div>
      </section>

      {/* ── Supervisor routing card ────────────────────────────────────────── */}
      {supervisorResult && <SupervisorCard result={supervisorResult} />}

      {/* ── Validation quality-gate card ──────────────────────────────────── */}
      {validationResult && <ValidationCard result={validationResult} />}

      {/* ── Integration layer card ────────────────────────────────────────── */}
      {integrationResult && <IntegrationCard result={integrationResult} />}

      {/* ── Marketing report card ─────────────────────────────────────────── */}
      {marketingReport && (
        <MarketingReportCard
          report={marketingReport}
          reportPath={marketingReportPath}
        />
      )}

      {/* token breakdown */}
      <section>
        <Label>Token Usage</Label>
        <div className="grid grid-cols-3 gap-2 mt-1">
          <Metric label="Prompt"     value={(totals?.prompt_tokens     ?? 0).toLocaleString()} />
          <Metric label="Completion" value={(totals?.completion_tokens ?? 0).toLocaleString()} />
          <Metric label="Total"      value={totalTokens.toLocaleString()} />
        </div>
      </section>

      {/* per-agent token breakdown */}
      {Object.keys(byAgent).length > 0 && (
        <section>
          <Label>Per-Agent Tokens</Label>
          <div className="mt-1 space-y-1.5">
            {Object.entries(byAgent).map(([name, data]) => {
              const pct = totalTokens ? (data.total_tokens / totalTokens) * 100 : 0
              return (
                <div key={name}>
                  <div className="flex justify-between text-[0.62rem] mb-0.5">
                    <span className="text-muted">{name}</span>
                    <span className="text-textDim">{data.total_tokens.toLocaleString()}</span>
                  </div>
                  <Bar pct={pct} color="#00d9ff88" />
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* agent pipeline DAG */}
      <section>
        <Label>Pipeline DAG</Label>
        <div className="mt-1 flex flex-col gap-0.5">
          {AGENT_ORDER.map((name, i) => {
            const s = agents[name].status
            const dotColor =
              s === 'running' ? '#00d9ff' :
              s === 'success' ? '#00ff88' :
              s === 'error'   ? '#ff0055' : '#1e1e32'
            return (
              <div key={name} className="flex items-center gap-2">
                <div
                  className="w-2.5 h-2.5 rounded-full border-2 transition-colors"
                  style={{ borderColor: dotColor, background: s !== 'idle' ? dotColor : 'transparent' }}
                />
                <span className={s === 'idle' ? 'text-muted' : 'text-text'}>
                  {name.replace('Agent', '')}
                </span>
                {i < AGENT_ORDER.length - 1 && (
                  <div className="w-px h-3 bg-[#1e1e32] ml-1" />
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* output info */}
      {projectName && (
        <section>
          <Label>Output</Label>
          <div className="mt-1 space-y-1">
            <div className="text-textDim">
              Project: <span className="text-accent">{projectName}</span>
            </div>
            {/* DISABLED - TesterAgent removed */}
          </div>
        </section>
      )}

      {/* ── 📜 Scribe Agent — Project Walkthrough ───────────────────────────── */}
      {scribeOutput && (
        <section>
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setScribeExpanded(v => !v)}
          >
            <Label>📜 Scribe Agent — Project Walkthrough</Label>
            <span className="text-[0.6rem] text-muted">
              {scribeExpanded ? '▲ hide' : '▼ show'}
            </span>
          </div>

          {scribeExpanded && (
            <div style={{ marginTop: '12px' }}>

              {/* Walkthrough markdown */}
              <pre style={{
                whiteSpace:   'pre-wrap',
                fontFamily:   'monospace',
                fontSize:     '13px',
                background:   '#1e1e1e',
                color:        '#d4d4d4',
                padding:      '16px',
                borderRadius: '8px',
                overflowX:    'auto',
                maxHeight:    '500px',
                overflowY:    'auto',
                border:       '1px solid #3f3f3f',
              }}>
                <code>{scribeOutput}</code>
              </pre>

              {/* ── Download Controls ── */}
              {(scribeWalkthroughPath || scribeOutputDir) && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '14px' }}>

                  {/* Download walkthrough.md */}
                  {scribeWalkthroughPath && (
                    <a
                      href={`http://localhost:8000/api/download-walkthrough?path=${encodeURIComponent(scribeWalkthroughPath)}`}
                      download="walkthrough.md"
                      style={btnStyle('#7c3aed')}
                    >
                      📄 Download walkthrough.md
                    </a>
                  )}

                  {/* Download entire project as ZIP */}
                  {scribeOutputDir && (
                    <a
                      href={`http://localhost:8000/api/download-project-zip?output_dir=${encodeURIComponent(scribeOutputDir)}`}
                      download="project.zip"
                      style={btnStyle('#065f46')}
                    >
                      📦 Download Project (.zip)
                    </a>
                  )}

                </div>
              )}

              {/* Saved files list */}
              {scribeSavedFiles.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <p style={{ color: '#888', fontSize: '12px', marginBottom: '4px' }}>
                    📁 Files saved to:{' '}
                    <span style={{ color: '#a3e635' }}>{scribeOutputDir}</span>
                  </p>
                  <ul style={{ fontSize: '12px', color: '#94a3b8', paddingLeft: '16px' }}>
                    {scribeSavedFiles.map((f, i) => <li key={i}>{f}</li>)}
                  </ul>
                </div>
              )}

              {/* Run commands */}
              {scribeRunCommands.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <p style={{ color: '#888', fontSize: '12px' }}>▶️ Run commands:</p>
                  {scribeRunCommands.map((cmd, i) => (
                    <pre key={i} style={{
                      background:   '#0f172a',
                      color:        '#4ade80',
                      padding:      '8px 12px',
                      borderRadius: '6px',
                      fontSize:     '13px',
                      marginTop:    '4px',
                    }}>
                      $ {cmd}
                    </pre>
                  ))}
                </div>
              )}

              {/* walkthrough.md path */}
              {scribeWalkthroughPath && (
                <p style={{ fontSize: '12px', color: '#888', marginTop: '8px' }}>
                  📄 walkthrough.md saved to: {scribeWalkthroughPath}
                </p>
              )}

              {/* ── 💾 Save-to-folder panel ──────────────────────────────────── */}
              <div style={{
                marginTop:    '16px',
                background:   '#111',
                border:       '1px solid #2a2a3a',
                borderRadius: '8px',
                padding:      '12px',
              }}>
                <p style={{ color: '#888', fontSize: '12px', marginBottom: '8px' }}>
                  💾 Save walkthrough to a custom folder:
                </p>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <input
                    value={saveDir}
                    onChange={e => setSaveDir(e.target.value)}
                    placeholder="e.g. C:\Projects\MyAgent"
                    style={{
                      flex:        1,
                      minWidth:    '180px',
                      background:  '#0a0a14',
                      border:      '1px solid #333',
                      borderRadius:'4px',
                      color:       '#e0e0f0',
                      fontSize:    '12px',
                      padding:     '6px 10px',
                      outline:     'none',
                    }}
                  />
                  <button
                    onClick={handleSaveFiles}
                    disabled={saving}
                    style={{
                      padding:      '8px 16px',
                      background:   saving ? '#374151' : '#065f46',
                      color:        '#fff',
                      border:       'none',
                      borderRadius: '6px',
                      cursor:       saving ? 'not-allowed' : 'pointer',
                      fontFamily:   'monospace',
                      fontSize:     '13px',
                      whiteSpace:   'nowrap',
                    }}
                  >
                    {saving ? '⏳ Saving…' : '💾 Save Files'}
                  </button>
                </div>
                {saveStatus && (
                  <p style={{
                    marginTop: '8px',
                    fontSize:  '12px',
                    color:     saveStatus.startsWith('✅') ? '#4ade80' : '#f87171',
                  }}>
                    {saveStatus}
                  </p>
                )}
              </div>

              {/* ── Terminal panel ──────────────────────────────────────────── */}
              <TerminalPanel runCommands={scribeRunCommands} />

            </div>
          )}
        </section>
      )}

    </div>
  )
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[0.6rem] uppercase tracking-widest text-muted">
      {children}
    </div>
  )
}

function Metric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="bg-[#0f0f1e] border border-[#1e1e32] rounded-lg p-2 text-center">
      <div className="font-semibold" style={{ color: color ?? '#e0e0f0' }}>{value}</div>
      <div className="text-muted text-[0.58rem] uppercase tracking-wider mt-0.5">{label}</div>
    </div>
  )
}

// ── Supervisor routing card ───────────────────────────────────────────────────

const PIPELINE_COLORS: Record<string, string> = {
  AI_VISION:     '#a855f7',
  WEB_APP:       '#00d9ff',
  CHATBOT:       '#f59e0b',
  DATA_PIPELINE: '#10b981',
  AUTOMATION:    '#f97316',
  MOBILE_APP:    '#ec4899',
}

const COMPLEXITY_COLOR: Record<string, string> = {
  LOW:    '#10b981',
  MEDIUM: '#f59e0b',
  HIGH:   '#ff0055',
}

function SupervisorCard({ result }: { result: SupervisorResult }) {
  const [expanded, setExpanded] = useState(true)
  const confidence = Math.round(result.confidence * 100)
  const complexityColor = COMPLEXITY_COLOR[result.complexity] ?? '#888'

  return (
    <section
      style={{
        background:   'linear-gradient(135deg, #0a0a20 0%, #0d0d25 100%)',
        border:       '1px solid #2a1a5e',
        borderRadius: '10px',
        padding:      '12px',
        boxShadow:    '0 0 20px rgba(100,50,255,0.08)',
      }}
    >
      {/* header */}
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(v => !v)}
      >
        <div className="flex items-center gap-2">
          <span style={{ fontSize: '14px' }}>🧠</span>
          <span
            style={{
              fontSize:      '0.65rem',
              fontWeight:    700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color:         '#a78bfa',
            }}
          >
            Supervisor Routing
          </span>
        </div>
        <span className="text-[0.6rem] text-muted">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div style={{ marginTop: '10px' }} className="space-y-3">

          {/* selected pipelines */}
          <div>
            <div className="text-[0.58rem] uppercase tracking-widest text-muted mb-1">
              Selected Pipeline(s)
            </div>
            <div className="flex flex-wrap gap-1.5">
              {result.pipelines.map(p => (
                <span
                  key={p}
                  style={{
                    fontSize:     '0.62rem',
                    fontWeight:   700,
                    padding:      '3px 8px',
                    borderRadius: '4px',
                    background:   `${PIPELINE_COLORS[p] ?? '#4a4a6a'}22`,
                    border:       `1px solid ${PIPELINE_COLORS[p] ?? '#4a4a6a'}66`,
                    color:        PIPELINE_COLORS[p] ?? '#e0e0f0',
                    letterSpacing:'0.04em',
                  }}
                >
                  {p}
                </span>
              ))}
            </div>
          </div>

          {/* confidence bar */}
          <div>
            <div className="flex justify-between text-[0.58rem] mb-0.5">
              <span className="text-muted">Confidence</span>
              <span style={{ color: confidence >= 80 ? '#00ff88' : '#f59e0b', fontWeight: 600 }}>
                {confidence}%
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-[#1e1e32] overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width:      `${confidence}%`,
                  background: `linear-gradient(90deg, #7c3aed, ${confidence >= 80 ? '#00ff88' : '#f59e0b'})`,
                }}
              />
            </div>
          </div>

          {/* complexity + reason */}
          <div className="grid grid-cols-2 gap-2">
            <div
              style={{
                background:   '#0f0f1e',
                border:       `1px solid ${complexityColor}44`,
                borderRadius: '6px',
                padding:      '6px 8px',
                textAlign:    'center',
              }}
            >
              <div style={{ color: complexityColor, fontWeight: 700, fontSize: '0.75rem' }}>
                {result.complexity}
              </div>
              <div className="text-muted text-[0.55rem] uppercase tracking-wider mt-0.5">
                Complexity
              </div>
            </div>
            <div
              style={{
                background:   '#0f0f1e',
                border:       '1px solid #1e1e32',
                borderRadius: '6px',
                padding:      '6px 8px',
                textAlign:    'center',
              }}
            >
              <div style={{ color: '#e0e0f0', fontWeight: 700, fontSize: '0.75rem' }}>
                {result.estimated_modules.length}
              </div>
              <div className="text-muted text-[0.55rem] uppercase tracking-wider mt-0.5">
                Modules
              </div>
            </div>
          </div>

          {/* reason */}
          {result.reason && (
            <div
              style={{
                fontSize:     '0.65rem',
                color:        '#94a3b8',
                background:   '#0a0a14',
                borderRadius: '6px',
                padding:      '8px 10px',
                borderLeft:   '3px solid #7c3aed',
                lineHeight:   1.5,
              }}
            >
              {result.reason}
            </div>
          )}

          {/* tools */}
          {result.tools.length > 0 && (
            <div>
              <div className="text-[0.58rem] uppercase tracking-widest text-muted mb-1">
                Recommended Tools
              </div>
              <div className="flex flex-wrap gap-1">
                {result.tools.map(t => (
                  <span
                    key={t}
                    style={{
                      fontSize:     '0.6rem',
                      padding:      '2px 6px',
                      borderRadius: '3px',
                      background:   '#1a1a2e',
                      border:       '1px solid #2a2a4e',
                      color:        '#c0c0e0',
                    }}
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* estimated modules */}
          {result.estimated_modules.length > 0 && (
            <div>
              <div className="text-[0.58rem] uppercase tracking-widest text-muted mb-1">
                Estimated Modules
              </div>
              <ul className="space-y-0.5">
                {result.estimated_modules.map((m, i) => (
                  <li key={i} className="flex items-center gap-1.5 text-[0.62rem] text-textDim">
                    <span style={{ color: '#7c3aed', fontSize: '0.6rem' }}>▸</span>
                    {m}
                  </li>
                ))}
              </ul>
            </div>
          )}

        </div>
      )}
    </section>
  )
}

// ── Marketing Report Card ─────────────────────────────────────────────────────

const SECTION_ICONS: Record<string, string> = {
  'PRODUCT UNDERSTANDING':    '🎯',
  'COMPETITOR ANALYSIS':      '🔍',
  'DIFFERENTIATION STRATEGY': '💎',
  'USE CASES':                '📋',
  'MARKETING STRATEGY':       '📣',
  'CAMPAIGN IDEAS':           '💡',
  'GO-TO-MARKET PLAN':        '🚀',
  'CONTENT STRATEGY':         '✍️',
  'GROWTH HACKS':             '⚡',
  'SWOT ANALYSIS':            '📊',
}

function parseSections(report: string): Array<{ title: string; icon: string; content: string }> {
  const sections: Array<{ title: string; icon: string; content: string }> = []
  const lines = report.split('\n')
  let cur: { title: string; icon: string; content: string } | null = null

  for (const line of lines) {
    const h2 = line.match(/^##\s+\d+\.\s+(.+)/)
    if (h2) {
      if (cur) sections.push(cur)
      const title = h2[1].trim().toUpperCase()
      const icon  = Object.entries(SECTION_ICONS).find(([k]) => title.includes(k))?.[1] ?? '📌'
      cur = { title: h2[1].trim(), icon, content: '' }
    } else if (cur) {
      cur.content += line + '\n'
    }
  }
  if (cur) sections.push(cur)
  return sections
}

function MarketingReportCard({
  report,
  reportPath,
}: {
  report: string
  reportPath: string
}) {
  const [expanded,        setExpanded]        = useState(true)
  const [openSection,     setOpenSection]     = useState<number | null>(0)
  const [copyStatus,      setCopyStatus]      = useState<'idle' | 'copied'>('idle')

  const sections = parseSections(report)
  const wordCount = report.split(/\s+/).filter(Boolean).length

  const handleCopy = () => {
    navigator.clipboard.writeText(report).then(() => {
      setCopyStatus('copied')
      setTimeout(() => setCopyStatus('idle'), 2000)
    })
  }

  return (
    <section
      style={{
        background:   'linear-gradient(135deg, #0a1a0a 0%, #0d1f0d 100%)',
        border:       '1px solid #1a4d1a',
        borderRadius: '10px',
        padding:      '12px',
        boxShadow:    '0 0 20px rgba(16,185,129,0.06)',
      }}
    >
      {/* header */}
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(v => !v)}
      >
        <div className="flex items-center gap-2">
          <span style={{ fontSize: '14px' }}>📣</span>
          <span
            style={{
              fontSize:      '0.65rem',
              fontWeight:    700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color:         '#34d399',
            }}
          >
            Marketing Intelligence Report
          </span>
          <span
            style={{
              fontSize:     '0.58rem',
              color:        '#6b7280',
              background:   '#111',
              border:       '1px solid #1e3a1e',
              borderRadius: '3px',
              padding:      '1px 5px',
            }}
          >
            {wordCount.toLocaleString()} words · {sections.length} sections
          </span>
        </div>
        <span className="text-[0.6rem] text-muted">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div style={{ marginTop: '10px' }} className="space-y-2">

          {/* action bar */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={handleCopy}
              style={{
                fontSize:     '0.62rem',
                padding:      '4px 10px',
                background:   copyStatus === 'copied' ? '#065f46' : '#1a2e1a',
                border:       '1px solid #1a4d1a',
                borderRadius: '4px',
                color:        copyStatus === 'copied' ? '#6ee7b7' : '#94a3b8',
                cursor:       'pointer',
              }}
            >
              {copyStatus === 'copied' ? '✓ Copied!' : '📋 Copy Markdown'}
            </button>
            {reportPath && (
              <a
                href={`http://localhost:8000/api/download-walkthrough?path=${encodeURIComponent(reportPath)}`}
                download="marketing_report.md"
                style={{
                  fontSize:       '0.62rem',
                  padding:        '4px 10px',
                  background:     '#1a2e1a',
                  border:         '1px solid #1a4d1a',
                  borderRadius:   '4px',
                  color:          '#94a3b8',
                  textDecoration: 'none',
                  cursor:         'pointer',
                }}
              >
                ⬇ Download .md
              </a>
            )}
          </div>

          {/* section accordion */}
          {sections.map((sec, i) => (
            <div
              key={i}
              style={{
                background:   '#0a140a',
                border:       `1px solid ${openSection === i ? '#1a4d1a' : '#111a11'}`,
                borderRadius: '6px',
                overflow:     'hidden',
              }}
            >
              <div
                className="flex items-center gap-2 cursor-pointer px-3 py-2"
                onClick={() => setOpenSection(openSection === i ? null : i)}
                style={{ userSelect: 'none' }}
              >
                <span style={{ fontSize: '0.75rem' }}>{sec.icon}</span>
                <span
                  style={{
                    flex:       1,
                    fontSize:   '0.65rem',
                    fontWeight: 600,
                    color:      openSection === i ? '#34d399' : '#64748b',
                  }}
                >
                  {sec.title}
                </span>
                <span style={{ fontSize: '0.6rem', color: '#374151' }}>
                  {openSection === i ? '▲' : '▼'}
                </span>
              </div>
              {openSection === i && (
                <pre
                  style={{
                    whiteSpace:  'pre-wrap',
                    wordBreak:   'break-word',
                    fontFamily:  'monospace',
                    fontSize:    '0.65rem',
                    color:       '#94a3b8',
                    padding:     '10px 14px',
                    borderTop:   '1px solid #111a11',
                    margin:      0,
                    maxHeight:   '360px',
                    overflowY:   'auto',
                    lineHeight:  1.6,
                  }}
                >
                  {sec.content.trim()}
                </pre>
              )}
            </div>
          ))}

        </div>
      )}
    </section>
  )
}

// ── Validation Card ───────────────────────────────────────────────────────────

function ValidationCard({ result }: { result: ValidationResult }) {
  const [expanded, setExpanded] = useState(true)

  const scoreColor =
    result.score >= 9 ? '#00ff88' :
    result.score >= 7 ? '#34d399' :
    result.score >= 5 ? '#f59e0b' : '#ff0055'

  return (
    <section
      style={{
        background:   'linear-gradient(135deg, #0a1f1a 0%, #0d251f 100%)',
        border:       `1px solid ${result.ready ? '#065f46' : '#4d1a1a'}`,
        borderRadius: '10px',
        padding:      '12px',
        boxShadow:    `0 0 20px ${result.ready ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)'}`,
      }}
    >
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(v => !v)}
      >
        <div className="flex items-center gap-2">
          <span style={{ fontSize: '14px' }}>{result.ready ? '✅' : '⚠️'}</span>
          <span
            style={{
              fontSize:      '0.65rem',
              fontWeight:    700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color:         result.ready ? '#6ee7b7' : '#fca5a5',
            }}
          >
            Validation Report
          </span>
          <span
            style={{
              fontSize:     '0.6rem',
              fontWeight:   700,
              padding:      '2px 8px',
              borderRadius: '10px',
              background:   `${scoreColor}22`,
              border:       `1px solid ${scoreColor}66`,
              color:        scoreColor,
            }}
          >
            {result.score.toFixed(1)} / 10
          </span>
        </div>
        <span className="text-[0.6rem] text-muted">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div style={{ marginTop: '10px' }} className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <div
              style={{
                background:   '#0f0f1e',
                border:       `1px solid ${result.ready ? '#065f46' : '#4d1a1a'}44`,
                borderRadius: '6px',
                padding:      '6px 8px',
                textAlign:    'center',
              }}
            >
              <div style={{ color: result.ready ? '#00ff88' : '#ff0055', fontWeight: 700, fontSize: '0.75rem' }}>
                {result.ready ? 'READY' : 'BLOCKED'}
              </div>
              <div className="text-muted text-[0.55rem] uppercase tracking-wider mt-0.5">
                Production
              </div>
            </div>
            <div
              style={{
                background:   '#0f0f1e',
                border:       '1px solid #1e1e32',
                borderRadius: '6px',
                padding:      '6px 8px',
                textAlign:    'center',
              }}
            >
              <div style={{
                color:      result.issues.length === 0 ? '#00ff88' : '#f59e0b',
                fontWeight: 700,
                fontSize:   '0.75rem',
              }}>
                {result.issues.length}
              </div>
              <div className="text-muted text-[0.55rem] uppercase tracking-wider mt-0.5">
                Issues
              </div>
            </div>
          </div>

          {result.issues.length > 0 && (
            <div>
              <div className="text-[0.58rem] uppercase tracking-widest text-muted mb-1">
                Issues Found
              </div>
              <ul className="space-y-1">
                {result.issues.map((issue, i) => (
                  <li
                    key={i}
                    style={{
                      fontSize:     '0.62rem',
                      color:        '#fca5a5',
                      background:   '#1a0a0a',
                      borderLeft:   '3px solid #dc2626',
                      padding:      '4px 8px',
                      borderRadius: '4px',
                    }}
                  >
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.reportPath && (
            <div className="flex gap-2">
              <a
                href={`http://localhost:8000/api/download-walkthrough?path=${encodeURIComponent(result.reportPath)}`}
                download="validation_report.md"
                style={{
                  fontSize:       '0.62rem',
                  padding:        '4px 10px',
                  background:     '#1a2e1a',
                  border:         '1px solid #1a4d1a',
                  borderRadius:   '4px',
                  color:          '#94a3b8',
                  textDecoration: 'none',
                }}
              >
                ⬇ Download report
              </a>
            </div>
          )}

          <details style={{ fontSize: '0.62rem' }}>
            <summary
              style={{
                cursor:     'pointer',
                color:      '#64748b',
                padding:    '4px 0',
                userSelect: 'none',
              }}
            >
              View full Markdown report
            </summary>
            <pre
              style={{
                marginTop:    '6px',
                whiteSpace:   'pre-wrap',
                wordBreak:    'break-word',
                fontFamily:   'monospace',
                fontSize:     '0.6rem',
                color:        '#94a3b8',
                padding:      '10px',
                background:   '#0a140a',
                border:       '1px solid #111a11',
                borderRadius: '6px',
                maxHeight:    '320px',
                overflowY:    'auto',
                lineHeight:   1.6,
              }}
            >
              {result.report}
            </pre>
          </details>
        </div>
      )}
    </section>
  )
}

// ── Integration Card ──────────────────────────────────────────────────────────

function IntegrationCard({ result }: { result: IntegrationResult }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <section
      style={{
        background:   'linear-gradient(135deg, #0a1a20 0%, #0d1f28 100%)',
        border:       '1px solid #1a3d5e',
        borderRadius: '10px',
        padding:      '12px',
        boxShadow:    '0 0 20px rgba(0,200,255,0.06)',
      }}
    >
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(v => !v)}
      >
        <div className="flex items-center gap-2">
          <span style={{ fontSize: '14px' }}>🔗</span>
          <span
            style={{
              fontSize:      '0.65rem',
              fontWeight:    700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color:         '#67e8f9',
            }}
          >
            Integration Layer
          </span>
          <span
            style={{
              fontSize:     '0.58rem',
              color:        '#6b7280',
              background:   '#0a1a20',
              border:       '1px solid #1a3d5e',
              borderRadius: '3px',
              padding:      '1px 5px',
            }}
          >
            {result.files.length} file(s)
          </span>
        </div>
        <span className="text-[0.6rem] text-muted">{expanded ? '▲' : '▼'}</span>
      </div>

      {expanded && (
        <div style={{ marginTop: '10px' }} className="space-y-3">
          {result.files.length > 0 && (
            <div>
              <div className="text-[0.58rem] uppercase tracking-widest text-muted mb-1">
                Generated Files
              </div>
              <ul className="space-y-0.5">
                {result.files.map((f, i) => (
                  <li
                    key={i}
                    style={{
                      fontSize:   '0.62rem',
                      color:      '#94a3b8',
                      fontFamily: 'monospace',
                    }}
                  >
                    <span style={{ color: '#67e8f9' }}>▸</span> {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.notes.length > 0 && (
            <div>
              <div className="text-[0.58rem] uppercase tracking-widest text-muted mb-1">
                Integration Notes
              </div>
              <ul className="space-y-1">
                {result.notes.map((n, i) => (
                  <li
                    key={i}
                    style={{
                      fontSize:     '0.62rem',
                      color:        '#94a3b8',
                      background:   '#0a1520',
                      borderLeft:   '3px solid #0891b2',
                      padding:      '4px 8px',
                      borderRadius: '4px',
                    }}
                  >
                    {n}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
