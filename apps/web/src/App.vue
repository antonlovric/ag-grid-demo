<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useWebSocket } from './composables/useWebSocket'
import TradesGrid from './components/TradesGrid.vue'

const health = ref<string>('checking...')
const { isConnected } = useWebSocket()

onMounted(async () => {
  try {
    const res = await fetch('/api/health')
    const data = await res.json()
    health.value = data.status
  } catch {
    health.value = 'error'
  }
})
</script>

<template>
  <div class="app">
    <header>
      <span class="title">ag-grid-demo</span>
      <span class="status">API: {{ health }} | WS: {{ isConnected ? 'connected' : 'disconnected' }}</span>
    </header>
    <TradesGrid />
  </div>
</template>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, #app { height: 100%; }

.app {
  display: flex;
  flex-direction: column;
  height: 100%;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #1a1a2e;
  color: #e0e0e0;
  font-family: monospace;
  font-size: 13px;
  flex-shrink: 0;
}

.title {
  font-weight: bold;
  letter-spacing: 0.5px;
}

.status {
  opacity: 0.7;
  font-size: 11px;
}
</style>
