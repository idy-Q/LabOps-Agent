<template>
  <div class="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans">
    <!-- 顶部全局导航栏 -->
    <header class="h-14 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-4 flex items-center justify-between shrink-0 z-20">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-lg font-bold shadow-md shadow-emerald-500/20">
          ⚡
        </div>
        <div>
          <h1 class="text-sm font-bold text-slate-100 tracking-wide flex items-center gap-2">
            LabOps-Agent
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-normal">
              高校机房智能运维管家
            </span>
          </h1>
          <p class="text-[10px] text-slate-400 hidden sm:block">
            轻量级 ReAct 架构 · 深度白盒推理状态机 · 规章 RAG 溯源 · 左右实时业务闭环
          </p>
        </div>
      </div>

      <!-- 右侧全局控制与状态 -->
      <div class="flex items-center space-x-3 text-xs">
        <!-- 后端服务动态连接状态 -->
        <div
          @click="refreshAllData"
          class="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-full border text-[11px] cursor-pointer transition-colors shadow-sm"
          :class="backendConnected ? 'bg-slate-800 border-slate-700/60 text-slate-300' : 'bg-rose-950/50 border-rose-800/80 text-rose-300 hover:bg-rose-900/60'"
          :title="backendConnected ? 'FastAPI 后端服务正常连接 (8000)' : 'FastAPI 后端服务未连接，点击重试'"
        >
          <span class="w-2 h-2 rounded-full" :class="backendConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500 animate-ping'"></span>
          <span>{{ backendConnected ? 'FastAPI 8000 在线' : 'FastAPI 8000 离线 (请启动后端)' }}</span>
          <span class="text-slate-600">|</span>
          <span class="font-mono text-slate-400">SSE 双工通道</span>
        </div>

        <button
          @click="openSessionDrawer"
          class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs flex items-center space-x-1.5 transition-colors shadow-sm"
          title="查看与切换系统历史会话"
        >
          <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>历史会话</span>
        </button>

        <button
          @click="startNewSession"
          class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs flex items-center space-x-1.5 transition-colors shadow-sm"
        >
          <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>新建会话</span>
        </button>

        <button
          @click="refreshAllData"
          class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-colors"
          title="刷新大盘全部数据"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </header>

    <!-- 左右分栏核心业务交互区 -->
    <div class="flex-1 flex flex-col lg:flex-row overflow-hidden">
      <!-- 左侧：对话推理流面板 (45%) -->
      <section class="w-full lg:w-[46%] flex flex-col border-b lg:border-b-0 lg:border-r border-slate-800 bg-slate-950/60 overflow-hidden shrink-0">
        <!-- 左侧面板顶栏 -->
        <div class="px-4 py-2 bg-slate-900/60 border-b border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <div class="flex items-center space-x-2">
            <span class="font-medium text-slate-200">ReAct 推理流</span>
            <span class="px-1.5 py-0.5 rounded bg-slate-800 font-mono text-[10px] text-slate-400">
              {{ currentSessionId || '未初始化' }}
            </span>
          </div>
          <div v-if="currentTraceId" class="text-[10px] font-mono text-slate-500">
            Trace: {{ currentTraceId }}
          </div>
        </div>

        <!-- 消息流组件 -->
        <ChatStream
          ref="chatStreamRef"
          :messages="messages"
          :isStreaming="isStreaming"
        />

        <!-- 输入框组件 -->
        <ChatInput
          :isLoading="isStreaming"
          @send="handleSendMessage"
          @abort="handleAbortStream"
        />
      </section>

      <!-- 右侧：实时数据看板 (54%) -->
      <section class="flex-1 flex flex-col bg-slate-950 p-3 sm:p-4 overflow-y-auto space-y-4">
        <!-- 后端未启动友好引导条 -->
        <div
          v-if="!backendConnected"
          class="p-3.5 rounded-2xl bg-amber-950/40 border border-amber-500/30 text-amber-200 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 shadow-lg shadow-amber-950/20"
        >
          <div class="flex items-center space-x-2.5">
            <span class="text-lg">⚠️</span>
            <div>
              <div class="font-bold text-amber-100 flex items-center gap-1.5">
                FastAPI 后端服务 (端口 8000) 尚未启动
                <span class="text-[10px] px-1.5 py-0.2 rounded bg-amber-500/20 border border-amber-500/30 text-amber-300">离线</span>
              </div>
              <p class="text-[11px] text-amber-300/80 mt-0.5">
                请在终端 2 运行：<code class="px-1.5 py-0.5 rounded bg-slate-900 text-amber-200 font-mono">cd backend; .\.venv\Scripts\python.exe -m app.main</code>
              </p>
            </div>
          </div>
          <button
            @click="refreshAllData"
            class="self-end sm:self-center px-3 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs transition-colors shrink-0 shadow"
          >
            重试连接
          </button>
        </div>

        <!-- 1. 监控大盘指标卡片 -->
        <MetricsCard
          :metrics="metricsSummary"
          @refresh="loadMetrics"
          @inspectDevice="handleInspectDevice"
        />

        <!-- 2. 运维工单实时看板 (左侧提单即时黄色高亮新增行) -->
        <TicketTable
          :tickets="tickets"
          :highlightedTicketNo="highlightedTicketNo"
          @refresh="loadTickets"
          @updateStatus="handleUpdateTicketStatus"
          @inspectTicket="handleInspectTicket"
        />

        <!-- 3. 机房资产设备台账 (支持健康/借用变更双向联动) -->
        <AssetTable
          :assets="assets"
          :highlightedAssetNo="highlightedAssetNo"
          @refresh="loadAssets"
          @borrowAsset="handleBorrowAsset"
          @returnAsset="handleReturnAsset"
          @updateHealth="handleUpdateAssetHealth"
          @inspectAsset="handleInspectAsset"
        />
      </section>
    </div>

    <!-- 历史会话抽屉弹窗 -->
    <div
      v-if="showSessionDrawer"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
      @click.self="showSessionDrawer = false"
    >
      <div class="w-full max-w-lg rounded-2xl bg-slate-900 border border-slate-700/80 p-5 space-y-4 shadow-2xl flex flex-col max-h-[80vh]">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center space-x-2">
            <span class="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <h3 class="font-semibold text-slate-100 text-sm">系统历史会话列表</h3>
          </div>
          <button
            @click="showSessionDrawer = false"
            class="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800"
          >
            ✕
          </button>
        </div>

        <div class="overflow-y-auto space-y-2 flex-1 pr-1">
          <div v-if="sessionList.length === 0" class="py-8 text-center text-slate-500 text-xs">
            暂无历史会话记录
          </div>
          <div
            v-for="s in sessionList"
            :key="s.session_id"
            @click="switchToSession(s.session_id)"
            :class="[
              'p-3 rounded-xl border cursor-pointer transition-all space-y-1',
              s.session_id === currentSessionId
                ? 'bg-emerald-950/40 border-emerald-500/40 ring-1 ring-emerald-500/30'
                : 'bg-slate-800/50 hover:bg-slate-800 border-slate-700/50'
            ]"
          >
            <div class="flex items-center justify-between text-xs">
              <span class="font-mono text-cyan-300 font-medium">{{ s.session_id }}</span>
              <span class="text-[10px] text-slate-400 font-mono">{{ s.last_activity }}</span>
            </div>
            <p class="text-xs text-slate-300 truncate">{{ s.last_message || '（空对话）' }}</p>
            <div class="text-[10px] text-slate-500">
              消息总数：{{ s.message_count }} 条
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ChatStream from './components/Chat/ChatStream.vue'
import ChatInput from './components/Chat/ChatInput.vue'
import MetricsCard from './components/Dashboard/MetricsCard.vue'
import TicketTable from './components/Dashboard/TicketTable.vue'
import AssetTable from './components/Dashboard/AssetTable.vue'
import { api } from './api/client'
import { fetchSSE } from './api/sse'

// 对话状态
const currentSessionId = ref('')
const currentTraceId = ref('')
const messages = ref([])
const isStreaming = ref(false)
const chatStreamRef = ref(null)
let abortController = null

// 后端服务连通状态
const backendConnected = ref(false)

// 看板状态
const metricsSummary = ref({})
const tickets = ref([])
const assets = ref([])

// 联动高亮状态
const highlightedTicketNo = ref('')
const highlightedAssetNo = ref('')
let ticketHighlightTimer = null
let assetHighlightTimer = null

// 历史会话抽屉状态
const showSessionDrawer = ref(false)
const sessionList = ref([])

// 初始化加载
onMounted(async () => {
  startNewSession()
  await refreshAllData()
})

function startNewSession() {
  currentSessionId.value = `sess-${Date.now().toString(36)}`
  currentTraceId.value = ''
  messages.value = []
}

async function openSessionDrawer() {
  showSessionDrawer.value = true
  try {
    const res = await api.listChatSessions()
    if (res.status === 'success') {
      sessionList.value = res.data
    }
  } catch (err) {
    console.error('加载历史会话失败:', err)
  }
}

async function switchToSession(sessionId) {
  currentSessionId.value = sessionId
  currentTraceId.value = ''
  showSessionDrawer.value = false
  try {
    const historyRecords = await api.getChatHistory(sessionId)
    messages.value = (historyRecords || []).map((h) => ({
      id: `hist-${h.id}`,
      role: h.role,
      content: h.content || '',
      thought: h.thought || '',
      isThinking: false,
      isStreaming: false,
      toolCalls: [],
      citations: [],
      created_at: h.created_at,
    }))
  } catch (err) {
    console.error('加载会话消息失败:', err)
  }
}

async function refreshAllData() {
  await Promise.allSettled([loadMetrics(), loadTickets(), loadAssets()])
}

async function loadMetrics() {
  try {
    const res = await api.getMetricsSummary()
    if (res.status === 'success') {
      metricsSummary.value = res.data
      backendConnected.value = true
    }
  } catch (err) {
    backendConnected.value = false
    console.error('加载机房指标失败:', err)
  }
}

async function loadTickets() {
  try {
    const list = await api.listTickets({ limit: 50 })
    tickets.value = list
  } catch (err) {
    console.error('加载工单列表失败:', err)
  }
}

async function loadAssets() {
  try {
    const list = await api.listAssets({ limit: 50 })
    assets.value = list
  } catch (err) {
    console.error('加载资产台账失败:', err)
  }
}

// -------------------------------------------------------------
// SSE 对话交互与事件分发核心
// -------------------------------------------------------------
async function handleSendMessage(promptText) {
  if (isStreaming.value || !promptText.trim()) return

  // 1. 追加用户消息
  const userMsgId = `usr-${Date.now()}`
  messages.value.push({
    id: userMsgId,
    role: 'user',
    content: promptText,
    created_at: new Date().toISOString(),
  })

  // 2. 预备 Assistant 消息容器
  const assistantMsgId = `ast-${Date.now()}`
  const assistantMsg = {
    id: assistantMsgId,
    role: 'assistant',
    content: '',
    thought: '',
    isThinking: true,
    step: 1,
    toolCalls: [],
    citations: [],
    isStreaming: true,
    created_at: new Date().toISOString(),
  }
  messages.value.push(assistantMsg)
  isStreaming.value = true

  abortController = new AbortController()

  await fetchSSE({
    prompt: promptText,
    sessionId: currentSessionId.value,
    signal: abortController.signal,
    onEvent: (event) => {
      handleIncomingSSEEvent(event, assistantMsg)
    },
    onError: (err) => {
      assistantMsg.content += `\n【网络异常或服务错误】: ${err.message}`
      assistantMsg.isThinking = false
      assistantMsg.isStreaming = false
    },
    onFinish: () => {
      assistantMsg.isThinking = false
      assistantMsg.isStreaming = false
      isStreaming.value = false
    },
  })
}

function handleIncomingSSEEvent(event, assistantMsg) {
  const { type } = event

  if (type === 'think') {
    assistantMsg.thought = (assistantMsg.thought ? assistantMsg.thought + '\n' : '') + (event.thought || '')
    assistantMsg.step = event.step || assistantMsg.step
    assistantMsg.isThinking = true
  } else if (type === 'tool_start') {
    assistantMsg.isThinking = false
    assistantMsg.toolCalls.push({
      tool_call_id: event.tool_call_id,
      name: event.name,
      args: event.args,
      step: event.step,
      result: null,
    })
  } else if (type === 'tool_end') {
    const targetCall = assistantMsg.toolCalls.find(
      (tc) => (event.tool_call_id && tc.tool_call_id === event.tool_call_id) ||
              (tc.name === event.name && tc.step === event.step && !tc.result)
    ) || assistantMsg.toolCalls[assistantMsg.toolCalls.length - 1]
    if (targetCall) {
      targetCall.result = event.result
    }
  } else if (type === 'citation') {
    assistantMsg.citations.push({
      source: event.source,
      section: event.section,
      content: event.content,
      step: event.step,
    })
  } else if (type === 'ticket_mutation') {
    // 左右业务联动：工单突变，刷新看板并触发黄色高亮动画！
    triggerTicketHighlight(event.ticket_no)
    loadTickets()
    loadMetrics()
  } else if (type === 'asset_mutation') {
    // 左右业务联动：资产突变，刷新台账与指标
    triggerAssetHighlight(event.asset_no)
    loadAssets()
    loadMetrics()
  } else if (type === 'content') {
    assistantMsg.isThinking = false
    assistantMsg.content = event.text || assistantMsg.content
  } else if (type === 'error') {
    assistantMsg.isThinking = false
    assistantMsg.isStreaming = false
    assistantMsg.content += (assistantMsg.content ? '\n\n' : '') + `【系统错误】: ${event.message || '内部处理发生异常'}`
  } else if (type === 'done') {
    currentSessionId.value = event.session_id || currentSessionId.value
    currentTraceId.value = event.trace_id || ''
    assistantMsg.isThinking = false
    assistantMsg.isStreaming = false
  }
}

function triggerTicketHighlight(ticketNo) {
  if (!ticketNo) return
  highlightedTicketNo.value = ticketNo
  if (ticketHighlightTimer) clearTimeout(ticketHighlightTimer)
  ticketHighlightTimer = setTimeout(() => {
    highlightedTicketNo.value = ''
  }, 4000)
}

function triggerAssetHighlight(assetNo) {
  if (!assetNo) return
  highlightedAssetNo.value = assetNo
  if (assetHighlightTimer) clearTimeout(assetHighlightTimer)
  assetHighlightTimer = setTimeout(() => {
    highlightedAssetNo.value = ''
  }, 4000)
}

function handleAbortStream() {
  if (abortController) {
    abortController.abort()
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg && lastMsg.role === 'assistant') {
      lastMsg.isThinking = false
      lastMsg.isStreaming = false
      if (!lastMsg.content) {
        lastMsg.content = '【已由管理员主动中止回答】'
      } else {
        lastMsg.content += ' (已中止)'
      }
    }
    isStreaming.value = false
  }
}

// -------------------------------------------------------------
// 右侧看板向左侧逆向联动事件
// -------------------------------------------------------------
function handleInspectDevice(deviceId) {
  handleSendMessage(`查询 ${deviceId} 的实时监控指标，若发现异常请按机房规范自动创建检修工单`)
}

function handleInspectAsset(assetNo) {
  handleSendMessage(`巡检设备 ${assetNo} 的当前健康状态与借用情况`)
}

function handleInspectTicket(ticketNo) {
  handleSendMessage(`查询工单 ${ticketNo} 的详细处置进展与排查说明`)
}

async function handleUpdateTicketStatus(ticketId, newStatus) {
  try {
    await api.updateTicket(ticketId, { status: newStatus })
    await loadTickets()
    await loadMetrics()
  } catch (err) {
    alert(`工单状态更新失败: ${err.message}`)
  }
}

async function handleBorrowAsset(assetNo, borrower) {
  handleSendMessage(`帮 ${borrower} 办理设备 ${assetNo} 的借用登记`)
}

async function handleReturnAsset(assetNo) {
  handleSendMessage(`办理设备 ${assetNo} 的归还登记`)
}

async function handleUpdateAssetHealth(assetId, healthStatus) {
  try {
    const asset = assets.value.find((a) => a.id === assetId)
    if (!asset) return
    await api.updateAsset(assetId, { health_status: healthStatus })
    triggerAssetHighlight(asset.asset_no)
    await loadAssets()
    await loadMetrics()
  } catch (err) {
    alert(`更新资产健康状态失败: ${err.message}`)
  }
}
</script>
