<template>
  <div
    class="flex flex-col h-screen w-screen overflow-hidden bg-transparent font-sans relative selection:bg-indigo-500/30 selection:text-white"
    :class="[
      currentTheme === 'light' ? 'text-zinc-900' : 'text-zinc-100',
      { 'select-none': isDragging }
    ]"
  >
    <!-- Codex 专属原生 HTML5 Canvas 2D 动态极光流体与鼠标 ASCII 水滴粒子背景 -->
    <CodexCanvasBackground :isPaused="!isBgAnimationActive" :theme="currentTheme" />

    <!-- 顶部全局导航栏 (Codex Glass Minimalist Bar) -->
    <header class="h-14 border-b glass-panel px-4 flex items-center justify-between shrink-0 z-20 relative">
      <div class="flex items-center space-x-3">
        <!-- 品牌标识 SVG (机房运维意向：齿轮 + 交叉扳手螺丝刀) -->
        <div
          class="w-8 h-8 rounded-lg border flex items-center justify-center shadow-sm group transition-colors"
          :class="[
            currentTheme === 'light'
              ? 'bg-white/90 border-slate-200 hover:border-indigo-500/40'
              : 'bg-zinc-900/90 border-indigo-500/20 hover:border-indigo-500/40'
          ]"
        >
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
          <h1 class="text-sm font-semibold tracking-wide glass-text flex items-center gap-2" title="面向高校实验室的轻量化智能自治运维系统">
            <span>LabOps-Agent</span>
            <span class="text-xs text-zinc-400 font-normal hidden lg:inline border-l border-white/10 pl-2">面向高校实验室的轻量化智能自治运维系统</span>
          </h1>
        </div>
      </div>

      <!-- 右侧全局控制与状态 -->
      <div class="flex items-center space-x-2 text-xs">
        <!-- 用户身份与账户中心收敛小图标 (合二为一：仅保留小图标，点击展开下拉框：个人档案、权限切换) -->
        <div class="relative inline-block text-left">
          <button
            @click.stop="toggleUserMenu"
            class="p-2 rounded-xl border text-xs flex items-center justify-center transition-all shadow-sm active:scale-95 select-none relative group"
            :class="userIconClass"
            :title="userIconTitle"
          >
            <!-- 人物矢量 SVG 图标 -->
            <svg class="w-3.5 h-3.5 transition-transform duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </button>

          <!-- 下拉菜单浮层 -->
          <div
            v-if="showUserMenu"
            @click.stop
            :class="[
              'absolute right-0 w-44 py-1.5 rounded-xl border shadow-xl z-50 backdrop-blur-xl transition-all text-xs font-sans text-left mt-1.5',
              currentTheme === 'light'
                ? 'bg-white/95 border-slate-200 text-slate-800 shadow-slate-200/60'
                : 'bg-zinc-900/95 border-white/[0.12] text-zinc-200 ring-1 ring-white/[0.05] shadow-2xl'
            ]"
          >
            <!-- 已登录状态：展示轻量身份摘要与个人档案、权限切换两项操作 -->
            <template v-if="isLoggedIn">
              <div class="px-3 py-1.5 border-b" :class="currentTheme === 'light' ? 'border-slate-100 bg-slate-50/60' : 'border-white/[0.06] bg-white/[0.02]'">
                <div class="font-medium truncate text-xs">{{ currentUser.real_name }}</div>
                <div class="text-[10px] text-zinc-400 font-mono flex items-center justify-between pt-0.5">
                  <span>{{ currentUser.username }}</span>
                  <span class="px-1.5 py-0.2 rounded text-[10px] font-sans border" :class="userRoleClass(currentUser.role)">{{ userRoleLabel(currentUser.role) }}</span>
                </div>
              </div>

              <!-- 按钮 1：个人档案 -->
              <button
                @click="showUserMenu = false; handleOpenUserProfile(currentUser.username)"
                class="w-full px-3 py-2 flex items-center space-x-2 transition-colors text-left"
                :class="currentTheme === 'light' ? 'hover:bg-slate-100 text-slate-700 hover:text-indigo-600' : 'hover:bg-white/[0.08] text-zinc-300 hover:text-indigo-300'"
              >
                <svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>个人档案</span>
              </button>

              <!-- 按钮 2：权限切换 -->
              <button
                @click="showUserMenu = false; showAuthModal = true"
                class="w-full px-3 py-2 flex items-center space-x-2 transition-colors text-left"
                :class="currentTheme === 'light' ? 'hover:bg-slate-100 text-slate-700 hover:text-cyan-600' : 'hover:bg-white/[0.08] text-zinc-300 hover:text-cyan-300'"
              >
                <svg class="w-3.5 h-3.5 text-cyan-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
                <span>权限切换</span>
              </button>
            </template>

            <!-- 未登录状态：仅展示登录注册按钮 -->
            <template v-else>
              <button
                @click="showUserMenu = false; showAuthModal = true"
                class="w-full px-3 py-2 flex items-center space-x-2 transition-colors text-left font-medium"
                :class="currentTheme === 'light' ? 'hover:bg-slate-100 text-indigo-600' : 'hover:bg-white/[0.08] text-indigo-400'"
              >
                <svg class="w-3.5 h-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                <span>登录 / 注册</span>
              </button>
            </template>
          </div>
        </div>

        <!-- 站内待办通知铃铛 🔔 按钮 (含呼吸微光未读红点与数字徽标) -->
        <button
          @click="toggleNotificationToast"
          class="relative p-2 rounded-xl border text-xs flex items-center justify-center transition-all shadow-sm active:scale-95 select-none"
          :class="[
            currentTheme === 'light'
              ? 'bg-white/90 hover:bg-indigo-50/80 text-slate-700 hover:text-indigo-600 border-slate-200 hover:border-indigo-400/60 shadow-slate-200/50'
              : 'bg-zinc-900/90 hover:bg-zinc-800 text-zinc-300 hover:text-white border-white/[0.08] hover:border-indigo-500/40 shadow-black/40'
          ]"
          :title="unreadNotificationCount > 0 ? `有 ${unreadNotificationCount} 条待办通知待处理，点击查看` : '站内待办通知 (无未读)'"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <span
            v-if="unreadNotificationCount > 0"
            class="absolute -top-1 -right-1 flex h-4 min-w-4 px-1 items-center justify-center rounded-full bg-rose-500 text-[10px] font-bold text-white shadow-sm shadow-rose-500/50"
          >
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
            <span class="relative">{{ unreadNotificationCount }}</span>
          </span>
        </button>

        <!-- 风格切换按钮：清晰指示“明亮”或“暗黑”，每点击一下切换一次风格 -->
        <button
          @click="toggleTheme"
          class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center space-x-1.5 transition-all shadow-sm active:scale-95 select-none"
          :class="[
            currentTheme === 'light'
              ? 'bg-amber-50/90 hover:bg-amber-100/90 text-amber-800 border-amber-300/80 hover:border-amber-400'
              : 'bg-zinc-900/90 hover:bg-zinc-800 text-zinc-300 hover:text-white border-white/[0.08] hover:border-indigo-500/30'
          ]"
          :title="`当前为${currentTheme === 'light' ? '明亮' : '暗黑'}风格，点击切换为${currentTheme === 'light' ? '暗黑' : '明亮'}风格`"
        >
          <!-- 太阳矢量 SVG (明亮风格图标) -->
          <svg v-if="currentTheme === 'light'" class="w-3.5 h-3.5 text-amber-600 animate-fade-in" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <!-- 月亮矢量 SVG (暗黑风格图标) -->
          <svg v-else class="w-3.5 h-3.5 text-indigo-400 animate-fade-in" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
          <span class="font-medium">{{ currentTheme === 'light' ? '明亮' : '暗黑' }}</span>
        </button>

        <!-- 玻璃视效与背景动力学控制器 -->
        <GlassController v-model:bgAnimation="isBgAnimationActive" :theme="currentTheme" />

        <!-- 后端服务动态连接状态 (通俗易懂去技术化表达) -->
        <div
          @click="refreshAllData"
          class="hidden md:flex items-center space-x-1.5 px-3 py-1 rounded-full border text-[11px] cursor-pointer transition-all shadow-sm"
          :class="backendConnected ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20' : 'bg-rose-500/10 border-rose-500/20 text-rose-400 hover:bg-rose-500/20'"
          :title="backendConnected ? '机房运维后台服务运行正常' : '机房运维后台服务未连接，点击重试'"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="backendConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400 animate-ping'"></span>
          <span>{{ backendConnected ? '系统服务在线' : '系统服务离线' }}</span>
        </div>

        <button
          @click="openSessionDrawer"
          class="p-2 rounded-lg border transition-all shadow-sm active:scale-95"
          :class="[
            currentTheme === 'light'
              ? 'bg-white/90 hover:bg-indigo-50/80 text-slate-700 hover:text-indigo-600 border-slate-200 hover:border-indigo-400/60'
              : 'bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border-white/[0.08] hover:border-white/[0.15]'
          ]"
          title="历史会话"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
            <path d="M12 7v5l4 2" />
          </svg>
        </button>

        <!-- 新建会话加号按钮 (图二调优：半透微光质感，自适应页面深浅色彩，告别突兀实白方块) -->
        <button
          @click="startNewSession"
          class="p-2 rounded-lg border transition-all shadow-sm active:scale-95"
          :class="[
            currentTheme === 'light'
              ? 'bg-white/90 hover:bg-indigo-50/80 text-indigo-600 border-slate-200 hover:border-indigo-400/60'
              : 'bg-zinc-900/90 hover:bg-zinc-800 text-indigo-300 border-white/[0.08] hover:border-indigo-500/30'
          ]"
          title="新建会话"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 4v16m8-8H4" />
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
        <!-- 左侧面板顶栏 (优雅现代化包装与动态感知) -->
        <div class="px-4 py-2 bg-white/[0.02] border-b border-white/[0.06] flex items-center justify-between text-xs text-zinc-400">
          <div class="flex items-center space-x-2">
            <span class="font-medium text-zinc-200 flex items-center gap-1.5 glass-text">
              <span class="relative flex h-2 w-2">
                <span
                  v-if="isStreaming"
                  class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"
                ></span>
                <span
                  class="relative inline-flex rounded-full h-2 w-2 transition-colors duration-300"
                  :class="isStreaming ? 'bg-indigo-400' : 'bg-emerald-400'"
                ></span>
              </span>
              AI 运维管家
            </span>

            <!-- 动态状态呼吸药丸 (空闲就绪 vs 深度思考/运维工具执行动态切换) -->
            <span
              class="px-2 py-0.5 rounded-full text-[10px] font-medium flex items-center gap-1 border transition-all duration-300 shadow-sm"
              :class="[
                isStreaming
                  ? 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300 animate-pulse'
                  : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
              ]"
            >
              {{ agentStatusText }}
            </span>

            <!-- 精致轻量的会话微标 (悬停展示完整 ID，点击一键复制) -->
            <button
              @click="copySessionId"
              class="px-2 py-0.5 rounded-full text-[10px] font-mono text-zinc-400 hover:text-zinc-200 bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] hover:border-white/[0.14] transition-all flex items-center gap-1 active:scale-95 shadow-sm"
              :title="`当前会话: ${currentSessionId || '未初始化'} (点击复制)`"
            >
              <span class="text-zinc-500">#</span><span>{{ shortSessionId }}</span>
              <svg v-if="justCopied" class="w-2.5 h-2.5 text-emerald-400 animate-fade-in" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-2.5 h-2.5 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
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
          @select="handleSendMessage"
          @fill="handleFillInput"
        />

        <!-- 输入框组件 -->
        <ChatInput
          ref="chatInputRef"
          :currentUser="currentUser"
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
        title="按住左右拖拽调整分栏比例 (28%~58%)，双击复位"
      >
        <div class="w-1 h-8 rounded-full bg-zinc-700/60 group-hover:bg-indigo-400 transition-colors"></div>
      </div>

      <!-- 右侧：实时数据看板与业务分段流转区 (min-w-0 lg:min-w-[420px] 物理保护防挤压) -->
      <section class="flex-1 flex flex-col bg-transparent overflow-hidden min-w-0 lg:min-w-[420px]">
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
                :title="`当前有 ${pendingTicketCount} 起未成功归档的在办运维工单`"
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

            <button
              @click="currentTab = 'topology'"
              :class="[
                'px-3 py-1.5 rounded-lg font-medium transition-all flex items-center space-x-1.5',
                currentTab === 'topology'
                  ? 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              ]"
            >
              <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
              <span>机柜拓扑</span>
            </button>

            <button
              @click="currentTab = 'regulations'"
              :class="[
                'px-3 py-1.5 rounded-lg font-medium transition-all flex items-center space-x-1.5',
                currentTab === 'regulations'
                  ? 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
              ]"
            >
              <svg class="w-3.5 h-3.5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span>规章规程</span>
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
                  机房运维后台服务尚未连接
                  <span class="text-[10px] px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400 font-mono">离线</span>
                </div>
                <p class="text-[11px] text-amber-300/70 mt-0.5">
                  机房运维后台服务未连接，请检查后台服务是否已正常启动或点击右侧“重试连接”
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
              v-model:ttsEnabled="ttsEnabled"
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
              @patrolCompleted="handlePatrolCompleted"
            />
          </div>

          <!-- Tab 2: 运维工单流转库 -->
          <div v-show="currentTab === 'tickets'" class="animate-fade-in">
            <TicketTable
              :tickets="tickets"
              :currentUser="currentUser"
              :highlightedTicketNo="highlightedTicketNo"
              @refresh="handleRefreshTickets"
              @updateStatus="handleUpdateTicketStatus"
              @inspectTicket="handleInspectTicket"
              @viewTimeline="handleViewTicketTimeline"
            />
          </div>

          <!-- Tab 3: 机房设备资产台账 -->
          <div v-show="currentTab === 'assets'" class="animate-fade-in">
            <AssetTable
              :assets="assets"
              :currentUser="currentUser"
              :highlightedAssetNo="highlightedAssetNo"
              :overdueMap="overdueMap"
              @refresh="handleRefreshAssets"
              @borrowAsset="handleBorrowAsset"
              @returnAsset="handleReturnAsset"
              @updateHealth="handleUpdateAssetHealth"
              @inspectAsset="handleInspectAsset"
              @viewTimeline="handleViewAssetTimeline"
              @openOverdueNotice="handleOpenOverdueNotice"
            />
          </div>

          <!-- Tab 4: 机柜 2D 拓扑大盘 -->
          <div v-show="currentTab === 'topology'" class="animate-fade-in">
            <RackTopologyView
              ref="rackTopologyRef"
              :theme="currentTheme"
              :currentUser="currentUser"
              @inspectAsset="handleInspectAssetFromTopology"
              @refresh="refreshAllData"
            />
          </div>

          <!-- Tab 5: 规章规程知识中心 -->
          <div v-show="currentTab === 'regulations'" class="animate-fade-in">
            <RegulationsCenter
              :theme="currentTheme"
              :currentUser="currentUser"
              @askAI="handleAskAIAboutRegulation"
              @refresh="refreshAllData"
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
      v-backdrop-dismiss="() => showSessionDrawer = false"
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

    <!-- 用户身份鉴权与角色切换弹窗 -->
    <AuthModal
      v-model="showAuthModal"
      :currentUser="currentUser"
      @loginSuccess="handleLoginSuccess"
      @logout="handleLogout"
      @openProfile="handleOpenUserProfile"
    />

    <!-- 用户个人全景档案与安全设置弹窗 -->
    <UserProfileModal
      v-model="showCurrentUserProfileModal"
      :identifier="currentProfileIdentifier"
      :currentUser="currentUser"
      :theme="currentTheme"
      @userUpdated="handleUserUpdated"
    />

    <!-- 全网主动自治体检《运行健康研判简报》弹窗 -->
    <PatrolReportModal
      v-model="showPatrolModal"
      :report="patrolReportData"
      :theme="currentTheme"
      @inspectTicket="handleInspectTicketFromReport"
    />

    <!-- 硬件设备全景台账弹窗 (从机架拓扑槽位唤出) -->
    <DeviceDetailModal
      v-model="showTopologyDeviceModal"
      :asset="selectedTopologyAsset"
      :currentUser="currentUser"
      @inspect="handleInspectAsset"
      @borrow="handleBorrowAssetFromTopology"
      @return="handleReturnAssetFromTopology"
      @edit="handleEditAssetFromTopology"
      @delete="handleDeleteAssetFromTopology"
      @viewTimeline="handleViewAssetTimeline"
    />

    <!-- 拓扑视图设备删除二次确认模态框 (与台账删除体验保持严格一致) -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="showTopologyDeleteModal"
          @keydown.esc.window="showTopologyDeleteModal = false"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md overflow-hidden"
          v-backdrop-dismiss="() => showTopologyDeleteModal = false"
        >
          <div class="w-full max-w-sm rounded-3xl bg-zinc-900/95 border border-rose-500/30 ring-1 ring-rose-500/10 p-5 space-y-4 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] backdrop-blur-2xl">
            <div class="flex items-center space-x-3 text-rose-400">
              <div class="p-2.5 rounded-2xl bg-rose-500/10 border border-rose-500/20">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-semibold text-zinc-100 tracking-tight">确认彻底删除该设备？</h4>
                <p class="text-[11px] text-zinc-400">此操作不可撤销，硬件档案亦将清理</p>
              </div>
            </div>

            <div class="p-3 rounded-2xl bg-zinc-950/60 border border-white/[0.06] text-xs space-y-1">
              <div>目标编号: <span class="font-mono text-cyan-400 font-semibold select-all">{{ targetAssetForTopologyDelete?.asset_no }}</span></div>
              <div class="text-zinc-200 font-medium">{{ targetAssetForTopologyDelete?.name }}</div>
              <div class="text-zinc-500 font-mono text-[11px]">{{ targetAssetForTopologyDelete?.location }}</div>
              <div v-if="targetAssetForTopologyDelete?.borrow_status === 'IN_USE'" class="pt-1 text-rose-400 font-medium">
                ⚠️ 该设备处于借用中 (借用人: {{ targetAssetForTopologyDelete?.borrower || '未填写' }})！
              </div>
            </div>

            <div v-if="deleteTopologyError" class="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {{ deleteTopologyError }}
            </div>

            <div class="flex items-center justify-end space-x-2 pt-2 border-t border-white/[0.06]">
              <button
                @click="showTopologyDeleteModal = false"
                class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition-all"
              >
                取消
              </button>
              <button
                @click="confirmDeleteTopologyAsset"
                :disabled="isDeletingTopologyAsset"
                class="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md transition-all active:scale-95 disabled:opacity-50"
              >
                {{ isDeletingTopologyAsset ? '正在删除...' : '确认移除设备' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 运维工单流转与资产全生命周期履历时间轴抽屉 (Timeline Drawer) -->
    <TimelineDrawer
      v-model="showTimelineDrawer"
      :mode="timelineMode"
      :target="timelineTarget"
      :currentUser="currentUser"
      :theme="currentTheme"
      @ticketUpdated="refreshAllData"
      @userUpdated="handleUserUpdated"
    />

    <!-- 设备资产超期使用归还催告单模态框 (Overdue Notice Modal) -->
    <OverdueNoticeModal
      v-model="showOverdueNoticeModal"
      :assetNo="selectedOverdueAssetNo"
      :currentUser="currentUser"
      :theme="currentTheme"
      @promptAgent="handlePromptAgentFromNotice"
      @urgeSent="handleUrgeSentFromNotice"
    />

    <!-- 资产超期催收站内待办督促浮窗 (Urge Notification Toast) -->
    <UrgeNotificationToast
      v-model="showUrgeToast"
      :notification="activeNotification"
      :assets="assets"
      :overdueMap="overdueMap"
      :theme="currentTheme"
      @viewNotice="handleViewNoticeFromToast"
      @markRead="handleNotificationMarkRead"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import CodexCanvasBackground from './components/Background/CodexCanvasBackground.vue'
import GlassController from './components/Common/GlassController.vue'
import ChatStream from './components/Chat/ChatStream.vue'
import ChatInput from './components/Chat/ChatInput.vue'
import OverviewBento from './components/Dashboard/OverviewBento.vue'
import TicketTable from './components/Dashboard/TicketTable.vue'
import AssetTable from './components/Dashboard/AssetTable.vue'
import RackTopologyView from './components/Dashboard/RackTopologyView.vue'
import DeviceDetailModal from './components/Dashboard/DeviceDetailModal.vue'
import TimelineDrawer from './components/Dashboard/TimelineDrawer.vue'
import AuthModal from './components/Auth/AuthModal.vue'
import UserProfileModal from './components/Common/UserProfileModal.vue'
import PatrolReportModal from './components/Dashboard/PatrolReportModal.vue'
import OverdueNoticeModal from './components/Dashboard/OverdueNoticeModal.vue'
import UrgeNotificationToast from './components/Dashboard/UrgeNotificationToast.vue'
import RegulationsCenter from './components/Dashboard/RegulationsCenter.vue'
import { api } from './api/client'
import { fetchSSE } from './api/sse'

// 用户认证与权限模态框状态
const showAuthModal = ref(false)

// 时间轴抽屉状态与全局统一调度 (工单流转与资产履历双模态自适应)
const showTimelineDrawer = ref(false)
const timelineMode = ref('ticket') // 'ticket' | 'asset'
const timelineTarget = ref('')

function handleViewTicketTimeline(ticketNoOrId) {
  timelineMode.value = 'ticket'
  timelineTarget.value = ticketNoOrId
  showTimelineDrawer.value = true
}

function handleViewAssetTimeline(assetNo) {
  timelineMode.value = 'asset'
  timelineTarget.value = assetNo
  showTimelineDrawer.value = true
}

// 全网主动自治体检简报弹窗状态
const showPatrolModal = ref(false)
const patrolReportData = ref({})

// 超期借用催告公函弹窗状态与全局调度
const showOverdueNoticeModal = ref(false)
const selectedOverdueAssetNo = ref('DEV-SRV-201')
const overdueAssets = ref([])
const overdueMap = computed(() => {
  const map = {}
  ;(overdueAssets.value || []).forEach((it) => {
    map[it.asset_no] = it
  })
  return map
})

function handleOpenOverdueNotice(assetNo) {
  selectedOverdueAssetNo.value = assetNo || 'DEV-SRV-201'
  showOverdueNoticeModal.value = true
}

function handlePromptAgentFromNotice(promptText) {
  handleSendMessage(promptText)
}

function handleUrgeSentFromNotice() {
  fetchUserNotifications(currentUser.value?.username)
}

// 站内待办与超期督促通知状态
const showUrgeToast = ref(false)
const userNotifications = ref([])
const unreadNotificationCount = computed(() => {
  return (userNotifications.value || []).filter((n) => !n.is_read).length
})
const activeNotification = computed(() => {
  const unreads = (userNotifications.value || []).filter((n) => !n.is_read)
  if (unreads.length > 0) return unreads[0]
  if (userNotifications.value && userNotifications.value.length > 0) return userNotifications.value[0]
  return {
    id: 0,
    username: currentUser.value?.username || 'user',
    title: '机房运转正常，暂无未读待办',
    content: '当前机房资产借用流转与运维工单均处于合规正常周期内，暂无需要紧急催办处置的待办事宜。',
    notice_type: 'SYSTEM',
    asset_no: '',
    is_read: true,
    created_at: '',
  }
})

async function fetchUserNotifications(username) {
  if (!username) return { unread_count: 0, items: [] }
  try {
    const data = await api.getNotifications(username)
    userNotifications.value = data.items || []
    return data
  } catch (err) {
    console.error('拉取站内待办通知失败:', err)
    return { unread_count: 0, items: [] }
  }
}

function toggleNotificationToast() {
  if (userNotifications.value.length === 0) {
    fetchUserNotifications(currentUser.value?.username).then(() => {
      showUrgeToast.value = true
    })
  } else {
    showUrgeToast.value = !showUrgeToast.value
  }
}

function handleViewNoticeFromToast(assetNo) {
  handleOpenOverdueNotice(assetNo)
}

function handleNotificationMarkRead(id) {
  const target = userNotifications.value.find((n) => n.id === id)
  if (target) {
    target.is_read = true
  }
  fetchUserNotifications(currentUser.value?.username)
}

// 当前登录用户 (会话期内存状态，F5 刷新页面即安全重置为默认管理员)
const currentUser = ref({
  username: 'admin',
  real_name: '王主管',
  role: 'ADMIN',
  department: '网络中心运维部',
  phone: '13800000001',
})

function handleLoginSuccess(user) {
  currentUser.value = user
}

function handleLogout() {
  currentUser.value = {
    username: 'guest',
    real_name: '未登录访客',
    role: 'STUDENT',
    department: '未认证访客',
    phone: '',
  }
}

// 个人全景档案与安全设置模态框状态
const showCurrentUserProfileModal = ref(false)
const currentProfileIdentifier = ref('admin')

function handleOpenUserProfile(username) {
  currentProfileIdentifier.value = username || currentUser.value?.username || 'admin'
  showCurrentUserProfileModal.value = true
}

function handleUserUpdated(updatedUser) {
  if (currentUser.value && updatedUser) {
    if (
      !updatedUser.username ||
      currentUser.value.username.toLowerCase() === updatedUser.username.toLowerCase()
    ) {
      currentUser.value = {
        ...currentUser.value,
        ...updatedUser,
      }
    }
  }
  refreshAllData()
}

// 监听当前登录角色切换：当切换为李老师 (teacher_li) 时自动拉取待办并滑出提醒浮窗
watch(
  () => currentUser.value,
  async (newUser) => {
    if (!newUser) return
    const notifs = await fetchUserNotifications(newUser.username)
    if (newUser.username === 'teacher_li' && notifs.unread_count > 0) {
      showUrgeToast.value = true
    } else {
      showUrgeToast.value = false
    }
  },
  { deep: true }
)

const isLoggedIn = computed(() => {
  return currentUser.value && currentUser.value.username && currentUser.value.username !== 'guest'
})

const showUserMenu = ref(false)

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function closeUserMenu() {
  showUserMenu.value = false
}

// 小图标柔和色彩映射 (与注册选择身份亮起的颜色一致：STUDENT翠绿, TEACHER青蓝, ADMIN玫瑰红，柔和不刺眼)
const userIconClass = computed(() => {
  if (!isLoggedIn.value) {
    return currentTheme.value === 'light'
      ? 'bg-white/90 hover:bg-slate-100 text-slate-500 border-slate-200 shadow-slate-200/50'
      : 'bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 border-white/[0.08] hover:border-white/[0.15] shadow-black/40'
  }
  const role = currentUser.value?.role
  if (role === 'STUDENT') {
    return currentTheme.value === 'light'
      ? 'bg-emerald-50 text-emerald-700 border-emerald-300 hover:bg-emerald-100/80 shadow-emerald-100/50'
      : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20 hover:border-emerald-500/50'
  }
  if (role === 'TEACHER') {
    return currentTheme.value === 'light'
      ? 'bg-cyan-50 text-cyan-700 border-cyan-300 hover:bg-cyan-100/80 shadow-cyan-100/50'
      : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/20 hover:border-cyan-500/50'
  }
  if (role === 'ADMIN') {
    return currentTheme.value === 'light'
      ? 'bg-rose-50 text-rose-700 border-rose-300 hover:bg-rose-100/80 shadow-rose-100/50'
      : 'bg-rose-500/10 text-rose-400 border-rose-500/30 hover:bg-rose-500/20 hover:border-rose-500/50'
  }
  return currentTheme.value === 'light'
    ? 'bg-white/90 hover:bg-slate-100 text-slate-700 border-slate-200'
    : 'bg-zinc-900/90 hover:bg-zinc-800 text-zinc-300 border-white/[0.08]'
})

const userRolePingClass = computed(() => {
  const role = currentUser.value?.role
  if (role === 'STUDENT') return 'bg-emerald-400'
  if (role === 'TEACHER') return 'bg-cyan-400'
  if (role === 'ADMIN') return 'bg-rose-400'
  return 'bg-zinc-400'
})

const userRoleDotClass = computed(() => {
  const role = currentUser.value?.role
  if (role === 'STUDENT') return 'bg-emerald-500'
  if (role === 'TEACHER') return 'bg-cyan-500'
  if (role === 'ADMIN') return 'bg-rose-500'
  return 'bg-zinc-500'
})

const userIconTitle = computed(() => {
  if (isLoggedIn.value) {
    return `当前登录: ${currentUser.value.real_name} [${userRoleLabel(currentUser.value.role)}] · 点击查看操作菜单`
  }
  return '未登录访客 · 点击登录或注册'
})

function userRoleClass(role) {
  switch (role) {
    case 'ADMIN':
      return 'bg-rose-500/15 border-rose-500/30 text-rose-300'
    case 'TEACHER':
      return 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300'
    case 'STUDENT':
      return 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
    default:
      return 'bg-zinc-800 border-white/[0.08] text-zinc-400'
  }
}

function userRoleLabel(role) {
  switch (role) {
    case 'ADMIN':
      return '超级管理员'
    case 'TEACHER':
      return '专业教师'
    case 'STUDENT':
      return '在读学生'
    default:
      return role || '用户'
  }
}


// 全站深色 / 明亮双模态主题系统 (持久化同步 localStorage)
const THEME_STORAGE_KEY = 'labops_theme_mode'

function getSavedTheme() {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY)
    if (saved === 'light' || saved === 'dark') return saved
  } catch {}
  return 'dark'
}

const currentTheme = ref(getSavedTheme())

function applyTheme(theme) {
  const root = document.documentElement
  if (theme === 'light') {
    root.classList.add('light')
    root.classList.remove('dark')
  } else {
    root.classList.add('dark')
    root.classList.remove('light')
  }
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch {}
}

function toggleTheme() {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
  applyTheme(currentTheme.value)
}

// 顶层立即执行一次，避免初次渲染时闪烁
applyTheme(currentTheme.value)

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
const agentStatusText = ref('就绪')
const justCopied = ref(false)

const shortSessionId = computed(() => {
  if (!currentSessionId.value) return '新会话'
  return currentSessionId.value.replace(/^sess-/, '').slice(0, 7)
})

function copySessionId() {
  if (!currentSessionId.value) return
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(currentSessionId.value).then(() => {
      justCopied.value = true
      setTimeout(() => {
        justCopied.value = false
      }, 1500)
    }).catch(() => {})
  }
}

const chatStreamRef = ref(null)
const chatInputRef = ref(null)
let abortController = null

// 分栏宽度与拖拽状态 (28% ~ 58%，默认 42%)
const leftWidthPercent = ref(42)
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
  // 严格约束 28% 到 58% 边界，防止右侧看板被挤压变形
  leftWidthPercent.value = Math.min(Math.max(newPercent, 28), 58)
}

function onTouchDragging(e) {
  if (!isDragging.value || !e.touches || e.touches.length === 0) return
  e.preventDefault()
  const touch = e.touches[0]
  const totalWidth = window.innerWidth
  const newPercent = (touch.clientX / totalWidth) * 100
  leftWidthPercent.value = Math.min(Math.max(newPercent, 28), 58)
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
  leftWidthPercent.value = 42
}

// 右侧分段 Tab 控制
const currentTab = ref('overview')

function handleSwitchTab(tabName) {
  currentTab.value = tabName
}

function handleQuickAction(prompt) {
  handleSendMessage(prompt)
}

function handleFillInput(prompt) {
  chatInputRef.value?.setInput(prompt)
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
// 设备健康率计算属性：优先根据在册资产状态实时动态计算，兜底采用全局指标
const healthRate = computed(() => {
  if (assets.value && assets.value.length > 0) {
    const healthy = assets.value.filter((a) => a.health_status === 'HEALTHY').length
    return Math.round((healthy / assets.value.length) * 100)
  }
  return overview.value.system_health_rate ?? 100
})
// 统计未成功归档的所有在办/待办工单数 (不含 CLOSED 已归档工单)
const pendingTicketCount = computed(() => tickets.value.filter((t) => t.status !== 'CLOSED').length)

// 联动高亮状态
const highlightedTicketNo = ref('')
const highlightedAssetNo = ref('')
let ticketHighlightTimer = null
let assetHighlightTimer = null

// 历史会话抽屉状态
const showSessionDrawer = ref(false)
const sessionList = ref([])

// 全局后台被动静默自适应轮询探针 (每 8 秒自动拉取指标与工单，支持休眠避让、流式避让与并发防重叠互斥锁)
let silentPollingTimer = null
let isPollingActive = true
let isSilentPollingRunning = false

function handleVisibilityChange() {
  if (document.hidden) {
    isPollingActive = false
  } else {
    isPollingActive = true
    // 重新切回前台时，立即静默拉取一次最新动环与工单数据
    refreshAllData()
  }
}

function startSilentPolling() {
  if (silentPollingTimer) clearInterval(silentPollingTimer)
  silentPollingTimer = setInterval(async () => {
    // 互斥防护：慢网络或高延迟下若上一轮请求未结束，直接跳过本次触发，严防并发堆叠
    if (isPollingActive && !document.hidden && !isStreaming.value && !isSilentPollingRunning) {
      isSilentPollingRunning = true
      try {
        await refreshAllData()
      } catch (err) {
        console.error('静默轮询同步数据异常:', err)
      } finally {
        isSilentPollingRunning = false
      }
    }
  }, 8000)
}

function stopSilentPolling() {
  if (silentPollingTimer) {
    clearInterval(silentPollingTimer)
    silentPollingTimer = null
  }
}

onMounted(async () => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  window.addEventListener('click', closeUserMenu)
  document.addEventListener('visibilitychange', handleVisibilityChange)
  initAudioContextUnlock()
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    updateVoicesList()
    window.speechSynthesis.onvoiceschanged = () => {
      updateVoicesList()
      // 语音列表注入更新后，静默预热一次云端链路
      warmupTtsConnection()
    }
  }
  startNewSession()
  await refreshAllData()
  startSilentPolling()
  // 方案 2: 页面加载完成后轻微延迟静默预热 Edge/Azure 云端语音链路，彻底消除首次告警冷启动耗时
  setTimeout(() => {
    warmupTtsConnection()
  }, 1200)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  window.removeEventListener('click', closeUserMenu)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  stopSilentPolling()
  removeAudioContextUnlock()
  stopDragging()
  if (ticketHighlightTimer) clearTimeout(ticketHighlightTimer)
  if (assetHighlightTimer) clearTimeout(assetHighlightTimer)
  clearWatchdogTimer()
  clearWarmupTimer()
  if (fallbackDispatchTimer) clearTimeout(fallbackDispatchTimer)
  if (audioCtx && audioCtx.close) {
    audioCtx.close().catch(() => {})
    audioCtx = null
  }
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = null
    try {
      window.speechSynthesis.cancel()
      clearAllUtterances()
    } catch {}
  }
})

function startNewSession() {
  if (isStreaming.value) {
    handleAbortStream()
  }
  currentSessionId.value = `sess-${Date.now().toString(36)}`
  currentTraceId.value = ''
  messages.value = []
  agentStatusText.value = '就绪'
  chatInputRef.value?.clear()
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
  if (isStreaming.value) {
    handleAbortStream()
  }
  currentSessionId.value = sessionId
  currentTraceId.value = ''
  agentStatusText.value = '就绪'
  showSessionDrawer.value = false
  chatInputRef.value?.clear()
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

// 规章规程知识中心在册数量与 AI 提问联动
const regulationsCount = ref(3)

function handleAskAIAboutRegulation(prompt) {
  if (prompt) {
    handleSendMessage(prompt)
  }
}

async function loadRegulationsSummary() {
  try {
    const summary = await api.getRegulationsSummary()
    if (summary && typeof summary.total_documents === 'number') {
      regulationsCount.value = summary.total_documents
    }
  } catch (err) {
    console.error('加载规程概览失败:', err)
  }
}

async function refreshAllData() {
  await Promise.allSettled([
    loadMetrics(),
    loadTickets(),
    loadAssets(),
    loadRegulationsSummary(),
    fetchUserNotifications(currentUser.value?.username),
  ])
  rackTopologyRef.value?.loadTopology?.()
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

async function handleRefreshTickets() {
  await Promise.all([loadTickets(), loadMetrics(), loadAssets()])
  if (rackTopologyRef.value?.loadTopology) {
    try {
      await rackTopologyRef.value.loadTopology()
    } catch (e) {}
  }
}

async function loadOverdueAssets() {
  try {
    const res = await api.getOverdueAssets()
    if (res && res.status === 'success') {
      overdueAssets.value = res.items || res.assets || []
    }
  } catch (err) {
    console.error('加载借用超期设备概要失败:', err)
  }
}

async function loadAssets() {
  try {
    const [list] = await Promise.all([
      api.listAssets({ limit: 500 }),
      loadOverdueAssets(),
    ])
    assets.value = list
  } catch (err) {
    console.error('加载资产台账失败:', err)
  }
}

async function handleRefreshAssets() {
  await Promise.allSettled([loadAssets(), loadMetrics(), loadOverdueAssets()])
}

// -------------------------------------------------------------
// 高危告警原生语音 TTS 播报与四级容灾优化核心
// -------------------------------------------------------------
const ttsEnabled = ref(false)
const activeUtterances = new Set()
let activeWatchdogTimer = null
let warmupSafetyTimer = null
let fallbackDispatchTimer = null
let isWarmingUp = false
let audioCtx = null
let unlockAudioListenersAdded = false
const cachedVoices = ref([])

function clearWatchdogTimer() {
  if (activeWatchdogTimer) {
    clearTimeout(activeWatchdogTimer)
    activeWatchdogTimer = null
  }
}

function clearWarmupTimer() {
  if (warmupSafetyTimer) {
    clearTimeout(warmupSafetyTimer)
    warmupSafetyTimer = null
  }
}

function trackUtterance(u) {
  if (u) activeUtterances.add(u)
}

function untrackUtterance(u) {
  if (u) activeUtterances.delete(u)
}

function clearAllUtterances() {
  activeUtterances.clear()
}

// -------------------------------------------------------------
// 方案 1: 0毫秒声学先导音 (纯原生 Web Audio API，消除首包死寂感)
// -------------------------------------------------------------
function initAudioContextUnlock() {
  if (typeof window === 'undefined' || unlockAudioListenersAdded) return
  unlockAudioListenersAdded = true
  const unlock = () => {
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume().catch(() => {})
    }
  }
  window.addEventListener('click', unlock, { passive: true })
  window.addEventListener('keydown', unlock, { passive: true })
  window.addEventListener('touchstart', unlock, { passive: true })
}

function removeAudioContextUnlock() {
  if (typeof window === 'undefined' || !unlockAudioListenersAdded) return
  unlockAudioListenersAdded = false
}

function getAudioContext() {
  if (typeof window === 'undefined') return null
  if (!audioCtx) {
    const AudioCtxClass = window.AudioContext || window.webkitAudioContext
    if (AudioCtxClass) {
      audioCtx = new AudioCtxClass()
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {})
  }
  return audioCtx
}

function playAlertChime() {
  try {
    const ctx = getAudioContext()
    if (!ctx) return
    const now = ctx.currentTime

    // 主音振荡器：880Hz (A5) 柔和爬升至 1320Hz (E6)，具备清晰警示与科技质感
    const osc1 = ctx.createOscillator()
    const gain1 = ctx.createGain()
    osc1.type = 'sine'
    osc1.frequency.setValueAtTime(880, now)
    osc1.frequency.exponentialRampToValueAtTime(1320, now + 0.12)

    // 主音量包络：15ms 平滑起振消除扬声器阶跃爆破音，辅以 0.35s 柔和指数衰减
    gain1.gain.setValueAtTime(0.0001, now)
    gain1.gain.linearRampToValueAtTime(0.18, now + 0.015)
    gain1.gain.exponentialRampToValueAtTime(0.0001, now + 0.35)

    osc1.connect(gain1)
    gain1.connect(ctx.destination)
    osc1.start(now)
    osc1.stop(now + 0.36)

    // 泛音谐波点缀 (1760Hz)：增强空间先导清脆感与数字机房立体态势感
    const osc2 = ctx.createOscillator()
    const gain2 = ctx.createGain()
    osc2.type = 'sine'
    osc2.frequency.setValueAtTime(1760, now)
    gain2.gain.setValueAtTime(0.0001, now)
    gain2.gain.linearRampToValueAtTime(0.06, now + 0.015)
    gain2.gain.exponentialRampToValueAtTime(0.0001, now + 0.22)

    osc2.connect(gain2)
    gain2.connect(ctx.destination)
    osc2.start(now)
    osc2.stop(now + 0.23)
  } catch (err) {
    console.warn('[LabOps Audio] 告警先导和弦音播放微异常:', err)
  }
}

// 初始化与更新语音列表 (兼容 Edge / Chromium 异步注入云端神经音色)
function updateVoicesList() {
  if (typeof window === 'undefined' || !window.speechSynthesis) return
  const voices = window.speechSynthesis.getVoices() || []
  if (voices.length > 0) {
    cachedVoices.value = voices
  }
}

// -------------------------------------------------------------
// 方案 4 发音人调度模型：主用云端晓晓，容灾本地瑶瑶
// -------------------------------------------------------------
function isChineseVoice(v) {
  if (!v) return false
  const lang = (v.lang || '').toLowerCase()
  return lang.includes('zh') || lang.includes('cn') || lang.includes('cmn')
}

function isLocalVoice(v) {
  if (!v) return false
  if (v.localService === true) return true
  const nameLower = (v.name || '').toLowerCase()
  if (nameLower.includes('online') || nameLower.includes('natural')) return false
  return true
}

function getAllAvailableVoices() {
  if (typeof window === 'undefined' || !window.speechSynthesis) return []
  const live = window.speechSynthesis.getVoices() || []
  if (live.length > 0) {
    cachedVoices.value = live
    return live
  }
  return cachedVoices.value || []
}

// 1. 获取主用发音人：首选微软晓晓云端自然音 (Xiaoxiao Online Natural)
function getPrimaryCloudVoice() {
  const voices = getAllAvailableVoices()
  if (!voices || voices.length === 0) return null

  // 首选：微软晓晓在线自然音 (Xiaoxiao Online Natural)
  const xiaoxiao = voices.find(
    (v) =>
      (v.name.toLowerCase().includes('xiaoxiao') || v.name.includes('晓晓')) &&
      isChineseVoice(v)
  )
  if (xiaoxiao) return xiaoxiao

  // 次选：包含 Natural 或 Online 的微软优质中文发音人 (如 Yunxi, Xiaoyi 等)
  const naturalChinese = voices.find(
    (v) =>
      (v.name.toLowerCase().includes('natural') || v.name.toLowerCase().includes('online')) &&
      isChineseVoice(v)
  )
  if (naturalChinese) return naturalChinese

  return null
}

// 2. 获取本地容灾发音人：严格首选系统本地微软瑶瑶 (Microsoft Yaoyao，非云端 Online 发音人)
function getFallbackLocalVoice() {
  const voices = getAllAvailableVoices()
  if (!voices || voices.length === 0) return null

  // 首选本地容灾：系统本地微软瑶瑶 (Microsoft Yaoyao，排除包含 Online/Natural 的云端版本)
  const yaoyao = voices.find(
    (v) =>
      (v.name.toLowerCase().includes('yaoyao') || v.name.includes('瑶瑶')) &&
      isChineseVoice(v) &&
      isLocalVoice(v)
  )
  if (yaoyao) return yaoyao

  // 次选本地容灾：标有 localService 或离线的微软慧慧/康康
  const huihuiOrKangkang = voices.find(
    (v) =>
      isChineseVoice(v) &&
      isLocalVoice(v) &&
      (v.name.toLowerCase().includes('huihui') ||
        v.name.includes('慧慧') ||
        v.name.toLowerCase().includes('kangkang') ||
        v.name.includes('康康'))
  )
  if (huihuiOrKangkang) return huihuiOrKangkang

  // 再次选：标有 localService 的本地中文发音人
  const localServiceChinese = voices.find((v) => isChineseVoice(v) && v.localService === true)
  if (localServiceChinese) return localServiceChinese

  // 四选：非 Online/Natural 的离线中文发音人
  const offlineChinese = voices.find((v) => isChineseVoice(v) && isLocalVoice(v))
  if (offlineChinese) return offlineChinese

  // 终极兜底：任意可用中文发音人
  const generalChinese = voices.find((v) => isChineseVoice(v))
  if (generalChinese) return generalChinese

  return null
}

// -------------------------------------------------------------
// 方案 2: 静默链路预热 (消除 Edge/Azure 云端首包冷启动延迟)
// -------------------------------------------------------------
function warmupTtsConnection() {
  if (typeof window === 'undefined' || !window.speechSynthesis) return
  if (isWarmingUp) return
  if (typeof navigator !== 'undefined' && navigator.onLine === false) return

  try {
    isWarmingUp = true
    clearWarmupTimer()

    // 采用具发音音节的极短微词（避免纯标点符号导致 Chromium 引擎挂起或 speaking: true 假死锁）
    const warmupUtterance = new SpeechSynthesisUtterance('点')
    warmupUtterance.lang = 'zh-CN'
    warmupUtterance.volume = 0.01 // 极低微音，静默无感
    warmupUtterance.rate = 2.0   // 极速跑完

    const primaryVoice = getPrimaryCloudVoice()
    if (primaryVoice) {
      warmupUtterance.voice = primaryVoice
    }

    trackUtterance(warmupUtterance)

    const finishWarmup = () => {
      clearWarmupTimer()
      isWarmingUp = false
      untrackUtterance(warmupUtterance)
    }

    warmupUtterance.onend = finishWarmup
    warmupUtterance.onerror = finishWarmup

    // 预热防挂死安全看门狗：最长 1000ms 强制重置预热锁，确保后续正式播报永不阻塞
    warmupSafetyTimer = setTimeout(() => {
      if (isWarmingUp) {
        finishWarmup()
      }
    }, 1000)

    window.speechSynthesis.speak(warmupUtterance)
  } catch (e) {
    isWarmingUp = false
    clearWarmupTimer()
  }
}

// -------------------------------------------------------------
// 方案 4: 容灾兜底播放执行器 (本地微软瑶瑶无感降级)
// -------------------------------------------------------------
function executeFallbackSpeech(text, reason) {
  clearWatchdogTimer()
  if (fallbackDispatchTimer) {
    clearTimeout(fallbackDispatchTimer)
    fallbackDispatchTimer = null
  }

  const fallbackVoice = getFallbackLocalVoice()
  console.warn(`[LabOps TTS 容灾] ${reason}，已无感切换本地发音人: ${fallbackVoice?.name || '本地默认'}`)

  try {
    // 强制截断正在等待或超时的前序语音
    window.speechSynthesis.cancel()

    // Chromium 容灾竞态防御：cancel() 与 speak() 同步连续调用在 Chromium 会导致新语音被一并截断
    // 引入 40ms 微延时让底层语音合成队列 IPC 彻底重置，确保本地瑶瑶稳固发声
    fallbackDispatchTimer = setTimeout(() => {
      fallbackDispatchTimer = null
      if (!ttsEnabled.value) return

      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume()
      }

      const fallbackUtterance = new SpeechSynthesisUtterance(text)
      fallbackUtterance.lang = 'zh-CN'
      if (fallbackVoice) {
        fallbackUtterance.voice = fallbackVoice
      }
      fallbackUtterance.rate = 1.05
      fallbackUtterance.pitch = 1.0

      trackUtterance(fallbackUtterance)

      fallbackUtterance.onend = () => {
        untrackUtterance(fallbackUtterance)
      }
      fallbackUtterance.onerror = (e) => {
        if (e.error !== 'canceled' && e.error !== 'interrupted') {
          console.warn('[LabOps TTS] 本地容灾发音人播报事件:', e)
        }
        untrackUtterance(fallbackUtterance)
      }

      window.speechSynthesis.speak(fallbackUtterance)
    }, 40)
  } catch (err) {
    console.warn('[LabOps TTS] 本地容灾发音人启动失败:', err)
  }
}

// -------------------------------------------------------------
// 语音告警核心调度：云端晓晓为主，无感容灾兜底为辅
// -------------------------------------------------------------
function speakAlert(text) {
  if (typeof window === 'undefined' || !window.speechSynthesis || !text) return

  try {
    clearWatchdogTimer()
    if (fallbackDispatchTimer) {
      clearTimeout(fallbackDispatchTimer)
      fallbackDispatchTimer = null
    }

    const isOffline = typeof navigator !== 'undefined' && navigator.onLine === false
    const primaryVoice = !isOffline ? getPrimaryCloudVoice() : null

    // 容灾分支 1：检测到离线脱网，或未检测到云端高保真音色，直接走本地瑶瑶无感播报
    if (isOffline || !primaryVoice) {
      const reason = isOffline ? '网络处于离线断网状态(!navigator.onLine)' : '未检测到云端晓晓音色'
      executeFallbackSpeech(text, reason)
      return
    }

    // 主用分支：在线且具备微软晓晓云端自然音
    const isBusy = window.speechSynthesis.speaking || window.speechSynthesis.pending
    if (isBusy) {
      window.speechSynthesis.cancel()
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-CN'
    utterance.voice = primaryVoice
    utterance.rate = 1.05
    utterance.pitch = 1.0
    console.info(`[LabOps TTS] 已激活主用云端发音人: ${primaryVoice.name}`)

    trackUtterance(utterance)

    let hasStarted = false
    let hasFallbackRun = false

    // 容灾分支 2：5000ms 超时看门狗，给云端充足的网络建立与音频流缓冲时间，超时方才无感切本地瑶瑶
    activeWatchdogTimer = setTimeout(() => {
      if (!hasStarted && !hasFallbackRun) {
        hasFallbackRun = true
        console.warn('[LabOps TTS 容灾] 云端合成网络耗时超出 5000ms，触发本地瑶瑶容灾兜底')
        executeFallbackSpeech(text, '云端合成响应超时 (5000ms 未出声)')
      }
    }, 5000)

    utterance.onstart = () => {
      hasStarted = true
      clearWatchdogTimer()
      console.info(`[LabOps TTS 成功发声] 微软晓晓已成功开始播报语音`)
    }

    utterance.onend = () => {
      clearWatchdogTimer()
      untrackUtterance(utterance)
    }

    // 容灾分支 3：云端合成报错（网络中断、认证失败等），无感切本地瑶瑶
    utterance.onerror = (e) => {
      clearWatchdogTimer()
      untrackUtterance(utterance)
      if (e.error === 'canceled' || e.error === 'interrupted' || hasFallbackRun) {
        return
      }
      if (!hasStarted) {
        hasFallbackRun = true
        console.warn(`[LabOps TTS 容灾] 云端播报触发异常事件: ${e.error || 'unknown'}`)
        executeFallbackSpeech(text, `云端合成异常 (${e.error || 'unknown'})`)
      }
    }

    // 安全调度：若此前调用了 cancel() 截断旧播报，引入 40ms 微延时让 IPC 重置；若本来空闲则即刻发声
    if (isBusy) {
      setTimeout(() => {
        if (!ttsEnabled.value) return
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume()
        }
        window.speechSynthesis.speak(utterance)
      }, 40)
    } else {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume()
      }
      window.speechSynthesis.speak(utterance)
    }
  } catch (err) {
    console.warn('TTS 语音播报异常:', err)
  }
}

// 监听 TTS 开关：一旦用户主动开启，静默预热并激活声学引擎；一旦静音，清空定时器并强制截断
watch(ttsEnabled, (newVal) => {
  if (newVal) {
    getAudioContext()
    warmupTtsConnection()
  } else if (typeof window !== 'undefined' && window.speechSynthesis) {
    try {
      clearWatchdogTimer()
      clearWarmupTimer()
      if (fallbackDispatchTimer) {
        clearTimeout(fallbackDispatchTimer)
        fallbackDispatchTimer = null
      }
      isWarmingUp = false
      window.speechSynthesis.cancel()
      clearAllUtterances()
    } catch {}
  }
})

function buildTtsAlertText(report) {
  if (!report) return ''
  const abnormals = report.abnormal_devices || []
  const criticals = abnormals.filter(
    (d) =>
      d.is_overheat ||
      d.is_offline ||
      d.health_status === 'OVERHEAT' ||
      d.health_status === 'OFFLINE' ||
      (report.created_tickets && report.created_tickets.some((t) => t.device_id === d.asset_no))
  )

  if (criticals.length === 0) {
    // 若 abnormal_devices 为空但包含紧急新建工单时的安全兜底
    if (report.created_tickets && report.created_tickets.length > 0) {
      return `警告：全网自治体检已触发 ${report.created_tickets.length} 项紧急运维工单，请立即响应。`
    }
    return ''
  }

  if (criticals.length === 1) {
    const d = criticals[0]
    const devName = d.name || d.asset_no || '核心设备'
    const isOverheat = d.is_overheat || d.health_status === 'OVERHEAT'
    const isOffline = d.is_offline || d.health_status === 'OFFLINE'
    if (isOverheat) {
      const tempText = (d.temperature !== undefined && d.temperature !== null) ? `${d.temperature}度` : '超过警戒阈值'
      return `警告：检测到${devName}核心温度达到${tempText}，已自动触发紧急工单，请立即响应。`
    } else if (isOffline) {
      return `警告：检测到${devName}处于脱网掉线状态，已自动触发运维工单，请立即核查网络连通性。`
    } else {
      return `警告：检测到${devName}处于高危异常状态，已自动触发紧急工单，请立即响应。`
    }
  }

  // 多台设备高危异常
  const descriptions = criticals.slice(0, 2).map((d) => {
    const devName = d.name || d.asset_no || '核心设备'
    const isOverheat = d.is_overheat || d.health_status === 'OVERHEAT'
    const isOffline = d.is_offline || d.health_status === 'OFFLINE'
    if (isOverheat) {
      const tempText = (d.temperature !== undefined && d.temperature !== null) ? `核心温度达到${d.temperature}度` : '核心温度超标'
      return `${devName}${tempText}`
    } else if (isOffline) {
      return `${devName}掉线失联`
    }
    return `${devName}状态异常`
  })

  const remaining = criticals.length > 2 ? `等共${criticals.length}台设备` : ''
  return `警告：检测到${descriptions.join('，')}${remaining}存在高危异常，已自动触发紧急工单，请立即响应。`
}

function triggerTtsAlert(report) {
  if (!ttsEnabled.value) return
  const alertText = buildTtsAlertText(report)
  if (alertText) {
    // 方案 1: 第 0 毫秒立即发出科技感声学先导和弦音，彻底消灭等待死寂感
    playAlertChime()
    // 方案 4: 告警自然语音播报（主用云端晓晓，结合断网离线与超时无感降级本地瑶瑶）
    speakAlert(alertText)
  }
}

// -------------------------------------------------------------
// 全机房主动自治体检联动处理
// -------------------------------------------------------------
function handlePatrolCompleted(report) {
  patrolReportData.value = report || {}
  showPatrolModal.value = true

  // 方案 3 (网络与调度避让): 语音播报提升至第一优先级发出，彻底规避同毫秒网络与主线程拥塞
  if (ttsEnabled.value && report) {
    triggerTtsAlert(report)
  }

  // 将包含 5 个接口高负载并发的 refreshAllData() 推迟 80ms 执行
  setTimeout(() => {
    refreshAllData()
  }, 80)

  // 在左侧 AI 对话流中同步追加系统自治体检研判播报
  messages.value.push({
    id: `ast-${Date.now()}`,
    role: 'assistant',
    content: report.markdown_report || `【全机房主动自治巡检完成】综合健康得分：${report.health_score} 分（${report.posture_text}）\n${report.summary_text}`,
    thought: `【全网自治巡检完成】\n巡检批次：${report.batch_no || '实时'}\n总计扫描设备 ${report.kpi?.total_scanned || 0} 台，检出异常 ${report.abnormal_devices?.length || 0} 台，自动工单闭环已触发。`,
    isThinking: false,
    isStreaming: false,
    toolCalls: [
      {
        name: 'run_autonomous_patrol',
        args: { operator: report.operator || '全网自治巡检' },
        result: { status: 'success', report },
      },
    ],
    citations: (report.cited_regulations || []).map((r) => ({
      source: r.doc_name,
      section: r.clause,
      content: r.content,
    })),
    created_at: new Date().toISOString(),
  })
}

function handleInspectTicketFromReport(ticketNo) {
  showPatrolModal.value = false
  currentTab.value = 'tickets'
  triggerTicketHighlight(ticketNo)
}

// -------------------------------------------------------------
// SSE 对话交互与事件分发核心
// -------------------------------------------------------------
async function handleSendMessage(promptText) {
  if (isStreaming.value || !promptText.trim()) return
  chatInputRef.value?.clear()

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
  agentStatusText.value = '思考分析中...'

  abortController = new AbortController()

  await fetchSSE({
    prompt: promptText,
    sessionId: currentSessionId.value,
    user: currentUser.value,
    signal: abortController.signal,
    onEvent: (event) => {
      handleIncomingSSEEvent(event, assistantMsg)
    },
    onError: (err) => {
      assistantMsg.content += `\n【网络异常或服务错误】: ${err.message}`
      assistantMsg.isThinking = false
      assistantMsg.isStreaming = false
      agentStatusText.value = '就绪'
    },
    onFinish: async () => {
      assistantMsg.isThinking = false
      assistantMsg.isStreaming = false
      isStreaming.value = false
      agentStatusText.value = '就绪'
      // 对话流结束时无条件静默兜底同步最新台账与指标，防止智能体在后台修改数据后前端视图未刷新
      await Promise.allSettled([loadAssets(), loadTickets(), loadMetrics()])
      if (rackTopologyRef.value?.loadTopology) {
        rackTopologyRef.value.loadTopology().catch(() => {})
      }
    },
  })
}

function handleIncomingSSEEvent(event, assistantMsg) {
  const { type } = event

  if (type === 'think') {
    assistantMsg.thought = (assistantMsg.thought ? assistantMsg.thought + '\n' : '') + (event.thought || '')
    assistantMsg.step = event.step || assistantMsg.step
    assistantMsg.isThinking = true
    agentStatusText.value = '深度思考研判中...'
  } else if (type === 'tool_start') {
    assistantMsg.isThinking = false
    agentStatusText.value = '调用运维工具中...'
    assistantMsg.toolCalls.push({
      tool_call_id: event.tool_call_id,
      name: event.name,
      args: event.args,
      step: event.step,
      result: null,
    })
  } else if (type === 'tool_end') {
    agentStatusText.value = '分析处置结果中...'
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
    // 左右业务联动：工单突变，刷新看板。若巡检弹窗正在显示，不抢焦切Tab，留给用户在简报中点击直达
    if (!showPatrolModal.value) {
      currentTab.value = 'tickets'
      triggerTicketHighlight(event.ticket_no)
    }
    loadTickets()
    loadMetrics()
  } else if (type === 'asset_mutation') {
    // 左右业务联动：资产突变，自动切换至资产Tab，刷新台账与指标并触发高亮动画！
    currentTab.value = 'assets'
    triggerAssetHighlight(event.asset_no)
    loadAssets()
    loadMetrics()
    rackTopologyRef.value?.loadTopology?.()
  } else if (type === 'patrol_completed') {
    // 全网自治巡检完成事件：同步挂载简报数据并弹出微光简报模态框
    patrolReportData.value = event.report || {}
    showPatrolModal.value = true
    // 方案 3 (网络与调度避让): 语音播报提升至第一优先级发出，彻底规避同毫秒网络与主线程拥塞
    if (ttsEnabled.value && event.report) {
      triggerTtsAlert(event.report)
    }
    setTimeout(() => {
      loadMetrics()
      loadTickets()
      loadAssets()
    }, 80)
  } else if (type === 'content') {
    assistantMsg.isThinking = false
    agentStatusText.value = '生成答复中...'
    assistantMsg.content = event.text || assistantMsg.content
  } else if (type === 'error') {
    assistantMsg.isThinking = false
    assistantMsg.isStreaming = false
    agentStatusText.value = '就绪'
    assistantMsg.content += (assistantMsg.content ? '\n\n' : '') + `【系统错误】: ${event.message || '内部处理发生异常'}`
  } else if (type === 'done') {
    currentSessionId.value = event.session_id || currentSessionId.value
    currentTraceId.value = event.trace_id || ''
    assistantMsg.isThinking = false
    assistantMsg.isStreaming = false
    agentStatusText.value = '就绪'
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
    agentStatusText.value = '就绪'
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

// -------------------------------------------------------------
// 机架拓扑相关状态与全景台账弹窗联动事件
// -------------------------------------------------------------
const rackTopologyRef = ref(null)

const rackedAssetsCount = computed(() => {
  if (!assets.value || assets.value.length === 0) return 0
  return assets.value.filter(
    (a) => a.location && (a.location.includes('机柜') || a.location.includes('核心柜'))
  ).length
})

const totalRacksCount = computed(() => {
  return rackTopologyRef.value?.topologyData?.summary?.total_racks ?? 2
})

const showTopologyDeviceModal = ref(false)
const selectedTopologyAsset = ref(null)

const showTopologyDeleteModal = ref(false)
const targetAssetForTopologyDelete = ref(null)
const isDeletingTopologyAsset = ref(false)
const deleteTopologyError = ref('')

function handleInspectAssetFromTopology(asset) {
  const matched = assets.value.find((a) => a.asset_no === asset.asset_no)
  selectedTopologyAsset.value = matched || asset
  showTopologyDeviceModal.value = true
}

function handleDeleteAssetFromTopology(asset) {
  if (currentUser.value?.role !== 'ADMIN') return
  targetAssetForTopologyDelete.value = asset
  deleteTopologyError.value = ''
  showTopologyDeleteModal.value = true
}

async function confirmDeleteTopologyAsset() {
  if (!targetAssetForTopologyDelete.value || currentUser.value?.role !== 'ADMIN') return
  isDeletingTopologyAsset.value = true
  deleteTopologyError.value = ''
  try {
    await api.deleteAsset(targetAssetForTopologyDelete.value.id)
    showTopologyDeleteModal.value = false
    showTopologyDeviceModal.value = false
    targetAssetForTopologyDelete.value = null
    await refreshAllData()
  } catch (err) {
    deleteTopologyError.value = err.message || '删除设备失败'
  } finally {
    isDeletingTopologyAsset.value = false
  }
}

function handleBorrowAssetFromTopology(assetOrNo) {
  showTopologyDeviceModal.value = false
  const no = typeof assetOrNo === 'object' && assetOrNo !== null ? assetOrNo.asset_no : assetOrNo
  handleBorrowAsset(no, currentUser.value.real_name)
}

function handleReturnAssetFromTopology(assetOrNo) {
  showTopologyDeviceModal.value = false
  const no = typeof assetOrNo === 'object' && assetOrNo !== null ? assetOrNo.asset_no : assetOrNo
  handleReturnAsset(no)
}

function handleEditAssetFromTopology(asset) {
  showTopologyDeviceModal.value = false
  currentTab.value = 'assets'
  triggerAssetHighlight(asset?.asset_no)
}

function handleInspectTicket(ticketNo) {
  handleSendMessage(`查询工单 ${ticketNo} 的详细处置进展与排查说明`)
}

async function handleUpdateTicketStatus(ticketId, newStatus, extra = null) {
  try {
    const payload = {
      status: newStatus,
      operator: currentUser.value?.real_name || currentUser.value?.username || '管理员',
      ...(extra && typeof extra === 'object' ? extra : {}),
    }
    await api.updateTicket(ticketId, payload)
    await Promise.all([loadTickets(), loadMetrics(), loadAssets()])
    if (rackTopologyRef.value?.loadTopology) {
      try {
        await rackTopologyRef.value.loadTopology()
      } catch (e) {}
    }
  } catch (err) {
    console.error('工单状态更新失败:', err)
  }
}

async function handleBorrowAsset(assetNo, borrower) {
  try {
    const target = assets.value.find((a) => a.asset_no === assetNo)
    if (target) {
      target.borrow_status = 'IN_USE'
      target.borrower = borrower
    }
    await api.borrowAsset(assetNo, { borrower })
    triggerAssetHighlight(assetNo)
    await Promise.allSettled([loadAssets(), loadMetrics()])
    if (rackTopologyRef.value?.loadTopology) {
      rackTopologyRef.value.loadTopology().catch(() => {})
    }
  } catch (err) {
    console.error('借用设备失败:', err)
    handleSendMessage(`帮 ${borrower} 办理设备 ${assetNo} 的借用登记`)
  }
}

async function handleReturnAsset(assetNo) {
  try {
    // 1. 本地即时响应式乐观更新：立刻将设备状态恢复为 AVAILABLE，借用人清空！
    // 彻底杜绝界面图标不更新、按钮仍为“归还”、以及再次点击触发状态冲突
    const target = assets.value.find((a) => a.asset_no === assetNo)
    if (target) {
      target.borrow_status = 'AVAILABLE'
      target.borrower = null
    }
    await api.returnAsset(assetNo)
    triggerAssetHighlight(assetNo)
    await Promise.allSettled([
      loadAssets(),
      loadMetrics(),
      fetchUserNotifications(currentUser.value?.username),
    ])
    if (rackTopologyRef.value?.loadTopology) {
      rackTopologyRef.value.loadTopology().catch(() => {})
    }
  } catch (err) {
    console.error('归还设备失败:', err)
    handleSendMessage(`办理设备 ${assetNo} 的归还登记`)
  }
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
    console.error('更新资产健康状态失败:', err)
  }
}
</script>
