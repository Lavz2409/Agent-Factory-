import { useRef, useCallback } from 'react'
import type * as Monaco from 'monaco-editor'

export function useMonaco() {
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null)

  const onEditorMount = useCallback(
    (editor: Monaco.editor.IStandaloneCodeEditor, monaco: typeof Monaco) => {
      editorRef.current = editor

      // Dark futuristic theme
      monaco.editor.defineTheme('agentFactory', {
        base:    'vs-dark',
        inherit: true,
        rules: [
          { token: 'comment',   foreground: '4a4a6a', fontStyle: 'italic' },
          { token: 'keyword',   foreground: '00d9ff' },
          { token: 'string',    foreground: '00ff88' },
          { token: 'number',    foreground: 'ffaa00' },
          { token: 'type',      foreground: 'c792ea' },
          { token: 'function',  foreground: '82aaff' },
          { token: 'variable',  foreground: 'e0e0f0' },
          { token: 'decorator', foreground: 'ff0055' },
        ],
        colors: {
          'editor.background':            '#0f0f1e',
          'editor.foreground':            '#e0e0f0',
          'editor.lineHighlightBackground':'#1a1a2e',
          'editorLineNumber.foreground':   '#3a3a5a',
          'editorCursor.foreground':       '#00d9ff',
          'editor.selectionBackground':    '#00d9ff33',
          'editorIndentGuide.background1': '#1e1e32',
          'scrollbarSlider.background':    '#1e1e3288',
          'scrollbarSlider.hoverBackground':'#2a2a4488',
        },
      })
      monaco.editor.setTheme('agentFactory')

      // Key bindings
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        // Save event — handled by parent via onChange
      })
    },
    []
  )

  const getValue = useCallback(() => editorRef.current?.getValue() ?? '', [])

  const setValue = useCallback((value: string) => {
    editorRef.current?.setValue(value)
  }, [])

  const revealLine = useCallback((line: number) => {
    editorRef.current?.revealLineInCenter(line)
  }, [])

  return { onEditorMount, getValue, setValue, revealLine, editorRef }
}
