import { useEffect, useRef, useCallback } from 'react'
import type { PipelineEvent } from '@/types'

type Handler = (event: PipelineEvent) => void

interface Options {
  onEvent:       Handler
  onOpen?:       () => void
  onClose?:      () => void
  onError?:      (e: Event) => void
  reconnectMs?:  number
  maxRetries?:   number
}

export function useWebSocket(url: string | null, opts: Options) {
  const wsRef      = useRef<WebSocket | null>(null)
  const retryCount = useRef(0)
  const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const optsRef    = useRef(opts)
  optsRef.current  = opts   // always have latest handlers without re-subscribing

  const reconnectMs = opts.reconnectMs ?? 2000
  const maxRetries  = opts.maxRetries  ?? 5

  const connect = useCallback(() => {
    if (!url) return
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      retryCount.current = 0
      optsRef.current.onOpen?.()
    }

    ws.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data) as PipelineEvent
        if (event.type === 'ping') return
        optsRef.current.onEvent(event)
      } catch {
        // Malformed frame — ignore
      }
    }

    ws.onerror = (e) => optsRef.current.onError?.(e)

    ws.onclose = () => {
      optsRef.current.onClose?.()
      if (retryCount.current < maxRetries) {
        retryCount.current++
        retryTimer.current = setTimeout(connect, reconnectMs)
      }
    }
  }, [url, reconnectMs, maxRetries])

  useEffect(() => {
    if (!url) return
    connect()
    return () => {
      if (retryTimer.current) clearTimeout(retryTimer.current)
      wsRef.current?.close()
    }
  }, [url, connect])

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  const close = useCallback(() => {
    if (retryTimer.current) clearTimeout(retryTimer.current)
    retryCount.current = maxRetries   // prevent auto-reconnect
    wsRef.current?.close()
  }, [maxRetries])

  return { send, close }
}
