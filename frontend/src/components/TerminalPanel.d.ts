import type { FC } from 'react'

interface TerminalPanelProps {
  runCommands?: string[]
  wsUrl?: string
}

declare const TerminalPanel: FC<TerminalPanelProps>
export default TerminalPanel
