import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as taskApi from '../api/task'

export function useTask() {
  const loading = ref(false)

  async function startTask(id) {
    loading.value = true
    try {
      const res = await taskApi.startTask(id)
      if (res.data.code === 0) {
        ElMessage.success('任务已启动')
        return true
      }
      ElMessage.error(res.data.message || '启动失败')
      return false
    } catch (e) {
      ElMessage.error('启动失败: ' + (e.response?.data?.message || e.message))
      return false
    } finally {
      loading.value = false
    }
  }

  async function pauseTask(id) {
    try {
      const res = await taskApi.pauseTask(id)
      if (res.data.code === 0) {
        ElMessage.success('任务已暂停')
        return true
      }
      return false
    } catch (e) {
      ElMessage.error('暂停失败')
      return false
    }
  }

  async function resumeTask(id) {
    try {
      const res = await taskApi.resumeTask(id)
      if (res.data.code === 0) {
        ElMessage.success('任务已恢复')
        return true
      }
      return false
    } catch (e) {
      ElMessage.error('恢复失败')
      return false
    }
  }

  async function cancelTask(id) {
    try {
      const res = await taskApi.cancelTask(id)
      if (res.data.code === 0) {
        ElMessage.success('任务已取消')
        return true
      }
      return false
    } catch (e) {
      ElMessage.error('取消失败')
      return false
    }
  }

  async function deleteTask(id) {
    try {
      await taskApi.deleteTask(id)
      ElMessage.success('任务已删除')
      return true
    } catch (e) {
      ElMessage.error('删除失败')
      return false
    }
  }

  return {
    loading,
    startTask,
    pauseTask,
    resumeTask,
    cancelTask,
    deleteTask,
  }
}