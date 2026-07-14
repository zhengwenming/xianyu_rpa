<template>
  <div class="task-card">
    <div class="card-header">
      <span class="task-name">{{ task.name }}</span>
      <el-tag :type="statusType" size="small">{{ statusLabel }}</el-tag>
    </div>
    <div class="card-body">
      <div class="info-row">
        <span class="label">店铺</span>
        <span class="value">{{ task.shop_name || '-' }}</span>
      </div>
      <div class="info-row">
        <span class="label">进度</span>
        <span class="value">{{ task.current_count }} / {{ task.target_count }}</span>
      </div>
      <el-progress :percentage="progressPercent" :status="progressStatus" :stroke-width="8" />
      <div class="info-row" style="margin-top: 8px;">
        <span class="label">创建时间</span>
        <span class="value">{{ formatTime(task.created_at) }}</span>
      </div>
    </div>
    <div class="card-actions">
      <slot name="actions" :task="task" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  task: { type: Object, required: true },
})

const statusType = computed(() => {
  const map = { running: 'primary', paused: 'warning', pending: 'info', cancelled: 'danger', completed: 'success', failed: 'danger' }
  return map[props.task.status] || 'info'
})

const statusLabel = computed(() => {
  const map = { running: '运行中', paused: '已暂停', pending: '等待中', cancelled: '已取消', completed: '已完成', failed: '失败' }
  return map[props.task.status] || props.task.status
})

const progressPercent = computed(() => {
  if (props.task.target_count === 0) return 0
  return Math.round(props.task.current_count / props.task.target_count * 100)
})

const progressStatus = computed(() => {
  if (props.task.status === 'completed') return 'success'
  if (props.task.status === 'failed') return 'exception'
  return ''
})

function formatTime(ts) {
  if (!ts) return '-'
  return new Date(ts).toLocaleString('zh-CN')
}
</script>

<style scoped>
.task-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.task-name { font-size: 15px; font-weight: 600; }
.card-body { margin-bottom: 12px; }
.info-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; }
.info-row .label { color: var(--text-secondary); }
.info-row .value { color: var(--text-primary); }
.card-actions { display: flex; gap: 6px; flex-wrap: wrap; }
</style>