<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">任务管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">创建任务</el-button>
    </div>
    <div class="filter-bar">
      <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width:140px">
        <el-option label="全部" value="" />
        <el-option label="运行中" value="running" />
        <el-option label="已暂停" value="paused" />
        <el-option label="等待中" value="pending" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
        <el-option label="失败" value="failed" />
      </el-select>
      <el-button @click="loadTasks">刷新</el-button>
    </div>
    <div class="task-grid" v-if="tasks.length > 0">
      <TaskCard v-for="task in tasks" :key="task.id" :task="task">
        <template #actions="{ task }">
          <template v-if="task.status === 'pending'">
            <el-button size="small" type="primary" @click="handleStart(task.id)">启动</el-button>
            <el-button size="small" @click="handleCancel(task.id)">取消</el-button>
            <el-button size="small" @click="handleDelete(task.id)">删除</el-button>
          </template>
          <template v-else-if="task.status === 'running'">
            <el-button size="small" @click="handlePause(task.id)">暂停</el-button>
            <el-button size="small" @click="handleCancel(task.id)">取消</el-button>
          </template>
          <template v-else-if="task.status === 'paused'">
            <el-button size="small" type="primary" @click="handleResume(task.id)">继续</el-button>
            <el-button size="small" @click="handleCancel(task.id)">取消</el-button>
          </template>
          <template v-else>
            <el-button size="small" @click="handleDelete(task.id)">删除</el-button>
          </template>
        </template>
      </TaskCard>
    </div>
    <el-empty v-else description="暂无任务" />
    <el-dialog v-model="showCreateDialog" title="创建上架任务" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="任务名称"><el-input v-model="createForm.name" placeholder="如：数码商品上架" /></el-form-item>
        <el-form-item label="选择店铺">
          <el-select v-model="createForm.shop_id" filterable style="width:100%">
            <el-option v-for="s in shops" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="采集关键词"><el-input v-model="createForm.keywords" placeholder="多个关键词用逗号分隔" /></el-form-item>
        <el-form-item label="目标数量"><el-input-number v-model="createForm.target_count" :min="1" :max="500" /></el-form-item>
        <el-form-item label="商品类别"><el-input v-model="createForm.category" placeholder="如：数码、服饰" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as taskApi from '../api/task'
import * as shopApi from '../api/shop'
import TaskCard from '../components/TaskCard.vue'

const tasks = ref([]), shops = ref([]), filterStatus = ref(''), showCreateDialog = ref(false)
const createForm = ref({ name: '', shop_id: '', keywords: '', target_count: 10, category: '' })

async function loadTasks() {
  try { const params = { page: 1, page_size: 50 }; if (filterStatus.value) params.status = filterStatus.value
    const res = await taskApi.listTasks(params); tasks.value = res.data.data?.items || [] } catch (e) { console.error(e) }
}
async function loadShops() { try { const res = await shopApi.listShops(); shops.value = res.data.data || [] } catch (e) { console.error(e) } }
async function handleStart(id) { const res = await taskApi.startTask(id); res.data.code === 0 ? ElMessage.success('任务已启动') : ElMessage.error(res.data.message); await loadTasks() }
async function handlePause(id) { await taskApi.pauseTask(id); ElMessage.success('任务已暂停'); await loadTasks() }
async function handleResume(id) { await taskApi.resumeTask(id); ElMessage.success('任务已恢复'); await loadTasks() }
async function handleCancel(id) { await taskApi.cancelTask(id); ElMessage.success('任务已取消'); await loadTasks() }
async function handleDelete(id) { await taskApi.deleteTask(id); ElMessage.success('任务已删除'); await loadTasks() }
async function submitCreate() {
  const data = { name: createForm.value.name || '未命名任务', shop_id: createForm.value.shop_id,
    shop_name: shops.value.find(s => s.id === createForm.value.shop_id)?.name || '',
    keywords: JSON.stringify(createForm.value.keywords.split(',').map(k => k.trim()).filter(Boolean)),
    target_count: createForm.value.target_count, category: createForm.value.category }
  await taskApi.createTask(data); showCreateDialog.value = false; ElMessage.success('任务创建成功'); await loadTasks()
}
onMounted(() => { loadTasks(); loadShops() })
</script>

<style scoped>
.task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
</style>
