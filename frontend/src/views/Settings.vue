<template>
  <div class="page-container">
    <div class="page-header"><h1 class="page-title">全局设置</h1></div>
    <el-card>
      <el-form :model="form" label-width="160px" v-loading="loading">
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="📐 图片与视频设置" name="image">
            <el-form-item label="AI主图视频"><el-switch v-model="form.enable_ai_main_video" /><span class="setting-desc">为每个商品生成短视频主图</span></el-form-item>
            <el-form-item label="智能裁剪3:4"><el-switch v-model="form.enable_smart_crop_3_4" /><span class="setting-desc">自动裁剪主图为3:4比例</span></el-form-item>
            <el-form-item label="AI导购短标题"><el-switch v-model="form.enable_ai_short_title" /><span class="setting-desc">生成8-12字导购短标题</span></el-form-item>
          </el-collapse-item>
          <el-collapse-item title="💰 价格设置" name="price">
            <el-form-item label="加价比例"><el-input-number v-model="form.price_markup_ratio" :min="1.0" :max="5.0" :step="0.1" /><span class="setting-desc">上架价格 = 采集价 × 加价比例 + 加价金额</span></el-form-item>
            <el-form-item label="加价金额"><el-input-number v-model="form.price_markup_amount" :min="0" :max="500" /><span class="setting-desc">在比例基础上叠加的固定金额</span></el-form-item>
          </el-collapse-item>
          <el-collapse-item title="🚫 过滤与屏蔽" name="filter">
            <el-form-item label="供应商黑名单">
              <el-tag v-for="(s, idx) in supplierList" :key="idx" closable @close="removeSupplier(s)" style="margin:2px">{{ s }}</el-tag>
              <el-input v-model="newSupplier" size="small" style="width:150px;margin-left:4px" @keyup.enter="addSupplier" placeholder="输入后回车" />
            </el-form-item>
            <el-form-item label="关键词屏蔽">
              <el-tag v-for="(kw, idx) in keywordList" :key="idx" closable @close="removeKeyword(kw)" style="margin:2px">{{ kw }}</el-tag>
              <el-input v-model="newKeyword" size="small" style="width:150px;margin-left:4px" @keyup.enter="addKeyword" placeholder="输入后回车" />
            </el-form-item>
          </el-collapse-item>
          <el-collapse-item title="⏱️ 节奏控制" name="pace">
            <el-form-item label="上货后延迟"><el-input-number v-model="form.post_listing_delay" :min="5" :max="120" /> 秒<span class="setting-desc">每个商品上架后的等待时间</span></el-form-item>
            <el-form-item label="暂停触发数量"><el-input-number v-model="form.simulated_pause_count" :min="5" :max="50" /> 个<span class="setting-desc">连续上架多少个后触发休息</span></el-form-item>
            <el-form-item label="暂停休息时间"><el-input-number v-model="form.simulated_pause_interval" :min="5" :max="60" /> 分钟<span class="setting-desc">休息的时长</span></el-form-item>
          </el-collapse-item>
          <el-collapse-item title="🎯 目标控制" name="target">
            <el-form-item label="目标成功个数"><el-input-number v-model="form.target_success_count" :min="1" :max="500" /><span class="setting-desc">创建任务时的默认目标数量</span></el-form-item>
          </el-collapse-item>
        </el-collapse>
        <div style="margin-top:20px;display:flex;gap:12px">
          <el-button type="primary" @click="saveSettings" :loading="saving">保存设置</el-button>
          <el-button @click="resetSettings">恢复默认</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as settingsApi from '../api/settings'

const loading = ref(false), saving = ref(false), activeCollapse = ref(['image', 'price', 'filter', 'pace', 'target'])
const form = reactive({
  enable_ai_main_video: false, enable_smart_crop_3_4: true, enable_ai_short_title: false,
  price_markup_ratio: 1.3, price_markup_amount: 0,
  supplier_blacklist: '[]', keyword_blocklist: '[]',
  post_listing_delay: 30, simulated_pause_interval: 15, simulated_pause_count: 10,
  target_success_count: 10,
})
const supplierList = ref([]), keywordList = ref([])
const newSupplier = ref(''), newKeyword = ref('')

async function loadSettings() {
  loading.value = true
  try {
    const res = await settingsApi.getSettings()
    if (res.data.data) { Object.assign(form, res.data.data) }
    const [supRes, kwRes] = await Promise.all([settingsApi.getSuppliers(), settingsApi.getKeywords()])
    supplierList.value = supRes.data.data || []
    keywordList.value = kwRes.data.data || []
  } catch (e) { console.error(e) } finally { loading.value = false }
}
async function saveSettings() {
  saving.value = true
  try {
    form.supplier_blacklist = JSON.stringify(supplierList.value)
    form.keyword_blocklist = JSON.stringify(keywordList.value)
    await settingsApi.updateSettings({ ...form })
    ElMessage.success('设置已保存')
  } catch (e) { ElMessage.error('保存失败') } finally { saving.value = false }
}
async function resetSettings() {
  try { await settingsApi.resetSettings(); await loadSettings(); ElMessage.success('已恢复默认') }
  catch (e) { ElMessage.error('恢复失败') }
}
async function addSupplier() {
  if (!newSupplier.value) return
  try { const res = await settingsApi.addSupplier(newSupplier.value); supplierList.value = res.data.data || []; newSupplier.value = '' } catch (e) { ElMessage.error('添加失败') }
}
async function removeSupplier(s) {
  try { const res = await settingsApi.removeSupplier(s); supplierList.value = res.data.data || [] } catch (e) { ElMessage.error('移除失败') }
}
async function addKeyword() {
  if (!newKeyword.value) return
  try { const res = await settingsApi.addKeyword(newKeyword.value); keywordList.value = res.data.data || []; newKeyword.value = '' } catch (e) { ElMessage.error('添加失败') }
}
async function removeKeyword(kw) {
  try { const res = await settingsApi.removeKeyword(kw); keywordList.value = res.data.data || [] } catch (e) { ElMessage.error('移除失败') }
}
onMounted(loadSettings)
</script>

<style scoped>
.setting-desc { font-size: 12px; color: var(--text-secondary); margin-left: 12px; }
</style>
