<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">店铺管理</h1>
      <el-button type="primary" @click="showAddDialog = true">添加店铺</el-button>
    </div>
    <div class="shop-grid">
      <el-card v-for="shop in shops" :key="shop.id" class="shop-card">
        <div class="shop-avatar">
          <el-avatar :size="48" :src="shop.xianyu_avatar || undefined">
            {{ (shop.xianyu_nickname || shop.name || '?')[0] }}
          </el-avatar>
        </div>
        <div class="shop-info">
          <div class="shop-name">{{ shop.name }}</div>
          <div class="shop-nickname">{{ shop.xianyu_nickname || '未授权' }}</div>
          <el-tag :type="loginStatusType(shop.login_status)" size="small">{{ loginStatusLabel(shop.login_status) }}</el-tag>
        </div>
        <div class="shop-meta">
          <div v-if="shop.authorized_at" class="meta-item">授权: {{ formatTime(shop.authorized_at) }}</div>
          <div v-if="shop.last_active_time" class="meta-item">活跃: {{ formatTime(shop.last_active_time) }}</div>
        </div>
        <div class="shop-actions">
          <template v-if="shop.login_status === 'unauthorized'">
            <el-button size="small" type="primary" @click="authorize(shop.id)" :loading="authLoading === shop.id">授权登录</el-button>
          </template>
          <template v-else-if="shop.login_status === 'authorized'">
            <el-button size="small" type="primary" @click="$router.push('/tasks')">进入任务</el-button>
            <el-button size="small" @click="revoke(shop.id)">取消授权</el-button>
            <el-button size="small" @click="renameShop(shop)">重命名</el-button>
            <el-button size="small" type="danger" @click="deleteShop(shop)">删除</el-button>
          </template>
          <template v-else>
            <el-button size="small" type="warning" @click="authorize(shop.id)">重新授权</el-button>
            <el-button size="small" @click="revoke(shop.id)">取消授权</el-button>
            <el-button size="small" type="danger" @click="deleteShop(shop)">删除</el-button>
          </template>
        </div>
      </el-card>
      <el-card class="shop-card add-card" @click="showAddDialog = true">
        <div class="add-icon">+</div>
        <div class="add-text">添加店铺</div>
      </el-card>
    </div>
    <el-dialog v-model="showAddDialog" title="添加店铺" width="400px">
      <el-form :model="addForm">
        <el-form-item label="店铺名称"><el-input v-model="addForm.name" placeholder="如：数码小店A" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitAdd">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as shopApi from '../api/shop'

const shops = ref([])
const showAddDialog = ref(false)
const authLoading = ref(null)
const addForm = ref({ name: '' })

async function loadShops() {
  try { const res = await shopApi.listShops(); shops.value = res.data.data || [] } catch (e) { console.error(e) }
}
async function submitAdd() {
  if (!addForm.value.name) return ElMessage.warning('请输入店铺名称')
  await shopApi.createShop(addForm.value)
  showAddDialog.value = false; addForm.value.name = ''
  await loadShops(); ElMessage.success('店铺添加成功')
}
async function authorize(id) {
  authLoading.value = id
  try { const res = await shopApi.authorizeShop(id); if (res.data.code === 0) ElMessage.success('授权成功'); else ElMessage.warning(res.data.message); await loadShops() }
  catch (e) { ElMessage.error('授权失败') }
  finally { authLoading.value = null }
}
async function revoke(id) {
  try { await ElMessageBox.confirm('确认取消授权？', '提示'); await shopApi.revokeShop(id); ElMessage.success('已取消授权'); await loadShops() }
  catch (e) { if (e !== 'cancel') ElMessage.error('操作失败') }
}
async function renameShop(shop) {
  try { const { value } = await ElMessageBox.prompt('新名称', '重命名', { inputValue: shop.name });
    if (value) { await shopApi.updateShop(shop.id, { name: value }); ElMessage.success('重命名成功'); await loadShops() } }
  catch (e) { if (e !== 'cancel') ElMessage.error('重命名失败') }
}
async function deleteShop(shop) {
  try { await ElMessageBox.confirm(`确认删除店铺"${shop.name}"？`, '警告', { type: 'warning' }); await shopApi.deleteShop(shop.id); ElMessage.success('已删除'); await loadShops() }
  catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}
function loginStatusType(status) { return { authorized: 'success', unauthorized: 'info', expired: 'warning' }[status] || 'info' }
function loginStatusLabel(status) { return { authorized: '已授权', unauthorized: '未授权', expired: '已过期' }[status] || status }
function formatTime(ts) { if (!ts) return '-'; return new Date(ts).toLocaleString('zh-CN') }
onMounted(loadShops)
</script>

<style scoped>
.shop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.shop-card { text-align: center; }
.shop-avatar { margin-bottom: 12px; }
.shop-info { margin-bottom: 12px; }
.shop-name { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.shop-nickname { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.shop-meta { font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; }
.meta-item { margin-bottom: 2px; }
.shop-actions { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }
.add-card { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 200px; cursor: pointer; }
.add-card:hover { border-color: var(--accent); }
.add-icon { font-size: 48px; color: var(--text-secondary); margin-bottom: 8px; }
.add-text { font-size: 16px; color: var(--text-secondary); }
</style>
