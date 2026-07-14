<template>
  <div class="page-container">
    <div class="page-header"><h1 class="page-title">下架日志</h1></div>
    <div class="filter-bar">
      <el-select v-model="filterShop" placeholder="选择店铺" clearable style="width:160px" @change="loadData">
        <el-option label="全部店铺" value="" /><el-option v-for="s in shops" :key="s.id" :label="s.name" :value="s.id" />
      </el-select>
      <el-button @click="loadData">刷新</el-button>
      <el-button @click="clearLogs">清空</el-button>
    </div>
    <div class="stat-cards">
      <div class="stat-card"><div class="label">总下架</div><div class="value">{{ summary.total }}</div></div>
      <div class="stat-card"><div class="label" style="color:#4fc3f7">自动下架</div><div class="value" style="color:#4fc3f7">{{ summary.auto }}</div></div>
      <div class="stat-card"><div class="label" style="color:#ffa726">手动下架</div><div class="value" style="color:#ffa726">{{ summary.manual }}</div></div>
      <div class="stat-card"><div class="label" style="color:#ab47bc">售罄下架</div><div class="value" style="color:#ab47bc">{{ summary.sold_out }}</div></div>
    </div>
    <el-table :data="logs" stripe v-loading="loading">
      <el-table-column prop="delisted_at" label="下架时间" width="170"><template #default="{ row }">{{ formatTime(row.delisted_at || row.created_at) }}</template></el-table-column>
      <el-table-column prop="shop_name" label="店铺" width="120" />
      <el-table-column prop="product_title" label="商品标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="xianyu_item_id" label="闲鱼商品ID" width="140" />
      <el-table-column label="下架原因" width="120">
        <template #default="{ row }"><el-tag :type="reasonType(row.delist_reason)" size="small">{{ reasonLabel(row.delist_reason) }}</el-tag></template>
      </el-table-column>
      <el-table-column label="下架类型" width="100">
        <template #default="{ row }">{{ row.delist_type === 'auto' ? '自动' : '手动' }}</template>
      </el-table-column>
    </el-table>
    <div style="margin-top:16px;display:flex;justify-content:center">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" @current-change="loadData" layout="prev,pager,next,total" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as delistingLogApi from '../api/delistingLog'
import * as shopApi from '../api/shop'

const logs = ref([]), shops = ref([]), loading = ref(false), filterShop = ref(''), page = ref(1), pageSize = ref(20), total = ref(0)
const summary = ref({ total: 0, auto: 0, manual: 0, sold_out: 0 })

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterShop.value) params.shop_id = filterShop.value
    const [res, sumRes] = await Promise.all([delistingLogApi.listDelistingLogs(params), delistingLogApi.getDelistingLogSummary(params)])
    logs.value = res.data.data?.items || []; total.value = res.data.data?.total || 0; summary.value = sumRes.data.data || summary.value
  } catch (e) { console.error(e) } finally { loading.value = false }
}
async function clearLogs() {
  try { await ElMessageBox.confirm('确认清空下架日志？', '警告', { type: 'warning' }); await delistingLogApi.clearDelistingLogs({ confirm: true, shop_id: filterShop.value || undefined }); ElMessage.success('已清空'); await loadData() }
  catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}
function reasonType(r) { return { sold_out: 'info', violation: 'danger', manual: 'primary', expired: 'warning', strategy: 'warning' }[r] || 'info' }
function reasonLabel(r) { return { sold_out: '售罄', violation: '违规', manual: '手动', expired: '过期', strategy: '策略' }[r] || r }
function formatTime(ts) { if (!ts) return '-'; return new Date(ts).toLocaleString('zh-CN') }
onMounted(async () => { try { const res = await shopApi.listShops(); shops.value = res.data.data || [] } catch (e) {}; await loadData() })
</script>
