<template>
  <div
    class="flex flex-col h-screen w-screen overflow-hidden bg-transparent text-zinc-100 font-sans relative selection:bg-indigo-500/30 selection:text-white"
    :class="{ 'select-none': isDragging }"
  >
    <!-- Codex 专属原生 HTML5 Canvas 2D 动态极光流体与鼠标 ASCII 水滴粒子背景 -->
    <CodexCanvasBackground :isPaused="!isBgAnimationActive" />

    <!-- 顶部全局导航栏 (Codex Glass Minimalist Bar) -->
    <header class="h-14 border-b glass-panel px-4 flex items-center justify-between shrink-0 z-20 relative">
      <div class="flex items-center space-x-3">
        <!-- 品牌标识 SVG (机房运维意向：齿轮 + 交叉扳手螺丝刀) -->
        <div class="w-8 h-8 rounded-lg bg-zinc-900/90 border border-indigo-500/20 flex items-center justify-center shadow-sm group hover:border-indigo-500/40 transition-colors">
          <svg class="w-5 h-5 transition-transform duration-300 group-hover:scale-105" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="labops-nav-logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#818cf8" />
                <stop offset="50%" stop-color="#6366f1" />
                <stop offset="100%" stop-color="#38bdf8" />
              </linearGradient>
              <linearGradient id="labops-nav-tool-grad" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#818cf8" />
              </linearGradient>
              <mask id="labops-wrench-cutout">
                <rect width="100" height="100" fill="white" />
                <path d="M 40.3,29.4 L 37.2,14.2 L 34.4,12.1 L 31.1,10.9 L 27.6,10.7 L 24.2,11.5 L 21.2,13.3 L 18.8,15.8 L 17.3,19.0 L 24.8,12.4 L 30.4,18.1 L 31.5,25.5 L 24.1,24.4 L 18.4,18.8 L 25.0,11.3 L 21.8,12.8 L 19.3,15.2 L 17.5,18.2 L 16.7,21.6 L 16.9,25.1 L 18.1,28.4 L 20.2,31.2 L 35.4,34.3 L 62.3,61.2 L 65.4,76.4 L 66.9,77.6 L 68.5,78.6 L 70.2,79.3 L 72.0,79.8 L 73.9,79.9 L 75.8,79.8 L 77.6,79.3 L 77.8,78.2 L 72.2,72.5 L 71.1,65.1 L 78.5,66.2 L 84.2,71.8 L 85.3,71.6 L 85.8,69.8 L 85.9,67.9 L 85.8,66.0 L 85.3,64.2 L 84.6,62.5 L 83.6,60.9 L 82.4,59.4 L 67.2,56.3 Z" fill="black" stroke="black" stroke-width="6" stroke-linejoin="round" />
              </mask>
            </defs>
            <g mask="url(#labops-wrench-cutout)">
              <path fill-rule="evenodd" d="M 37.0,20.8 L 39.1,11.3 L 48.9,11.3 L 51.0,20.8 L 61.1,25.0 L 69.3,19.7 L 76.3,26.7 L 71.0,34.9 L 75.2,45.0 L 84.7,47.1 L 84.7,56.9 L 75.2,59.0 L 71.0,69.1 L 76.3,77.3 L 69.3,84.3 L 61.1,79.0 L 51.0,83.2 L 48.9,92.7 L 39.1,92.7 L 37.0,83.2 L 26.9,79.0 L 18.7,84.3 L 11.7,77.3 L 17.0,69.1 L 12.8,59.0 L 3.3,56.9 L 3.3,47.1 L 12.8,45.0 L 17.0,34.9 L 11.7,26.7 L 18.7,19.7 L 26.9,25.0 Z M 65.0,52.0 L 64.3,57.4 L 62.2,62.5 L 58.8,66.8 L 54.5,70.2 L 49.4,72.3 L 44.0,73.0 L 38.6,72.3 L 33.5,70.2 L 29.2,66.8 L 25.8,62.5 L 23.7,57.4 L 23.0,52.0 L 23.7,46.6 L 25.8,41.5 L 29.2,37.2 L 33.5,33.8 L 38.6,31.7 L 44.0,31.0 L 49.4,31.7 L 54.5,33.8 L 58.8,37.2 L 62.2,41.5 L 64.3,46.6 Z" fill="url(#labops-nav-logo-grad)" opacity="0.92" />
              <path d="M 78.9,20.7 L 75.3,17.1 L 69.7,19.9 L 68.3,24.2 L 42.1,50.4 L 40.0,48.2 L 28.0,60.3 L 26.7,62.3 L 26.4,64.8 L 27.2,67.1 L 28.9,68.8 L 31.2,69.6 L 33.7,69.3 L 35.7,68.0 L 47.8,56.0 L 45.6,53.9 L 71.8,27.7 L 76.1,26.3 Z" fill="url(#labops-nav-tool-grad)" />
            </g>
            <path d="M 40.3,29.4 L 37.2,14.2 L 34.4,12.1 L 31.1,10.9 L 27.6,10.7 L 24.2,11.5 L 21.2,13.3 L 18.8,15.8 L 17.3,19.0 L 24.8,12.4 L 30.4,18.1 L 31.5,25.5 L 24.1,24.4 L 18.4,18.8 L 25.0,11.3 L 21.8,12.8 L 19.3,15.2 L 17.5,18.2 L 16.7,21.6 L 16.9,25.1 L 18.1,28.4 L 20.2,31.2 L 35.4,34.3 L 62.3,61.2 L 65.4,76.4 L 66.9,77.6 L 68.5,78.6 L 70.2,79.3 L 72.0,79.8 L 73.9,79.9 L 75.8,79.8 L 77.6,79.3 L 77.8,78.2 L 72.2,72.5 L 71.1,65.1 L 78.5,66.2 L 84.2,71.8 L 85.3,71.6 L 85.8,69.8 L 85.9,67.9 L 85.8,66.0 L 85.3,64.2 L 84.6,62.5 L 83.6,60.9 L 82.4,59.4 L 67.2,56.3 Z" fill="url(#labops-nav-logo-grad)" stroke="rgba(255,255,255,0.2)" stroke-width="0.8" stroke-linejoin="round" />
          </svg>
        </div>
        <div>
          <h1 class="text-sm font-semibold text-zinc-100 tracking-wide glass-text">
            LabOps-Agent
          </h1>
        </div>
      </div>

      <!-- 右侧全局控制与状态 -->
      <div class="flex items-center space-x-2 text-xs">
        <!-- 玻璃视效与背景动力学控制器 -->
        <GlassController v-model:bgAnimation="isBgAnimationActive" />

        <!-- 后端服务动态连接状态 -->
        <div
          @click="refreshAllData"
          class="hidden md:flex items-center space-x-1.5 px-3 py-1 rounded-full border text-[11px] cursor-pointer transition-all shadow-sm"
          :class="backendConnected ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20' : 'bg-rose-500/10 border-rose-500/20 text-rose-400 hover:bg-rose-500/20'"
          :title="backendConnected ? 'FastAPI 后端服务正常连接 (端口 8000)' : 'FastAPI 后端服务未连接，点击重试'"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="backendConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400 animate-ping'"></span>
          <span>{{ backendConnected ? 'FastAPI 8000 在线' : 'FastAPI 8000 离线' }}</span>
        </div>

        <button
          @click="openSessionDrawer"
          class="p-2 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-white/[0.08] hover:border-white/[0.15] transition-all shadow-sm active:scale-95"
          title="历史会话"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
            <path d="M12 7v5l4 2" />
          </svg>
        </button>

        <button
          @click="startNewSession"
          class="p-2 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-medium transition-all shadow-sm active:scale-95"
          title="新建会话"
        >
          <svg class="w-3.5 h-3.5 text-zinc-950" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 4v16m8-8H4" />
          </svg>
        </button>

        <button
          @click="refreshAllData"
          class="p-2 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-white/[0.08] hover:border-white/[0.15] transition-all active:scale-95 shadow-sm"
          title="刷新大盘全部数据"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </header>

    <!-- 左右交互区 (支持动态可拖拽分栏比例) -->
    <div class="flex-1 flex flex-col lg:flex-row overflow-hidden relative z-10">
      <!-- 左侧：AI 推理与对话流面板 -->
      <section
        class="w-full h-[50vh] lg:h-full flex flex-col border-b lg:border-b-0 lg:border-r glass-panel overflow-hidden shrink-0"
        :style="isLargeScreen ? { width: `${leftWidthPercent}%` } : {}"
      >
        <!-- 左侧面板顶栏 -->
        <div class="px-4 py-2 bg-white/[0.02] border-b border-white/[0.06] flex items-center justify-between text-xs text-zinc-400">
          <div class="flex items-center space-x-2">
            <span class="font-medium text-zinc-200 flex items-center gap-1.5 glass-text">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              ReAct 推理流
            </span>
            <span class="px-2 py-0.5 rounded-md bg-zinc-900/80 border border-white/[0.06] font-mono text-[10px] text-zinc-400">
              {{ currentSessionId || '未初始化' }}
            </span>
          </div>
          <div v-if="currentTraceId" class="text-[10px] font-mono text-zinc-500">
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

      <!-- 中间：交互式分栏拖拽手柄 (Resize Divider) -->
      <div
        class="hidden lg:flex items-center justify-center split-handle bg-transparent hover:bg-indigo-500/30 transition-colors z-20 group"
        :class="{ 'is-dragging': isDragging }"
        @mousedown="startDragging"
        @touchstart.passive="startDragging"
        @dblclick="resetSplit"
        title="按住左右拖拽调整分栏比例 (30%~70%)，双击复位"
      >
        <div class="w-1 h-8 rounded-full bg-zinc-700/60 group-hover:bg-indigo-400 transition-colors"></div>
      </div>

      <!-- 右侧：实时数据看板与业务分段流转区 -->
      <section class="flex-1 flex flex-col bg-transparent overflow-hidden min-w-0">
        <!-- 右侧顶部 Segmented Controls Tab 导航栏 -->
        <div class="px-4 py-2.5 glass-panel border-b flex items-center justify-between shrink-0">
          <!-- 分段控制器 Tabs -->
          <div class="flex items-center space-x-1 bg-zinc-900/80 p-1 rounded-xl border border-white/[0.08] shadow-sm text-xs">
            <button
              @click="currentTab = 'overview'"
              :class="[
                'px-3 py-1.5 rounded-lg font-medium transition-all flex items-center space-x-1.5',
                currentTab === 'overview'
                  ? 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              ]"
            >
              <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
              <span>全景概览</span>
            </button>

            <button
              @click="currentTab = 'tickets'"
              :class="[
                'px-3 py-1.5 rounded-lg font-medium transition-all flex items-center space-x-1.5',
                currentTab === 'tickets'
                  ? 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              ]"
            >
              <svg class="w-3.5 h-3.5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
              <span>运维工单</span>
              <span
                v-if="pendingTicketCount > 0"
                class="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30"
              >
                {{ pendingTicketCount }}
              </span>
            </button>

            <button
              @click="currentTab = 'assets'"
              :class="[
                'px-3 py-1.5 rounded-lg font-medium transition-all flex items-center space-x-1.5',
                currentTab === 'assets'
                  ? 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              ]"
            >
              <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span>资产台账</span>
              <span class="px-1.5 py-0.5 rounded-full text-[10px] font-mono bg-zinc-800 text-zinc-400 border border-white/[0.08]">
                {{ assets.length }}
              </span>
            </button>
          </div>

          <!-- 右侧轻量指标状态 -->
          <div class="hidden sm:flex items-center space-x-3 text-xs text-zinc-400">
            <div class="flex items-center space-x-1.5">
              <span class="text-zinc-500">机房均温:</span>
              <span class="font-mono text-zinc-200" :class="avgTemp > 40 ? 'text-rose-400' : ''">{{ avgTemp }}℃</span>
            </div>
            <span class="text-zinc-700">|</span>
            <div class="flex items-center space-x-1.5">
              <span class="text-zinc-500">健康率:</span>
              <span class="font-mono text-emerald-400">{{ healthRate }}%</span>
            </div>
          </div>
        </div>

        <!-- 看板正文展示区 (可滚动) -->
        <div class="flex-1 overflow-y-auto p-3 sm:p-4 space-y-4">
          <!-- 后端未启动引导条 (Linear Warning Card) -->
          <div
            v-if="!backendConnected"
            class="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-amber-200 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 shadow-sm"
          >
            <div class="flex items-center space-x-2.5">
              <span class="p-1 rounded-md bg-amber-500/10 text-amber-400 shrink-0">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </span>
              <div>
                <div class="font-medium text-amber-100 flex items-center gap-1.5">
                  FastAPI 后端服务 (端口 8000) 尚未连接
                  <span class="text-[10px] px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400 font-mono">离线</span>
                </div>
                <p class="text-[11px] text-amber-300/70 mt-0.5">
                  请确认终端已启动后端服务：<code class="px-1.5 py-0.5 rounded bg-black/40 backdrop-blur-sm border border-amber-500/20 text-amber-300 font-mono">cd backend; .\.venv\Scripts\python.exe -m app.main</code>
                </p>
              </div>
            </div>
            <button
              @click="refreshAllData"
              class="self-end sm:self-center px-3 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 text-amber-200 font-medium text-xs transition-colors shrink-0 shadow-sm active:scale-95"
            >
              重试连接
            </button>
          </div>

          <!-- Tab 1: 全景概览 Bento 磁贴看板 -->
          <div v-show="currentTab === 'overview'" class="animate-fade-in">
            <OverviewBento
              :metrics="metricsSummary"
              :tickets="tickets"
              :assets="assets"
              :highlightedTicketNo="highlightedTicketNo"
              :highlightedAssetNo="highlightedAssetNo"
              @refresh="refreshAllData"
              @switchTab="handleSwitchTab"
              @inspectDevice="handleInspectDevice"
              @inspectTicket="handleInspectTicket"
              @inspectAsset="handleInspectAsset"
              @quickAction="handleQuickAction"
            />
          </div>

          <!-- Tab 2: 运维工单流转库 -->
          <div v-show="currentTab === 'tickets'" class="animate-fade-in">
            <TicketTable
              :tickets="tickets"
              :highlightedTicketNo="highlightedTicketNo"
              @refresh="loadTickets"
              @updateStatus="handleUpdateTicketStatus"
              @inspectTicket="handleInspectTicket"
            />
          </div>

          <!-- Tab 3: 机房设备资产台账 -->
          <div v-show="currentTab === 'assets'" class="animate-fade-in">
            <AssetTable
              :assets="assets"
              :highlightedAssetNo="highlightedAssetNo"
              @refresh="loadAssets"
              @borrowAsset="handleBorrowAsset"
              @returnAsset="handleReturnAsset"
              @updateHealth="handleUpdateAssetHealth"
              @inspectAsset="handleInspectAsset"
            />
          </div>
        </div>
      </section>
    </div>

    <!-- 历史会话抽屉弹窗 (Linear Modal) -->
    <div
      v-if="showSessionDrawer"
      @keydown.esc.window="showSessionDrawer = false"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in"
      @click.self="showSessionDrawer = false"
    >
      <div class="w-full max-w-lg rounded-2xl glass-card border border-white/[0.12] p-5 space-y-4 shadow-2xl flex flex-col max-h-[80vh] backdrop-blur-xl">
        <div class="flex items-center justify-between border-b border-white/[0.08] pb-3">
          <div class="flex items-center space-x-2">
            <span class="p-1.5 rounded-lg bg-zinc-900/90 border border-white/[0.08] text-indigo-400">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <h3 class="font-medium text-zinc-100 text-sm glass-text">系统历史运维会话列表</h3>
          </div>
          <button
            @click="showSessionDrawer = false"
            class="text-zinc-500 hover:text-zinc-300 p-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="overflow-y-auto space-y-2 flex-1 pr-1">
          <div v-if="sessionList.length === 0" class="py-8 text-center text-zinc-500 text-xs">
            暂无历史会话记录
          </div>
          <div
            v-for="s in sessionList"
            :key="s.session_id"
            @click="switchToSession(s.session_id)"
            :class="[
              'p-3.5 rounded-xl border cursor-pointer transition-all space-y-1.5',
              s.session_id === currentSessionId
                ? 'bg-indigo-950/40 border-indigo-500/40 ring-1 ring-indigo-500/30'
                : 'glass-card-sub hover:bg-white/[0.08] border-white/[0.06] hover:border-white/[0.14]'
            ]"
          >
            <div class="flex items-center justify-between text-xs">
              <span class="font-mono text-zinc-200 font-medium">{{ s.session_id }}</span>
              <span class="text-[10px] text-zinc-500 font-mono">{{ s.last_activity }}</span>
            </div>
            <p class="text-xs text-zinc-400 truncate">{{ s.last_message || '（空对话）' }}</p>
            <div class="text-[10px] text-zinc-500">
              消息总数：{{ s.message_count }} 条
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import CodexCanvasBackground from './components/Background/CodexCanvasBackground.vue'
import GlassController from './components/Common/GlassController.vue'
import ChatStream from './components/Chat/ChatStream.vue'
import ChatInput from './components/Chat/ChatInput.vue'
import OverviewBento from './components/Dashboard/OverviewBento.vue'
import TicketTable from './components/Dashboard/TicketTable.vue'
import AssetTable from './components/Dashboard/AssetTable.vue'
import { api } from './api/client'
import { fetchSSE } from './api/sse'

// Codex 动态背景启停状态 (同步读取 localStorage 避免冷启动闪烁)
function getSavedBgAnimation() {
  try {
    const saved = localStorage.getItem('labops_glass_config')
    if (saved) {
      const config = JSON.parse(saved)
      if (typeof config.bgAnimation === 'boolean') return config.bgAnimation
    }
  } catch {}
  return true
}
const isBgAnimationActive = ref(getSavedBgAnimation())

// 对话与流状态
const currentSessionId = ref('')
const currentTraceId = ref('')
const messages = ref([])
const isStreaming = ref(false)
const chatStreamRef = ref(null)
let abortController = null

// 分栏宽度与拖拽状态 (30% ~ 70%，默认 46%)
const leftWidthPercent = ref(46)
const isDragging = ref(false)
const isLargeScreen = ref(true)

function checkScreenSize() {
  isLargeScreen.value = window.innerWidth >= 1024
}

function startDragging(e) {
  if (e.type === 'mousedown') {
    e.preventDefault()
  }
  isDragging.value = true
  window.addEventListener('mousemove', onDragging)
  window.addEventListener('mouseup', stopDragging)
  window.addEventListener('touchmove', onTouchDragging, { passive: false })
  window.addEventListener('touchend', stopDragging)
}

function onDragging(e) {
  if (!isDragging.value) return
  const totalWidth = window.innerWidth
  const newPercent = (e.clientX / totalWidth) * 100
  // 严格约束 30% 到 70% 边界
  leftWidthPercent.value = Math.min(Math.max(newPercent, 30), 70)
}

function onTouchDragging(e) {
  if (!isDragging.value || !e.touches || e.touches.length === 0) return
  e.preventDefault()
  const touch = e.touches[0]
  const totalWidth = window.innerWidth
  const newPercent = (touch.clientX / totalWidth) * 100
  leftWidthPercent.value = Math.min(Math.max(newPercent, 30), 70)
}

function stopDragging() {
  if (isDragging.value) {
    isDragging.value = false
    window.removeEventListener('mousemove', onDragging)
    window.removeEventListener('mouseup', stopDragging)
    window.removeEventListener('touchmove', onTouchDragging)
    window.removeEventListener('touchend', stopDragging)
  }
}

function resetSplit() {
  leftWidthPercent.value = 46
}

// 右侧分段 Tab 控制
const currentTab = ref('overview')

function handleSwitchTab(tabName) {
  currentTab.value = tabName
}

function handleQuickAction(prompt) {
  handleSendMessage(prompt)
}

// 后端服务连通状态
const backendConnected = ref(false)

// 看板数据
const metricsSummary = ref({})
const tickets = ref([])
const assets = ref([])

// 统计衍生属性
const overview = computed(() => metricsSummary.value?.overview || {})
const avgTemp = computed(() => overview.value.avg_temperature || 24.5)
const healthRate = computed(() => overview.value.system_health_rate || 100)
const pendingTicketCount = computed(() => tickets.value.filter((t) => t.status === 'PENDING').length)

// 联动高亮状态
const highlightedTicketNo = ref('')
const highlightedAssetNo = ref('')
let ticketHighlightTimer = null
let assetHighlightTimer = null

// 历史会话抽屉状态
const showSessionDrawer = ref(false)
const sessionList = ref([])

onMounted(async () => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  startNewSession()
  await refreshAllData()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  stopDragging()
  if (ticketHighlightTimer) clearTimeout(ticketHighlightTimer)
  if (assetHighlightTimer) clearTimeout(assetHighlightTimer)
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
    // 左右业务联动：工单突变，自动切换至工单Tab，刷新看板并触发黄色高亮动画！
    currentTab.value = 'tickets'
    triggerTicketHighlight(event.ticket_no)
    loadTickets()
    loadMetrics()
  } else if (type === 'asset_mutation') {
    // 左右业务联动：资产突变，自动切换至资产Tab，刷新台账与指标并触发高亮动画！
    currentTab.value = 'assets'
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
