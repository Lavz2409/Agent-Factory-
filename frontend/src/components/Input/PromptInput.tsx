import { useState, useRef, type KeyboardEvent } from 'react'
import { motion } from 'framer-motion'

interface Props {
  onRun:    (requirement: string) => void
  running:  boolean
}

const EXAMPLES = [
  'Build a REST API for a todo app with SQLite and FastAPI',
  'Create a React dashboard with charts and dark theme',
  'Write a CLI tool to scrape news and summarize with AI',
  'Build a Discord bot that answers coding questions',
]

export default function PromptInput({ onRun, running }: Props) {
  const [text, setText]   = useState('')
  const [hint, setHint]   = useState(false)
  const textareaRef       = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    if (running || !text.trim()) return
    onRun(text.trim())
  }

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="text-[0.6rem] uppercase tracking-widest text-muted">Build Requirement</div>
      <div className={[
        'relative rounded-lg border transition-colors',
        running
          ? 'border-accent/40 shadow-[0_0_12px_rgba(0,217,255,0.12)]'
          : 'border-[#1e1e32] hover:border-[#2e2e4a]',
      ].join(' ')}>
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={onKey}
          disabled={running}
          rows={4}
          placeholder="Describe the app you want to build…&#10;&#10;Ctrl+Enter to run"
          className={[
            'w-full bg-transparent text-[0.75rem] text-text placeholder-muted',
            'resize-none px-3 pt-3 pb-8 outline-none rounded-lg font-mono leading-5',
            running ? 'opacity-50 cursor-not-allowed' : '',
          ].join(' ')}
        />
        <button
          onClick={submit}
          disabled={running || !text.trim()}
          className={[
            'absolute bottom-2 right-2 flex items-center gap-1.5',
            'text-[0.65rem] font-semibold px-3 py-1 rounded-md transition-all',
            running || !text.trim()
              ? 'bg-[#1e1e32] text-muted cursor-not-allowed'
              : 'bg-accent text-bg hover:bg-accent/80 shadow-[0_0_8px_rgba(0,217,255,0.4)]',
          ].join(' ')}
        >
          {running ? (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-current animate-ping" />
              Running…
            </>
          ) : (
            <>▶ Build</>
          )}
        </button>
      </div>

      {/* quick examples */}
      <button
        onClick={() => setHint(h => !h)}
        className="text-[0.6rem] text-muted hover:text-textDim text-left"
      >
        {hint ? '▾ Hide examples' : '▸ Show examples'}
      </button>
      {hint && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="space-y-1"
        >
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => { setText(ex); setHint(false) }}
              className="w-full text-left text-[0.65rem] text-muted hover:text-accent px-2 py-1 rounded hover:bg-accent/5 transition-colors border border-transparent hover:border-accent/20"
            >
              {ex}
            </button>
          ))}
        </motion.div>
      )}
    </div>
  )
}
