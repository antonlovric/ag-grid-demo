<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useWebSocket } from './composables/useWebSocket'

const health = ref<string>('checking...')
const { isConnected, lastMessage } = useWebSocket()

onMounted(async () => {
  try {
    const res = await fetch('/api/health')
    const data = await res.json()
    health.value = data.status
  } catch {
    health.value = 'error — is the API running?'
  }
})
</script>

<template>
  <main>
    <h1>ag-grid-demo</h1>
    <p>API health: <strong>{{ health }}</strong></p>
    <p>WebSocket: <strong>{{ isConnected ? 'connected' : 'disconnected' }}</strong></p>
    <p v-if="lastMessage">Last message: <strong>#{{ lastMessage.count }}</strong> at {{ lastMessage.timestamp }}</p>
  </main>
</template>
