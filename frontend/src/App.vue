<template>
  <el-container style="height: 100vh">
    <el-aside :width="sidebarWidth" style="background: #16213e; border-right: 1px solid #2a3a5a; overflow: hidden;">
      <div class="sidebar-header">
        <h2 class="sidebar-title">闲鱼铺货系统</h2>
      </div>
      <el-menu :default-active="currentRoute" router :collapse="isCollapsed" background-color="#16213e" text-color="#8899aa" active-text-color="#4fc3f7" style="border-right: none;">
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/shops">
          <el-icon><Shop /></el-icon>
          <span>店铺管理</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/llm-config">
          <el-icon><Cpu /></el-icon>
          <span>大模型配置</span>
        </el-menu-item>
        <el-menu-item index="/listing-logs">
          <el-icon><Upload /></el-icon>
          <span>上架日志</span>
        </el-menu-item>
        <el-menu-item index="/delisting-logs">
          <el-icon><Download /></el-icon>
          <span>下架日志</span>
        </el-menu-item>
        <el-menu-item index="/task-logs">
          <el-icon><Document /></el-icon>
          <span>任务策略日志</span>
        </el-menu-item>
        <el-menu-item index="/auto-reply">
          <el-icon><ChatLineSquare /></el-icon>
          <span>自动回复</span>
        </el-menu-item>
        <el-menu-item index="/delivery">
          <el-icon><Van /></el-icon>
          <span>自动发货</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>全局设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header style="height: 50px; background: #16213e; border-bottom: 1px solid #2a3a5a; display: flex; align-items: center; justify-content: flex-end; padding: 0 20px;">
        <el-button type="primary" size="small" @click="showLogDrawer = !showLogDrawer">
          <el-icon><Monitor /></el-icon> 运行日志
        </el-button>
      </el-header>
      <el-main style="padding: 0; background: #1a1a2e; overflow: hidden;">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- 运行日志抽屉 -->
  <el-drawer v-model="showLogDrawer" title="实时运行日志" size="40%" direction="btt" :with-header="true" style="background: #1a1a2e;">
    <LogViewer />
  </el-drawer>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import LogViewer from './components/LogViewer.vue'

const route = useRoute()
const currentRoute = computed(() => route.path)
const isCollapsed = ref(false)
const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '220px')
const showLogDrawer = ref(false)
</script>

<style scoped>
.sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #2a3a5a;
}
.sidebar-title {
  color: #4fc3f7;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}
</style>