<template>
  <div class="page-container">
    <div class="page-header"><h1 class="page-title">自动发货</h1></div>
    <div class="stat-cards">
      <div class="stat-card"><div class="label">总发货</div><div class="value">{{ summary.total }}</div></div>
      <div class="stat-card"><div class="label" style="color:#66bb6a">成功</div><div class="value" style="color:#66bb6a">{{ summary.success }}</div></div>
      <div class="stat-card"><div class="label" style="color:#ef5350">失败</div><div class="value" style="color:#ef5350">{{ summary.failed }}</div></div>
    </div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="发货配置" name="configs">
        <el-button type="primary" style="margin-bottom:12px" @click="showAddConfig = true">添加配置</el-button>
        <el-table :data="configs" stripe>
          <el-table-column prop="product_title" label="商品" min-width="200" show-overflow-tooltip />
          <el-table-column label="发货类型" width="100"><template #default="{ row }">{{ typeLabel(row.delivery_type) }}</template></el-table-column>
          <el-table-column label="自动发货" width="80"><template #default="{ row }"><el-switch v-model="row.auto_ship" disabled /></template></el-table-column>
          <el-table-column label="卡池余量" width="80"><template #default="{ row }">{{ row.card_pool_count || 0 }}</template></el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button size="small" @click="editConfig(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteConfig(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="发货日志" name="logs">
        <el-table :data="deliveryLogs" stripe>
          <el-table-column prop="created_at" label="时间" width="170"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
          <el-table-column prop="product_title" label="商品" min-width="200" show-overflow-tooltip />
          <el-table-column prop="delivery_type" label="类型" width="100"><template #default="{ row }">{{ typeLabel(row.delivery_type) }}</template></el-table-column>
          <el-table-column prop="tracking_no" label="物流单号" width="140" />
          <el-table-column label="状态" width="80"><template #default="{ row }"><el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag></template></el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="showAddConfig" title="添加发货配置" width="500px">
      <el-form :model="configForm" label-width="100px">
        <el-form-item label="店铺"><el-select v-model="configForm.shop_id" filterable style="width:100%"><el-option v-for="s in shops" :key="s.id" :label="s.name" :value="s.id" /></el-select></el-form-item>
        <el-form-item label="商品ID"><el-input v-model="configForm.product_id" /></el-form-item>
        <el-form-item label="商品标题"><el-input v-model="configForm.product_title" /></el-form-item>
        <el-form-item label="发货类型"><el-select v-model="configForm.delivery_type" style="width:100%"><el-option label="卡券" value="card" /><el-option label="网盘链接" value="link" /><el-option label="纯文本" value="text" /><el-option label="1688代发" value="proxy" /></el-select></el-form-item>
        <el-form-item v-if="configForm.delivery_type === 'link'" label="链接"><el-input v-model="configForm.link_url" /></el-form-item>
        <el-form-item v-if="configForm.delivery_type === 'link'" label="提取码"><el-input v-model="configForm.link_code" /></el-form-item>
        <el-form-item v-if="configForm.delivery_type === 'text'" label="内容"><el-input v-model="configForm.text_content" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="自动发货"><el-switch v-model="configForm.auto_ship" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddConfig = false">取消</el-button>
        <el-button type="primary" @click="submitConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as deliveryApi from '../api/delivery'
import * as shopApi from '../api/shop'

const activeTab = ref('configs'), configs = ref([]), deliveryLogs = ref([]), shops = ref([]), showAddConfig = ref(false), isEditConfig = ref(false), editConfigId = ref(null)
const summary = ref({ total: 0, success: 0, failed: 0 })
const configForm = ref({ shop_id: '', product_id: '', product_title: '', delivery_type: 'card', link_url: '', link_code: '', text_content: '', auto_ship: true })

async function loadData() {
  try {
    const [configRes, logRes, sumRes] = await Promise.all([deliveryApi.listDeliveryConfigs(), deliveryApi.listDeliveryLogs({ page: 1, page_size: 50 }), deliveryApi.getDeliveryLogSummary()])
    configs.value = configRes.data.data || []; deliveryLogs.value = logRes.data.data?.items || []; summary.value = sumRes.data.data || summary.value
  } catch (e) { console.error(e) }
}
function typeLabel(t) { return { card: '卡券', link: '链接', text: '文本', proxy: '代发' }[t] || t }
function editConfig(row) { isEditConfig.value = true; editConfigId.value = row.id; configForm.value = { ...row }; showAddConfig.value = true }
async function submitConfig() {
  try { if (isEditConfig.value) { await deliveryApi.updateDeliveryConfig(editConfigId.value, configForm.value); ElMessage.success('更新成功') } else { await deliveryApi.createDeliveryConfig(configForm.value); ElMessage.success('添加成功') }; showAddConfig.value = false; await loadData() }
  catch (e) { ElMessage.error('操作失败') }
}
async function deleteConfig(id) { try { await deliveryApi.deleteDeliveryConfig(id); ElMessage.success('已删除'); await loadData() } catch (e) { ElMessage.error('删除失败') } }
function formatTime(ts) { if (!ts) return '-'; return new Date(ts).toLocaleString('zh-CN') }
onMounted(async () => { try { const res = await shopApi.listShops(); shops.value = res.data.data || [] } catch (e) {}; await loadData() })
</script>
