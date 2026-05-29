import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

interface Props {
  title?:     string
  children:   ReactNode
  className?: string
  noPad?:     boolean
  accent?:    boolean
}

export default function GlassmorphPanel({ title, children, className = '', noPad = false, accent = false }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={[
        'flex flex-col rounded-xl overflow-hidden',
        'bg-[rgba(19,19,31,0.85)] backdrop-blur-md',
        accent
          ? 'border border-accent/30 shadow-[0_0_20px_rgba(0,217,255,0.08)]'
          : 'border border-[#1e1e32]',
        className,
      ].join(' ')}
    >
      {title && (
        <div className="flex items-center gap-2 px-4 py-2 border-b border-[#1e1e32] bg-[#0f0f1e]/60 shrink-0">
          <span className="text-[0.65rem] font-semibold uppercase tracking-widest text-[#4a4a6a]">
            {title}
          </span>
        </div>
      )}
      <div className={['flex-1 min-h-0', noPad ? '' : 'p-3'].join(' ')}>
        {children}
      </div>
    </motion.div>
  )
}
