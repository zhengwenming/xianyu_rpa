<template>
  <div class="page-container">
    <div class="page-header"><h1 class="page-title">任务策略日志</h1></div>
    <div class="filter-bar">
      <el-select v-model="filterShop" placeholder="选择店铺" clearable style="width:160px" @change="loadData">
        <el-option label="全部店铺" value="" /><el-option v-for="s in shops" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:140px" @change="loadData">
        <el-option label="全部" value="" /><el-option label="运行中" value="running" /><el-option label="已完成" value="completed" /><el-option label="已中断" value="interrupted" /><el-option label="已取消" value="cancelled" />
      </el-select>
      <el-button @click="loadData">刷新</el-button>
    </div>
    <div class="stat-cards">
      <div class="stat-card"><div class="label">总任务数</div><div class="value">{{ summary.total }}</div></div>
      <div class="stat-card"><div class="label" style="color:#4fc3f7">运行中</div><div class="value" style="color:#4fc3f7">{{ summary.running }}</div></div>
      <div class="stat-card"><div class="label" style="color:#66bb6a">已完成</div><div class="value" style="color:#66bb6a">{{ summary.completed }}</div></div>
      <div class="stat-card"><div class="label" style="color:#ef5350">已中断/取消</div><div class="value" style="color:#ef5350">{{ summary.interrupted }}</div></div>
    </div>
    <el-table :data="logs" stripe v-loading="loading">
      <el-table-column prop="task_name" label="任务名称" min-width="160" />
      <el-table-column prop="shop_name" label="店铺" width="120" />
      <el-table-column prop="product_category" label="类别" width="100" />
      <el-table-column prop="target_count" label="目标数" width="70" />
      <el-table-column prop="success_count" label="成功" width="60"><template #default="{ row }"><span style="color:#66bb6a">{{ row.success_count }}</span></template></el-table-column>
      <el-table-column prop="fail_count" label="失败" width="60"><template #default="{ row }"><span style="color:#ef5350">{{ row.fail_count }}</span></template></el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }"><el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="170"><template #default="{ row }">{{ formatTime(row.start_time) }}</template></el-table-column>
      <el-table-column prop="duration_seconds" label="耗时" width="80"><template #default="{ row }">{{ row.duration_seconds ? row.duration_seconds + 's' : '-' }}</template></el-table-column>
      <el-table-column label="操作" width="80">
        <template #default="{ row }"><el-button size="small" @click="showDetail(row)">详情</el-button></template>
      </el-table-column>
    </el-table>
    <div style="margin-top:16px;display:flex;justify-content:center">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" @current-change="loadData" layout="prev,pager,next,total" />
    </div>
    <el-dialog v-model="showDetailDialog" title="任务详情" width="600px">
      <pre v-if="detailLog" style="white-space:pre-wrap;color:#ccc">{{ JSON.stringify(detailLog, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as taskLogApi from '../api/taskLog'
import * as shopApi from '../api/shop'

const logs = ref([]), shops = ref([]), loading = ref(false), filterShop = ref(''), filterStatus = ref(''), page = ref(1), pageSize = ref(20), total = ref(0)
const summary = ref({ total: 0, running: 0, completed: 0, interrupted: 0 }), showDetailDialog = ref(false), detailLog = ref(null)

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterShop.value) params.shop_id = filterShop.value
    if (filterStatus.value) params.status = filterStatus.value
    const [res, sumRes] = await Promise.all([taskLogApi.listTaskLogs(params), taskLogApi.getTaskLogSummary(params)])
    logs.value = res.data.data?.items || []; total.value = res.data.data?.total || 0; summary.value = sumRes.data.data || summary.value
  } catch (e) { console.error(e) } finally { loading.value = false }
}
async function showDetail(row) { try { const res = await taskLogApi.getTaskLog(row.id); detailLog.value = res.data.data; showDetailDialog.value = true } catch (e) { console.error(e) } }
function statusType(s) { return { running: 'primary', paused: 'warning', completed: 'success', cancelled: 'danger', failed: 'danger', interrupted: 'warning' }[s] || 'info' }
function statusLabel(s) { return { running: '运行中', paused: '已暂停', completed: '已完成', cancelled: '已取消', failed: '失败', interrupted: '已中断' }[s] || s }
function formatTime(ts) { if (!ts) return '-'; return new Date(ts).toLocaleString('zh-CN') }
onMounted(async () => { try { const res = await shopApi.listShops(); shops.value = res.data.data || [] } catch (e) {}; await loadData() })
</script>
