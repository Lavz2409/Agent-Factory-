import { useEditorStore } from '@/store/editorStore'

const EXT_ICON: Record<string, string> = {
  py: '🐍', ts: '🔷', tsx: '⚛', js: '🟨', jsx: '⚛',
  json: '{}', md: '📄', sh: '💻', css: '🎨', html: '🌐',
  txt: '📝', yaml: '⚙', yml: '⚙',
}

function fileIcon(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() ?? ''
  return EXT_ICON[ext] ?? '📄'
}

function shortName(path: string): string {
  return path.split('/').pop() ?? path
}

export default function FileTabs() {
  const { tabs, activeTab, files, openTab, closeTab } = useEditorStore()

  if (tabs.length === 0) {
    return (
      <div className="flex items-center px-3 h-8 border-b border-[#1e1e32] text-[0.65rem] text-muted">
        No files generated yet
      </div>
    )
  }

  return (
    <div className="flex items-center overflow-x-auto border-b border-[#1e1e32] bg-surface shrink-0 scrollbar-none h-8">
      {tabs.map(path => {
        const active   = path === activeTab
        const modified = files[path]?.modified
        return (
          <div
            key={path}
            onClick={() => openTab(path)}
            className={[
              'flex items-center gap-1 px-3 h-full shrink-0 cursor-pointer',
              'text-[0.68rem] border-r border-[#1e1e32] transition-colors',
              active
                ? 'bg-bg text-text border-t-2 border-t-accent'
                : 'text-muted hover:text-text hover:bg-[#1a1a2e]',
            ].join(' ')}
          >
            <span>{fileIcon(path)}</span>
            <span className="max-w-[100px] truncate">{shortName(path)}</span>
            {modified && <span className="text-accent text-xs">●</span>}
            <button
              onClick={e => { e.stopPropagation(); closeTab(path) }}
              className="ml-1 hover:text-error text-muted text-xs leading-none"
              title="Close"
            >
              ×
            </button>
          </div>
        )
      })}
    </div>
  )
}
