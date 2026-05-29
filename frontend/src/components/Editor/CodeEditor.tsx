import MonacoEditor from '@monaco-editor/react'
import { useEditorStore } from '@/store/editorStore'
import { useMonaco } from '@/hooks/useMonaco'

export default function CodeEditor() {
  const { activeTab, files, updateFile } = useEditorStore()
  const { onEditorMount }                = useMonaco()

  const file = activeTab ? files[activeTab] : null

  if (!file) {
    return (
      <div className="flex items-center justify-center h-full bg-bg text-muted text-sm">
        <div className="text-center space-y-2">
          <div className="text-4xl opacity-20">⚙</div>
          <p className="text-[0.75rem]">Run a build to generate files</p>
        </div>
      </div>
    )
  }

  return (
    <MonacoEditor
      height="100%"
      language={file.language}
      value={file.content}
      theme="vs-dark"
      onMount={onEditorMount}
      onChange={value => { if (value !== undefined) updateFile(activeTab, value) }}
      options={{
        fontSize:            13,
        fontFamily:          "'JetBrains Mono', 'Fira Code', monospace",
        fontLigatures:       true,
        lineNumbers:         'on',
        minimap:             { enabled: false },
        scrollBeyondLastLine: false,
        wordWrap:            'on',
        tabSize:             4,
        renderWhitespace:    'selection',
        automaticLayout:     true,
        padding:             { top: 12, bottom: 12 },
        overviewRulerLanes:  0,
        scrollbar:           { vertical: 'hidden', horizontal: 'auto' },
        cursorBlinking:      'phase',
        smoothScrolling:     true,
        bracketPairColorization: { enabled: true },
      }}
    />
  )
}
