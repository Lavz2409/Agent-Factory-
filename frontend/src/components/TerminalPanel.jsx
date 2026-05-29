import { useEffect, useRef, useState } from 'react'

/**
 * TerminalPanel — real WebSocket-backed terminal UI.
 *
 * Props:
 *   runCommands  : string[]  — pre-populated commands from ScribeAgent (optional)
 *   wsUrl        : string    — defaults to ws://localhost:8000/ws/terminal
 */
export default function TerminalPanel({ runCommands = [], wsUrl = 'ws://localhost:8000/ws/terminal' }) {
  const [lines, setLines]   = useState([{ text: '$ Agent Factory Terminal\n', type: 'stdout' }])
  const [input, setInput]   = useState('')
  const [connected, setConnected] = useState(false)
  const wsRef   = useRef(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen  = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onerror = () => setConnected(false)

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data)
        if (msg.stream === 'stdout') {
          setLines(prev => [...prev, { text: msg.data, type: 'stdout' }])
        } else if (msg.stream === 'stderr') {
          setLines(prev => [...prev, { text: msg.data, type: 'stderr' }])
        } else if (msg.stream === 'exit') {
          setLines(prev => [...prev, { text: `[exit ${msg.data}]\n`, type: 'exit' }])
        }
      } catch {
        setLines(prev => [...prev, { text: evt.data + '\n', type: 'stdout' }])
      }
    }

    return () => ws.close()
  }, [wsUrl])

  // Auto-scroll to bottom on new output
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines])

  // Pre-populate input with first run command from ScribeAgent
  useEffect(() => {
    if (runCommands.length > 0 && !input) {
      setInput(runCommands[0])
    }
  }, [runCommands])

  const sendCommand = () => {
    const cmd = input.trim()
    if (!cmd || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    setLines(prev => [...prev, { text: `$ ${cmd}\n`, type: 'cmd' }])
    wsRef.current.send(cmd)
    setInput('')
  }

  const handleKey = (e) => {
    if (e.key === 'Enter') sendCommand()
  }

  const colorFor = (type) => {
    if (type === 'stderr') return '#ff4444'
    if (type === 'exit')   return '#888'
    if (type === 'cmd')    return '#a78bfa'
    return '#00ff41'
  }

  return (
    <div style={{
      background:   '#0d0d0d',
      border:       '1px solid #1e1e32',
      borderRadius: '8px',
      marginTop:    '16px',
      overflow:     'hidden',
      fontFamily:   'monospace',
    }}>
      {/* Header */}
      <div style={{
        background:    '#111',
        padding:       '6px 12px',
        display:       'flex',
        alignItems:    'center',
        justifyContent:'space-between',
        borderBottom:  '1px solid #1e1e32',
      }}>
        <span style={{ color: '#00ff41', fontSize: '12px', fontWeight: 600 }}>
          ▶ Terminal
        </span>
        <span style={{ fontSize: '11px', color: connected ? '#00ff41' : '#ff4444' }}>
          {connected ? '● connected' : '○ disconnected'}
        </span>
        <button
          onClick={() => setLines([{ text: '$ Terminal cleared.\n', type: 'stdout' }])}
          style={{
            background: 'transparent',
            border:     '1px solid #333',
            borderRadius: '4px',
            color:      '#888',
            fontSize:   '11px',
            cursor:     'pointer',
            padding:    '2px 8px',
          }}
        >
          Clear
        </button>
      </div>

      {/* Output area */}
      <div style={{
        maxHeight:  '400px',
        overflowY:  'auto',
        padding:    '12px',
        fontSize:   '13px',
        lineHeight: '1.5',
      }}>
        {lines.map((line, i) => (
          <span key={i} style={{ color: colorFor(line.type), whiteSpace: 'pre-wrap' }}>
            {line.text}
          </span>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input row */}
      <div style={{
        display:      'flex',
        alignItems:   'center',
        gap:          '8px',
        padding:      '8px 12px',
        borderTop:    '1px solid #1e1e32',
        background:   '#0a0a0a',
      }}>
        <span style={{ color: '#00ff41', fontSize: '13px' }}>$</span>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Enter command…"
          style={{
            flex:        1,
            background:  'transparent',
            border:      'none',
            outline:     'none',
            color:       '#00ff41',
            fontFamily:  'monospace',
            fontSize:    '13px',
          }}
        />
        <button
          onClick={sendCommand}
          style={{
            background:   '#00ff4122',
            border:       '1px solid #00ff41',
            borderRadius: '4px',
            color:        '#00ff41',
            fontSize:     '12px',
            cursor:       'pointer',
            padding:      '4px 10px',
          }}
        >
          ▶ Run
        </button>
      </div>
    </div>
  )
}
