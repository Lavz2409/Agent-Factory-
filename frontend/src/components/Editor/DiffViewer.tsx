import { useState } from 'react'
import { DiffEditor } from '@monaco-editor/react'
import { useEditorStore } from '@/store/editorStore'

/**
 * DiffViewer — side-by-side Monaco diff view.
 * Left = original (last saved content), right = current (possibly modified).
 */
export default function DiffViewer() {
  const { activeTab, files }         = useEditorStore()
  const [originals]                  = useState<Record<string, string>>({})

  const file = activeTab ? files[activeTab] : null

  if (!file) {
    return (
      <div className="flex items-center justify-center h-full bg-bg text-muted text-sm">
        Open a file to view diff
      </div>
    )
  }

  const orig = originals[activeTab] ?? file.content
  const curr = file.content

  return (
    <div className="h-full flex flex-col">
      <div className="flex gap-4 px-4 py-1.5 border-b border-[#1e1e32] text-[0.62rem] text-muted shrink-0">
        <span className="text-error">← Original</span>
        <span className="text-success">Modified →</span>
      </div>
      <div className="flex-1 min-h-0">
        <DiffEditor
          height="100%"
          original={orig}
          modified={curr}
          language={file.language}
          theme="vs-dark"
          options={{
            fontSize:         13,
            fontFamily:       "'JetBrains Mono', monospace",
            renderSideBySide: true,
            minimap:          { enabled: false },
            automaticLayout:  true,
            readOnly:         true,
          }}
        />
      </div>
    </div>
  )
}
