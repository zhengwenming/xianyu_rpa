<template>
  <div class="log-viewer">
    <div class="log-toolbar">
      <el-select v-model="levelFilter" multiple placeholder="级别过滤" size="small" style="width: 120px">
        <el-option label="信息" value="info" />
        <el-option label="警告" value="warning" />
        <el-option label="错误" value="error" />
        <el-option label="调试" value="debug" />
      </el-select>
      <el-input v-model="searchText" placeholder="搜索关键字" size="small" style="width: 150px" clearable />
      <el-button size="small" @click="autoScroll = !autoScroll">{{ autoScroll ? '自动滚动' : '已暂停' }}</el-button>
      <el-button size="small" @click="clearLogs">清空</el-button>
      <el-button size="small" @click="exportLogs">导出</el-button>
    </div>
    <div class="log-list" ref="logContainer">
      <div v-for="(log, idx) in filteredLogs" :key="idx" class="log-item" :class="'log-' + log.level">
        <span class="log-time">{{ formatTime(log.timestamp) }}</span>
        <span class="log-level" :class="'level-' + log.level">[{{ log.level.toUpperCase() }}]</span>
        <span class="log-msg">{{ log.message }}</span>
      </div>
      <div v-if="filteredLogs.length === 0" class="log-empty">暂无日志</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useWebSocket } from '../composables/useWebSocket'

const { messages, connect, clearMessages, send } = useWebSocket('/ws/logs')
const logContainer = ref(null)
const autoScroll = ref(true)
const levelFilter = ref([])
const searchText = ref('')

connect()

const filteredLogs = computed(() => {
  let logs = messages.value
  if (levelFilter.value.length > 0) {
    logs = logs.filter(l => levelFilter.value.includes(l.level))
  }
  if (searchText.value) {
    const kw = searchText.value.toLowerCase()
    logs = logs.filter(l => l.message.toLowerCase().includes(kw))
  }
  return logs
})

watch(filteredLogs, () => {
  if (autoScroll.value) {
    nextTick(() => {
      if (logContainer.value) {
        logContainer.value.scrollTop = logContainer.value.scrollHeight
      }
    })
  }
})

function formatTime(ts) {
  if (!ts) return ''
  try {
    return new Date(ts).toLocaleTimeString()
  } catch { return ts }
}

function clearLogs() {
  clearMessages()
}

function exportLogs() {
  const text = filteredLogs.value.map(l => `[${l.timestamp}] [${l.level.toUpperCase()}] ${l.message}`).join('\n')
  const blob = new Blob([text], { type: 'text/plain' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `logs_${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
}
</script>

<style scoped>
.log-viewer { height: 100%; display: flex; flex-direction: column; }
.log-toolbar { display: flex; gap: 8px; padding: 8px; background: #16213e; border-bottom: 1px solid #2a3a5a; flex-wrap: wrap; }
.log-list { flex: 1; overflow-y: auto; padding: 8px; font-family: 'Menlo', 'Monaco', monospace; font-size: 12px; }
.log-item { padding: 2px 4px; border-bottom: 1px solid rgba(42, 58, 90, 0.3); word-break: break-all; }
.log-time { color: #666; margin-right: 8px; }
.log-level { font-weight: bold; margin-right: 8px; }
.log-msg { color: #ccc; }
.level-info .log-msg { color: #ccc; }
.level-warning .log-msg { color: #ffa726; }
.level-error .log-msg { color: #ef5350; }
.level-debug .log-msg { color: #666; }
.log-empty { text-align: center; color: #666; padding: 40px; }
</style>