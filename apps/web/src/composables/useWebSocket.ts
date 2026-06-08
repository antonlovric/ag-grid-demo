import { ref, onUnmounted, type Ref } from 'vue'

const INITIAL_RECONNECT_DELAY = 1_000
const MAX_RECONNECT_DELAY = 30_000

export interface WsMessage {
  type: string
  timestamp: string
  count: number
}

export function useWebSocket(): { isConnected: Ref<boolean>; lastMessage: Ref<WsMessage | null> } {
  const isConnected = ref(false)
  const lastMessage = ref<WsMessage | null>(null)

  let ws: WebSocket | null = null
  let reconnectDelay = INITIAL_RECONNECT_DELAY
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let stopped = false

  function connect(): void {
    const url = `ws://${window.location.host}/api/ws`
    ws = new WebSocket(url)

    ws.onopen = () => {
      console.log('[WS] Connected')
      isConnected.value = true
      reconnectDelay = INITIAL_RECONNECT_DELAY
    }

    ws.onmessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data as string) as WsMessage
      console.log('[WS] Message:', data)
      lastMessage.value = data
    }

    ws.onclose = () => {
      isConnected.value = false
      if (!stopped) {
        console.log(`[WS] Disconnected. Reconnecting in ${reconnectDelay}ms…`)
        reconnectTimer = setTimeout(() => {
          connect()
        }, reconnectDelay)
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_RECONNECT_DELAY)
      }
    }

    ws.onerror = (event: Event) => {
      console.error('[WS] Error:', event)
    }
  }

  function disconnect(): void {
    stopped = true
    if (reconnectTimer !== null) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    ws?.close()
  }

  connect()
  onUnmounted(disconnect)

  return { isConnected, lastMessage }
}
