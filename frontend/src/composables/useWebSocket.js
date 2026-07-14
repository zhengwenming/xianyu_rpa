import { ref, onUnmounted } from 'vue'

export function useWebSocket(url = '/ws/logs') {
  const ws = ref(null)
  const connected = ref(false)
  const messages = ref([])
  const onMessageCallbacks = []

  function connect() {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) return
    try {
      // 桌面 App 环境（file:// 或无 host）直连本地后端
      let wsUrl
      if (window.location.protocol === 'file:' || !window.location.host) {
        wsUrl = `ws://localhost:8765${url}`
      } else {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        wsUrl = `${protocol}//${window.location.host}${url}`
      }
      ws.value = new WebSocket(wsUrl)

      ws.value.onopen = () => {
        connected.value = true
      }

      ws.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          messages.value.push(data)
          onMessageCallbacks.forEach(cb => cb(data))
          // 限制消息数量
          if (messages.value.length > 500) {
            messages.value = messages.value.slice(-500)
          }
        } catch (e) {
          console.warn('WS parse error:', e)
        }
      }

      ws.value.onclose = () => {
        connected.value = false
        // 自动重连
        setTimeout(() => connect(), 3000)
      }

      ws.value.onerror = () => {
        connected.value = false
      }
    } catch (e) {
      console.error('WS connect error:', e)
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    connected.value = false
  }

  function send(data) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }

  function onMessage(callback) {
    onMessageCallbacks.push(callback)
    return () => {
      const idx = onMessageCallbacks.indexOf(callback)
      if (idx >= 0) onMessageCallbacks.splice(idx, 1)
    }
  }

  function clearMessages() {
    messages.value = []
  }

  onUnmounted(() => disconnect())

  return {
    ws,
    connected,
    messages,
    connect,
    disconnect,
    send,
    onMessage,
    clearMessages,
  }
}