<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">上架日志</h1>
    </div>
    <div class="filter-bar">
      <el-select v-model="filterShop" placeholder="选择店铺" clearable style="width:160px" @change="loadData">
        <el-option label="全部店铺" value="" />
        <el-option v-for="s in shops" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" @change="loadData" />
      <el-button @click="loadData">刷新</el-button>
      <el-button @click="clearLogs">清空</el-button>
      <el-button @click="exportLogs">导出</el-button>
    </div>
    <div class="stat-cards">
      <div class="stat-card"><div class="label">总尝试</div><div class="value">{{ summary.total }}</div></div>
      <div class="stat-card"><div class="label" style="color:#66bb6a">成功</div><div class="value" style="color:#66bb6a">{{ summary.success }}</div></div>
      <div class="stat-card"><div class="label" style="color:#ef5350">失败</div><div class="value" style="color:#ef5350">{{ summary.failed }}</div></div>
      <div class="stat-card"><div class="label">成功率</div><div class="value">{{ summary.success_rate }}%</div></div>
    </div>
    <el-table :data="logs" stripe v-loading="loading" @sort-change="handleSort">
      <el-table-column prop="listed_at" label="上架时间" width="170" :sortable="'custom'">
        <template #default="{ row }">{{ formatTime(row.listed_at || row.created_at) }}</template>
      </el-table-column>
      <el-table-column prop="shop_name" label="店铺" width="120" />
      <el-table-column prop="product_title" label="商品标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="source_supplier" label="供应商" width="140" />
      <el-table-column prop="source_price" label="采集价" width="80" />
      <el-table-column prop="listing_price" label="上架价" width="80" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }"><el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">{{ row.status === 'success' ? '成功' : '失败' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="fail_reason" label="失败原因" min-width="160" show-overflow-tooltip />
    </el-table>
    <div style="margin-top:16px;display:flex;justify-content:center">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" @current-change="loadData" layout="prev,pager,next,total" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as listingLogApi from '../api/listingLog'
import * as shopApi from '../api/shop'

const logs = ref([]), shops = ref([]), loading = ref(false)
const filterShop = ref(''), page = ref(1), pageSize = ref(20), total = ref(0)
const dateRange = ref(null)
const summary = ref({ total: 0, success: 0, failed: 0, success_rate: 0 })

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterShop.value) params.shop_id = filterShop.value
    if (dateRange.value && dateRange.value[0]) { params.start_date = dateRange.value[0].toISOString().slice(0,10); params.end_date = dateRange.value[1].toISOString().slice(0,10) }
    const [res, sumRes] = await Promise.all([listingLogApi.listListingLogs(params), listingLogApi.getListingLogSummary(params)])
    logs.value = res.data.data?.items || []
    total.value = res.data.data?.total || 0
    summary.value = sumRes.data.data || { total: 0, success: 0, failed: 0, success_rate: 0 }
  } catch (e) { console.error(e) } finally { loading.value = false }
}
async function clearLogs() {
  try { await ElMessageBox.confirm('确认清空上架日志？', '警告', { type: 'warning' }); await listingLogApi.clearListingLogs({ confirm: true, shop_id: filterShop.value || undefined }); ElMessage.success('已清空'); await loadData() }
  catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}
function exportLogs() { listingLogApi.exportListingLogs({ shop_id: filterShop.value || undefined }).then(res => { const a = document.createElement('a'); a.href = URL.createObjectURL(res.data); a.download = 'listing_logs.csv'; a.click() }) }
function handleSort() {}
function formatTime(ts) { if (!ts) return '-'; return new Date(ts).toLocaleString('zh-CN') }
onMounted(async () => { try { const res = await shopApi.listShops(); shops.value = res.data.data || [] } catch (e) {}; await loadData() })
</script>
