<template>
  <div class="page-container">
    <div class="page-header"><h1 class="page-title">自动回复</h1></div>
    <div class="status-bar">
      <span v-for="(status, shopId) in replyStatus" :key="shopId" class="status-item">
        <span class="status-dot" :class="status === 'connected' ? 'online' : 'offline'"></span>
        店铺 {{ shopId }}: {{ status === 'connected' ? '已连接' : '已断开' }}
      </span>
      <el-button size="small" type="primary" @click="refreshStatus">刷新</el-button>
    </div>
    <el-row :gutter="16" style="height: calc(100vh - 200px);">
      <el-col :span="8">
        <el-card style="height:100%">
          <template #header>会话列表</template>
          <div v-if="conversations.length === 0" style="text-align:center;padding:20px;color:#666">暂无会话</div>
          <div v-for="conv in conversations" :key="conv.user_id" class="conv-item" @click="selectConv(conv)">
            <div class="conv-user">{{ conv.user_id }}</div>
            <div class="conv-preview">{{ conv.history?.[conv.history.length-1]?.content || '' }}</div>
            <div v-if="conv.human_takeover" class="takeover-badge">人工</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card style="height:100%">
          <template #header>
            <span>{{ selectedConv ? '对话: ' + selectedConv.user_id : '选择会话' }}</span>
            <span v-if="selectedConv" style="float:right">
              <el-button size="small" @click="toggleTakeover">{{ selectedConv.human_takeover ? '切换AI' : '切换人工' }}</el-button>
            </span>
          </template>
          <div v-if="!selectedConv" style="text-align:center;padding:40px;color:#666">请选择一个会话</div>
          <div v-else class="chat-messages">
            <div v-for="(msg, idx) in selectedConv.history" :key="idx" class="chat-msg" :class="msg.role === 'user' ? 'left' : 'right'">
              <div class="msg-bubble">{{ msg.content }}</div>
            </div>
            <div class="chat-input" v-if="selectedConv">
              <el-input v-model="replyText" placeholder="输入回复..." @keyup.enter="sendReply" />
              <el-button type="primary" @click="sendReply" style="margin-left:8px">发送</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as replyApi from '../api/reply'

const replyStatus = ref({}), conversations = ref([]), selectedConv = ref(null), replyText = ref('')

async function refreshStatus() { try { const res = await replyApi.getReplyStatus(); replyStatus.value = res.data.data || {} } catch (e) { console.error(e) } }
async function loadConversations() { try { const keys = Object.keys(replyStatus.value); if (keys.length > 0) { const res = await replyApi.listConversations(keys[0]); conversations.value = res.data.data || [] } } catch (e) { console.error(e) } }
function selectConv(conv) { selectedConv.value = conv }
async function toggleTakeover() {
  if (!selectedConv.value) return
  try { await replyApi.toggleTakeover(selectedConv.value.shop_id, selectedConv.value.user_id); selectedConv.value.human_takeover = !selectedConv.value.human_takeover; ElMessage.success('已切换') }
  catch (e) { ElMessage.error('切换失败') }
}
async function sendReply() {
  if (!replyText.value || !selectedConv.value) return
  try { await replyApi.sendMessage(selectedConv.value.shop_id, selectedConv.value.user_id, replyText.value); if (!selectedConv.value.history) selectedConv.value.history = []; selectedConv.value.history.push({ role: 'assistant', content: replyText.value }); replyText.value = '' } catch (e) { ElMessage.error('发送失败') }
}
onMounted(async () => { await refreshStatus(); await loadConversations() })
</script>

<style scoped>
.status-bar { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.status-item { display: flex; align-items: center; gap: 4px; font-size: 13px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.status-dot.online { background: #66bb6a; }
.status-dot.offline { background: #ef5350; }
.conv-item { padding: 8px; border-bottom: 1px solid var(--border); cursor: pointer; }
.conv-item:hover { background: rgba(79,195,247,0.05); }
.conv-user { font-weight: 600; font-size: 14px; }
.conv-preview { font-size: 12px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.takeover-badge { display: inline-block; background: #ffa726; color: #000; font-size: 10px; padding: 1px 4px; border-radius: 3px; }
.chat-messages { height: calc(100% - 60px); overflow-y: auto; padding: 12px; }
.chat-msg { margin-bottom: 12px; display: flex; }
.chat-msg.left { justify-content: flex-start; }
.chat-msg.right { justify-content: flex-end; }
.msg-bubble { max-width: 70%; padding: 8px 12px; border-radius: 8px; font-size: 14px; }
.chat-msg.left .msg-bubble { background: #2a3a5a; }
.chat-msg.right .msg-bubble { background: #4fc3f7; color: #000; }
.chat-input { display: flex; padding: 8px; border-top: 1px solid var(--border); }
</style>
