import { useState } from 'react'
import { useEditorStore } from '@/store/editorStore'

/**
 * CodeUpload — top-right header button.
 *
 * Opens a popover that lets the user enter a local folder path and saves ALL
 * generated files (code + walkthrough.md) to it via POST /api/save-files.
 * Files are sourced from editorStore, which accumulates every file event
 * emitted by the pipeline WebSocket.
 */
export default function CodeUpload() {
  const [showPanel, setShowPanel]   = useState(false)
  const [folder, setFolder]         = useState('')
  const [uploadStatus, setStatus]   = useState('')
  const [isUploading, setUploading] = useState(false)

  const editorFiles = useEditorStore(s => s.files)
  const fileCount   = Object.keys(editorFiles).length

  const handleUpload = async () => {
    if (!folder.trim()) {
      setStatus('❌ Enter a folder path first.')
      return
    }

    const files = Object.values(editorFiles).map(entry => ({
      filename: entry.path,
      content:  entry.content,
    }))

    if (files.length === 0) {
      setStatus('❌ Run the pipeline first — no files to save yet.')
      return
    }

    setUploading(true)
    setStatus('')
    try {
      const res  = await fetch('http://localhost:8000/api/save-files', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ output_dir: folder.trim(), files }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail ?? 'Unknown error')
      setStatus(`✅ ${data.count} file(s) saved to: ${data.output_dir}`)
    } catch (err: unknown) {
      setStatus(`❌ ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setUploading(false)
    }
  }

  const fileNames = Object.keys(editorFiles)

  return (
    <div style={{ position: 'relative' }}>

      {/* Toggle button */}
      <button
        onClick={() => { setShowPanel(p => !p); setStatus('') }}
        style={{
          padding:      '6px 14px',
          background:   '#1e293b',
          color:        '#94a3b8',
          border:       '1px solid #334155',
          borderRadius: '6px',
          cursor:       'pointer',
          fontFamily:   'monospace',
          fontSize:     '13px',
        }}
        title="Save all generated files to a local folder"
      >
        ⬆️ Upload to Folder
      </button>

      {/* Popover panel */}
      {showPanel && (
        <div style={{
          position:     'absolute',
          top:          '40px',
          right:        0,
          background:   '#1e1e1e',
          border:       '1px solid #334155',
          borderRadius: '8px',
          padding:      '16px',
          width:        '360px',
          zIndex:       1000,
          boxShadow:    '0 8px 32px rgba(0,0,0,0.5)',
        }}>
          <p style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '8px' }}>
            {fileCount > 0
              ? `📁 ${fileCount} file(s) ready: ${fileNames.slice(0, 5).join(', ')}${fileNames.length > 5 ? ` +${fileNames.length - 5} more` : ''}`
              : 'Run the pipeline first to generate files.'}
          </p>
          <input
            type="text"
            value={folder}
            onChange={e => setFolder(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleUpload()}
            placeholder="e.g. C:\Projects\MyAgent"
            style={{
              width:        '100%',
              padding:      '8px',
              background:   '#0f172a',
              color:        '#e2e8f0',
              border:       '1px solid #475569',
              borderRadius: '4px',
              fontFamily:   'monospace',
              fontSize:     '12px',
              boxSizing:    'border-box',
              outline:      'none',
            }}
          />
          <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
            <button
              onClick={handleUpload}
              disabled={isUploading || fileCount === 0}
              style={{
                flex:         1,
                padding:      '8px',
                background:   isUploading ? '#374151' : fileCount === 0 ? '#1e2940' : '#065f46',
                color:        fileCount === 0 ? '#475569' : '#fff',
                border:       'none',
                borderRadius: '4px',
                cursor:       isUploading || fileCount === 0 ? 'not-allowed' : 'pointer',
                fontFamily:   'monospace',
                fontSize:     '12px',
              }}
            >
              {isUploading ? '⏳ Saving...' : `💾 Save ${fileCount > 0 ? fileCount : ''} Files`}
            </button>
            <button
              onClick={() => setShowPanel(false)}
              style={{
                padding:      '8px 12px',
                background:   '#1e293b',
                color:        '#94a3b8',
                border:       '1px solid #334155',
                borderRadius: '4px',
                cursor:       'pointer',
                fontFamily:   'monospace',
                fontSize:     '12px',
              }}
            >
              ✕
            </button>
          </div>
          {uploadStatus && (
            <p style={{
              marginTop: '8px',
              fontSize:  '11px',
              color:     uploadStatus.startsWith('✅') ? '#4ade80' : '#f87171',
            }}>
              {uploadStatus}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
