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
      <div v-if="task.status === 'failed' && task.error_message" class="error-box">
        <el-icon class="error-icon"><WarningFilled /></el-icon>
        <span class="error-text">{{ task.error_message }}</span>
      </div>
    </div>
    <div class="card-actions">
      <slot name="actions" :task="task" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { WarningFilled } from '@element-plus/icons-vue'

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
.error-box {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 10px;
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.3);
  border-radius: 6px;
}
.error-icon { color: #f56c6c; margin-top: 1px; flex-shrink: 0; }
.error-text { font-size: 12px; color: #f56c6c; line-height: 1.5; word-break: break-all; }
.card-actions { display: flex; gap: 6px; flex-wrap: wrap; }
</style>