import { create } from 'zustand'
import type { FileEntry } from '@/types'

const LANG_MAP: Record<string, string> = {
  py:   'python',
  ts:   'typescript',
  tsx:  'typescript',
  js:   'javascript',
  jsx:  'javascript',
  json: 'json',
  md:   'markdown',
  sh:   'shell',
  txt:  'plaintext',
  yaml: 'yaml',
  yml:  'yaml',
  html: 'html',
  css:  'css',
}

function detectLanguage(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() ?? ''
  return LANG_MAP[ext] ?? 'plaintext'
}

interface EditorStore {
  files:        Record<string, FileEntry>
  tabs:         string[]
  activeTab:    string
  selectedFile: string | null
  // actions
  addFile:       (path: string, content: string) => void
  updateFile:    (path: string, content: string) => void
  openTab:       (path: string) => void
  closeTab:      (path: string) => void
  setActiveTab:  (path: string) => void
  selectFile:    (path: string | null) => void
  clearFiles:    () => void
}

export const useEditorStore = create<EditorStore>((set) => ({
  files:        {},
  tabs:         [],
  activeTab:    '',
  selectedFile: null,

  addFile: (path, content) =>
    set(s => {
      const entry: FileEntry = {
        path,
        content,
        language: detectLanguage(path),
        modified: false,
      }
      const tabs = s.tabs.includes(path) ? s.tabs : [...s.tabs, path]
      return {
        files:        { ...s.files, [path]: entry },
        tabs,
        activeTab:    path,
        selectedFile: path,
      }
    }),

  updateFile: (path, content) =>
    set(s => ({
      files: {
        ...s.files,
        [path]: { ...s.files[path], content, modified: true },
      },
    })),

  openTab: (path) =>
    set(s => ({
      tabs:      s.tabs.includes(path) ? s.tabs : [...s.tabs, path],
      activeTab: path,
    })),

  closeTab: (path) =>
    set(s => {
      const tabs     = s.tabs.filter(t => t !== path)
      const activeTab = s.activeTab === path
        ? (tabs[tabs.length - 1] ?? '')
        : s.activeTab
      return { tabs, activeTab }
    }),

  setActiveTab:  (path) => set({ activeTab: path }),
  selectFile:    (path) => set({ selectedFile: path }),
  clearFiles:    ()     => set({ files: {}, tabs: [], activeTab: '', selectedFile: null }),
}))
