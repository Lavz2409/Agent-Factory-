import { useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Folder, FolderOpen, FileCode, FlaskConical,
  FileText, FileJson, File, Settings,
} from 'lucide-react'
import { useEditorStore } from '@/store/editorStore'

interface TreeNode {
  name:     string
  path:     string
  isFile:   boolean
  children: TreeNode[]
}

function buildTree(paths: string[]): TreeNode[] {
  const root: TreeNode[] = []
  for (const path of paths) {
    const parts = path.split('/')
    let nodes   = root
    let cumPath = ''
    for (let i = 0; i < parts.length; i++) {
      cumPath = cumPath ? `${cumPath}/${parts[i]}` : parts[i]
      const isFile = i === parts.length - 1
      let node = nodes.find(n => n.name === parts[i])
      if (!node) {
        node = { name: parts[i], path: cumPath, isFile, children: [] }
        nodes.push(node)
      }
      nodes = node.children
    }
  }
  return root
}

function fileIcon(name: string): React.ReactElement {
  const lower = name.toLowerCase()
  const ext   = lower.split('.').pop() ?? ''

  if (lower.startsWith('test_') || lower.includes('.test.') || lower.includes('.spec.'))
    return <FlaskConical size={12} className="text-amber-400/80" />
  if (lower === 'walkthrough.md' || lower === 'readme.md')
    return <FileText size={12} className="text-purple-400/80" />
  if (ext === 'md')   return <FileText size={12} className="text-slate-400/80" />
  if (ext === 'json') return <FileJson size={12} className="text-yellow-400/80" />
  if (ext === 'py')   return <FileCode size={12} className="text-blue-400/80" />
  if (ext === 'ts' || ext === 'tsx') return <FileCode size={12} className="text-cyan-400/80" />
  if (ext === 'js' || ext === 'jsx') return <FileCode size={12} className="text-yellow-300/80" />
  if (ext === 'sh' || ext === 'env' || ext === 'toml' || ext === 'cfg' || ext === 'ini')
    return <Settings size={12} className="text-orange-400/80" />
  return <File size={12} className="text-slate-500/70" />
}

function TreeItem({ node, depth = 0 }: { node: TreeNode; depth?: number }) {
  const [open, setOpen]        = useState(true)
  const { openTab, activeTab } = useEditorStore()
  const isActive               = activeTab === node.path

  return (
    <div>
      <motion.div
        whileHover={{ x: 2 }}
        transition={{ duration: 0.1 }}
        onClick={() => {
          if (node.isFile) openTab(node.path)
          else setOpen(o => !o)
        }}
        className={[
          'flex items-center gap-1.5 py-1 cursor-pointer text-[0.7rem] rounded-md transition-all',
          isActive
            ? 'border-l-2 border-cyan-400 bg-cyan-500/8 text-white'
            : 'text-slate-500 hover:text-slate-200 hover:bg-white/4 border-l-2 border-transparent',
        ].join(' ')}
        style={{ paddingLeft: `${10 + depth * 14}px`, paddingRight: '8px' }}
      >
        {/* Icon */}
        <span className="shrink-0">
          {node.isFile
            ? fileIcon(node.name)
            : open
              ? <FolderOpen size={12} className="text-amber-400/70" />
              : <Folder     size={12} className="text-amber-400/50" />
          }
        </span>

        {/* Name */}
        <span className="truncate flex-1 font-mono" style={{ fontSize: '0.68rem' }}>
          {node.name}
        </span>

        {/* Active dot */}
        {isActive && (
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
        )}
      </motion.div>

      {/* Children with animation */}
      <AnimatePresence initial={false}>
        {!node.isFile && open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.15 }}
          >
            {node.children.map(c => (
              <TreeItem key={c.path} node={c} depth={depth + 1} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function FileExplorer() {
  const files = useEditorStore(s => s.files)
  const tree  = useMemo(() => buildTree(Object.keys(files)), [files])

  return (
    <div className="h-full overflow-y-auto py-2">
      <div className="px-3 pb-2 flex items-center gap-1.5">
        <Folder size={10} className="text-muted" />
        <span className="text-[0.58rem] font-semibold uppercase tracking-widest text-muted">
          Files
        </span>
        {Object.keys(files).length > 0 && (
          <span className="ml-auto text-[0.55rem] text-muted/60 tabular-nums">
            {Object.keys(files).length}
          </span>
        )}
      </div>

      <AnimatePresence>
        {tree.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="px-3 text-[0.65rem] text-muted/50 italic"
          >
            No files yet
          </motion.div>
        ) : (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            {tree.map(node => <TreeItem key={node.path} node={node} />)}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
