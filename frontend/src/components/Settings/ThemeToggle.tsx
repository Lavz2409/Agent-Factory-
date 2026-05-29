/**
 * ThemeToggle — 3-way segmented control: Light · System · Dark
 *
 * • Uses framer-motion's `layoutId` for a buttery sliding indicator.
 * • Fully keyboard-navigable (arrow keys + tab).
 * • Announces the new theme to screen readers via aria-live in SettingsPanel.
 */
import { motion } from 'framer-motion'
import { Sun, Moon, Monitor } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import type { ThemePreference } from '@/store/themeStore'

const OPTIONS: {
  value: ThemePreference
  label: string
  Icon:  React.ElementType
}[] = [
  { value: 'light',  label: 'Light',  Icon: Sun     },
  { value: 'system', label: 'System', Icon: Monitor },
  { value: 'dark',   label: 'Dark',   Icon: Moon    },
]

export default function ThemeToggle() {
  const { preference, setTheme } = useTheme()

  return (
    <div
      role="radiogroup"
      aria-label="Theme preference"
      className="relative inline-flex items-center gap-1 p-1 rounded-full"
      style={{
        background: 'rgb(var(--color-muted) / 0.6)',
        border:     '1px solid rgb(var(--color-border))',
      }}
    >
      {OPTIONS.map(({ value, label, Icon }) => {
        const selected = preference === value
        return (
          <button
            key={value}
            role="radio"
            aria-checked={selected}
            aria-label={`${label} theme`}
            tabIndex={selected ? 0 : -1}
            onClick={() => setTheme(value)}
            onKeyDown={(e) => {
              // Arrow-key navigation between options
              if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                e.preventDefault()
                const idx  = OPTIONS.findIndex(o => o.value === preference)
                const next = OPTIONS[(idx + 1) % OPTIONS.length]
                setTheme(next.value)
              } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault()
                const idx  = OPTIONS.findIndex(o => o.value === preference)
                const prev = OPTIONS[(idx - 1 + OPTIONS.length) % OPTIONS.length]
                setTheme(prev.value)
              }
            }}
            className="relative z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-full
                       text-xs font-medium transition-colors duration-150 cursor-pointer"
            style={{
              color: selected
                ? 'rgb(var(--color-primary-fg))'
                : 'rgb(var(--color-muted-fg))',
            }}
          >
            {selected && (
              <motion.span
                layoutId="theme-toggle-indicator"
                className="absolute inset-0 rounded-full z-[-1]"
                style={{ background: 'rgb(var(--color-primary))' }}
                transition={{ type: 'spring', stiffness: 500, damping: 36 }}
              />
            )}
            <Icon size={14} />
            {label}
          </button>
        )
      })}
    </div>
  )
}
