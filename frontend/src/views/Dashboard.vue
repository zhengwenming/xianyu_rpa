<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
    </div>
    <div class="stat-cards">
      <div class="stat-card"><div class="label">今日上架</div><div class="value" style="color:#4fc3f7">{{ todayCount }}</div></div>
      <div class="stat-card"><div class="label">累计上架</div><div class="value" style="color:#66bb6a">{{ totalListed }}</div></div>
      <div class="stat-card"><div class="label">运行中任务</div><div class="value" style="color:#ffa726">{{ runningTasks }}</div></div>
      <div class="stat-card"><div class="label">店铺总数</div><div class="value" style="color:#ab47bc">{{ shopCount }}</div></div>
    </div>
    <el-row :gutter="16">
      <el-col :span="16">
        <el-card>
          <template #header><span>进行中的任务</span></template>
          <div v-if="activeTasks.length === 0" style="text-align:center;padding:40px;color:#666">暂无进行中的任务</div>
          <div v-for="task in activeTasks" :key="task.id" class="task-item">
            <div class="task-info">
              <span>{{ task.name }}</span>
              <el-tag :type="task.status === 'running' ? 'primary' : 'warning'" size="small">{{ task.status === 'running' ? '运行中' : '已暂停' }}</el-tag>
            </div>
            <el-progress :percentage="task.target_count > 0 ? Math.round(task.current_count/task.target_count*100) : 0" :stroke-width="6" />
            <div class="task-progress">{{ task.current_count }}/{{ task.target_count }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span>最近活动</span></template>
          <div v-if="recentLogs.length === 0" style="text-align:center;padding:40px;color:#666">暂无活动记录</div>
          <div v-for="log in recentLogs" :key="log.id" class="log-item">
            <span class="log-time">{{ formatTime(log.timestamp) }}</span>
            <span class="log-msg">{{ log.message }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as taskApi from '../api/task'
import * as listingLogApi from '../api/listingLog'
import * as shopApi from '../api/shop'

const todayCount = ref(0)
const totalListed = ref(0)
const runningTasks = ref(0)
const shopCount = ref(0)
const activeTasks = ref([])
const recentLogs = ref([])

async function loadData() {
  try {
    const [tasksRes, listingRes, shopRes] = await Promise.all([
      taskApi.listTasks({ page: 1, page_size: 100 }),
      listingLogApi.getListingLogSummary(),
      shopApi.listShops(),
    ])
    const tasks = tasksRes.data.data?.items || []
    activeTasks.value = tasks.filter(t => t.status === 'running' || t.status === 'paused')
    runningTasks.value = tasks.filter(t => t.status === 'running').length
    const listingData = listingRes.data.data || {}
    totalListed.value = listingData.total || 0
    shopCount.value = (shopRes.data.data || []).length

    // 今日上架
    const today = new Date().toISOString().slice(0, 10)
    const todayRes = await listingLogApi.getListingLogSummary({ start_date: today })
    todayCount.value = todayRes.data.data?.total || 0
  } catch (e) {
    console.error('load dashboard error:', e)
  }
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString('zh-CN')
}

onMounted(loadData)
</script>

<style scoped>
.task-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.task-item:last-child { border-bottom: none; }
.task-info { display: flex; justify-content: space-between; margin-bottom: 8px; }
.task-progress { text-align: right; font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.log-item { padding: 4px 0; font-size: 12px; border-bottom: 1px solid rgba(42,58,90,0.3); }
.log-time { color: #666; margin-right: 8px; }
.log-msg { color: var(--text-secondary); }
</style>