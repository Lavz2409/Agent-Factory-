/**
 * SettingsButton — gear icon that opens the SettingsPanel.
 *
 * The header renders ONE of these (see MainLayout) and holds the open/close
 * state. Placed in the top-right corner of the app, as per SaaS convention.
 */
import { motion } from 'framer-motion'
import { Settings as SettingsIcon } from 'lucide-react'

interface SettingsButtonProps {
  onClick: () => void
  open:    boolean
}

export default function SettingsButton({ onClick, open }: SettingsButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      aria-label="Open settings"
      aria-haspopup="dialog"
      aria-expanded={open}
      title="Settings"
      className="flex items-center justify-center w-9 h-9 rounded-lg transition-colors"
      style={{
        background:  open
          ? 'rgba(99,102,241,0.18)'
          : 'rgba(255,255,255,0.03)',
        border:      `1px solid ${open ? 'rgba(99,102,241,0.45)' : 'rgba(255,255,255,0.06)'}`,
        color:       open ? '#a78bfa' : '#9ca3af',
        boxShadow:   open ? '0 0 12px rgba(99,102,241,0.22)' : 'none',
      }}
    >
      <motion.span
        animate={{ rotate: open ? 90 : 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 22 }}
        className="flex"
      >
        <SettingsIcon size={15} />
      </motion.span>
    </motion.button>
  )
}
