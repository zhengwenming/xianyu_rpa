<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">大模型配置</h1>
      <el-button type="primary" @click="showForm = true; isEdit = false; editForm = { name: '', provider_type: 'openai', api_key: '', api_base: '', model: 'gpt-4o', temperature: 0.7, max_tokens: 2048 }">添加配置</el-button>
    </div>
    <el-table :data="configs" stripe v-loading="loading">
      <el-table-column prop="name" label="名称" width="150" />
      <el-table-column prop="provider_type" label="提供商" width="120">
        <template #default="{ row }">{{ providerLabel(row.provider_type) }}</template>
      </el-table-column>
      <el-table-column prop="model" label="模型" width="180" />
      <el-table-column prop="temperature" label="温度" width="80" />
      <el-table-column prop="max_tokens" label="最大Token" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }"><el-tag v-if="row.is_active" type="success" size="small">当前激活</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button size="small" @click="editConfig(row)">编辑</el-button>
          <el-button size="small" @click="testConfig(row.id)" :loading="testingId === row.id">测试</el-button>
          <el-button v-if="!row.is_active" size="small" type="primary" @click="activate(row.id)">激活</el-button>
          <el-button size="small" type="danger" @click="removeConfig(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showForm" :title="isEdit ? '编辑配置' : '添加配置'" width="500px">
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="editForm.provider_type" style="width:100%" @change="onProviderChange">
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Base"><el-input v-model="editForm.api_base" :placeholder="defaultBase" /></el-form-item>
        <el-form-item label="API Key"><el-input v-model="editForm.api_key" type="password" show-password /></el-form-item>
        <el-form-item label="模型名称"><el-input v-model="editForm.model" placeholder="如：gpt-4o, claude-3-5-sonnet" /></el-form-item>
        <el-form-item label="温度"><el-slider v-model="editForm.temperature" :min="0" :max="2" :step="0.1" /></el-form-item>
        <el-form-item label="最大Token"><el-input-number v-model="editForm.max_tokens" :min="100" :max="128000" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForm = false">取消</el-button>
        <el-button type="primary" @click="submitForm">{{ isEdit ? '更新' : '添加' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as llmApi from '../api/llm'

const configs = ref([]), loading = ref(false), showForm = ref(false), isEdit = ref(false), testingId = ref(null)
const editForm = ref({ name: '', provider_type: 'openai', api_key: '', api_base: '', model: 'gpt-4o', temperature: 0.7, max_tokens: 2048 })
const editId = ref(null)

const defaultBase = computed(() => {
  const bases = { openai: 'https://api.openai.com/v1', anthropic: 'https://api.anthropic.com', deepseek: 'https://api.deepseek.com', ollama: 'http://localhost:11434/v1', custom: 'https://' }
  return bases[editForm.value.provider_type] || ''
})

function providerLabel(type) { return { openai: 'OpenAI', anthropic: 'Anthropic', deepseek: 'DeepSeek', ollama: 'Ollama', custom: '自定义' }[type] || type }
function onProviderChange() { if (!editForm.value.api_base) editForm.value.api_base = defaultBase.value }

async function loadConfigs() { loading.value = true; try { const res = await llmApi.listConfigs(); configs.value = res.data.data || [] } catch (e) { console.error(e) } finally { loading.value = false } }
function editConfig(row) { isEdit.value = true; editId.value = row.id; editForm.value = { ...row }; showForm.value = true }
async function submitForm() {
  try {
    if (isEdit.value) { await llmApi.updateConfig(editId.value, editForm.value); ElMessage.success('更新成功') }
    else { await llmApi.createConfig(editForm.value); ElMessage.success('添加成功') }
    showForm.value = false; await loadConfigs()
  } catch (e) { ElMessage.error('操作失败') }
}
async function testConfig(id) { testingId.value = id; try { const res = await llmApi.testConfig(id); ElMessage[res.data.code === 0 ? 'success' : 'error'](res.data.message) } catch (e) { ElMessage.error('测试失败') } finally { testingId.value = null } }
async function activate(id) { try { await llmApi.activateConfig(id); ElMessage.success('已激活'); await loadConfigs() } catch (e) { ElMessage.error('激活失败') } }
async function removeConfig(id) { try { await llmApi.deleteConfig(id); ElMessage.success('已删除'); await loadConfigs() } catch (e) { ElMessage.error('删除失败') } }
onMounted(loadConfigs)
</script>
