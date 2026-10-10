<template>
  <div class="space-y-4 relative">
    <!-- 拖拽调拨轻量反馈 Toast -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-3 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 -translate-y-3 scale-95"
    >
      <div
        v-if="toastMessage"
        class="fixed top-5 left-1/2 -translate-x-1/2 z-[200] px-4 py-2.5 rounded-2xl shadow-2xl border flex items-center space-x-2 text-xs font-medium backdrop-blur-2xl"
        :class="toastType === 'error'
          ? (isLight ? 'bg-rose-50/95 border-rose-300 text-rose-800 shadow-rose-200/50' : 'bg-rose-950/95 border-rose-500/50 text-rose-200 shadow-rose-950/60')
          : (isLight ? 'bg-emerald-50/95 border-emerald-300 text-emerald-800 shadow-emerald-200/50' : 'bg-zinc-900/95 border-emerald-500/50 text-emerald-300 ring-1 ring-emerald-500/30 shadow-emerald-950/50')"
      >
        <span class="text-sm">{{ toastType === 'error' ? '⚠️' : '✅' }}</span>
        <span>{{ toastMessage }}</span>
      </div>
    </Transition>

    <!-- 正在拖拽调度提示指示器 -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div
        v-if="isDragging"
        class="p-2.5 rounded-xl border flex items-center justify-between text-xs animate-pulse select-none"
        :class="isLight ? 'bg-cyan-50/90 border-cyan-200 text-cyan-800' : 'bg-cyan-950/40 border-cyan-500/30 text-cyan-300'"
      >
        <div class="flex items-center space-x-2">
          <span class="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
          <span><strong>数字孪生拖拽调度中:</strong> 正在移动设备 <code class="font-mono font-bold">{{ draggedAsset?.asset_no }}</code> (占用 {{ draggedHeight }}U 空间)</span>
        </div>
        <span class="text-[11px] opacity-80">拖拽至目标机柜空闲槽位释放即可自动完成上架调拨</span>
      </div>
    </Transition>

    <!-- 1. 顶部控制栏：机房下拉切换器与实时同步控制 (显式声明 relative z-30，确保下拉浮层不被下方卡片遮挡) -->
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-2xl glass-card border relative z-30"
      :class="isLight ? 'border-slate-200 shadow-sm' : ''"
    >
      <div class="flex items-center space-x-3">
        <div class="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
          <!-- 机架拓扑 SVG 图标 -->
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
          </svg>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h3 class="text-sm font-semibold glass-text" :class="isLight ? 'text-slate-900' : 'text-zinc-100'">机房机柜 2D 机位拓扑视图</h3>
            <span class="flex h-2 w-2 relative">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
            </span>

            <!-- 新位置刷新按钮：暗淡低调、不抢眼，需要时才注意到 -->
            <button
              @click="loadTopology"
              :disabled="loading"
              class="p-1 rounded-md transition-all text-zinc-500/70 hover:text-zinc-300 hover:bg-zinc-800/40 disabled:opacity-30 ml-1"
              :class="isLight ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-200/50' : ''"
              title="刷新机柜拓扑数据"
            >
              <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          <!-- 仅在“全部机房”全局视图下呈现概览小字；切换至具体子机房时隐藏，避免与下方机房元信息说明条重叠 -->
          <p v-if="selectedRoomCode === 'ALL'" class="text-xs mt-0.5" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">
            实训大楼全部机房 · 42U 标准工业级机架槽位与配套设施
          </p>
        </div>
      </div>

      <!-- 右侧控制区：机房下拉切换器 + 新建机房 (彻底消除按钮堆叠) -->
      <div class="flex items-center space-x-2 relative self-start sm:self-auto">
        <!-- 机房空间下拉选择器 (提升层级至绝对置顶) -->
        <div class="relative z-40 room-dropdown-container">
          <button
            @click.stop="roomDropdownOpen = !roomDropdownOpen"
            type="button"
            class="px-3 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-sm flex items-center space-x-2 active:scale-95 select-none"
            :class="[
              isLight
                ? 'bg-slate-100 hover:bg-slate-200/80 border-slate-200 text-slate-800'
                : 'bg-zinc-900/90 hover:bg-zinc-800 border-white/[0.08] text-zinc-200',
              roomDropdownOpen ? (isLight ? 'ring-2 ring-emerald-500/20 border-emerald-400' : 'ring-2 ring-emerald-500/20 border-emerald-500/40') : ''
            ]"
            title="点击切换查看的机房空间"
          >
            <!-- 房间图标 -->
            <svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>

            <!-- 按钮标签：当前选中房间 -->
            <span class="font-medium whitespace-nowrap">
              <template v-if="selectedRoomCode === 'ALL'">
                全部机房 ({{ activeTotalRacks }}柜/{{ activeTotalAssets }}设备)
              </template>
              <template v-else>
                {{ currentRoom ? `${currentRoom.room_name} (${currentRoom.room_code})` : selectedRoomCode }}
              </template>
            </span>

            <!-- 下拉箭头 -->
            <svg
              class="w-3 h-3 transition-transform duration-200 opacity-60 shrink-0"
              :class="{ 'rotate-180': roomDropdownOpen }"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- 下拉菜单浮层 (深邃亚克力 popover，100% 遮光防透底) -->
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="opacity-0 translate-y-1 scale-95"
            enter-to-class="opacity-100 translate-y-0 scale-100"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="opacity-100 translate-y-0 scale-100"
            leave-to-class="opacity-0 translate-y-1 scale-95"
          >
            <div
              v-if="roomDropdownOpen"
              class="glass-acrylic-popover absolute right-0 mt-1.5 w-64 rounded-xl border z-50 py-1.5 text-xs select-none"
            >
              <!-- 选项 1: 全部机房 -->
              <button
                @click="selectedRoomCode = 'ALL'; roomDropdownOpen = false"
                class="w-full px-3 py-2 text-left flex items-center justify-between transition-colors"
                :class="[
                  selectedRoomCode === 'ALL'
                    ? (isLight ? 'bg-emerald-50 text-emerald-700 font-semibold' : 'bg-emerald-950/40 text-emerald-300 font-semibold')
                    : (isLight ? 'hover:bg-slate-100 text-slate-700' : 'hover:bg-white/[0.06] text-zinc-300')
                ]"
              >
                <div class="flex items-center space-x-2">
                  <span class="w-1.5 h-1.5 rounded-full" :class="selectedRoomCode === 'ALL' ? 'bg-emerald-500' : 'bg-transparent'"></span>
                  <span>全部机房 (全局概览)</span>
                </div>
                <span class="font-mono text-[10px] opacity-70">{{ activeTotalRacks }}柜 / {{ activeTotalAssets }}设备</span>
              </button>

              <div class="my-1 border-t" :class="isLight ? 'border-slate-100' : 'border-white/[0.06]'"></div>

              <div class="px-2.5 py-1 text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
                实训子机房与库房
              </div>

              <!-- 选项 2...N: 子机房列表 -->
              <button
                v-for="room in topologyData?.rooms || []"
                :key="room.room_code"
                @click="selectedRoomCode = room.room_code; roomDropdownOpen = false"
                class="w-full px-3 py-2 text-left flex items-center justify-between transition-colors"
                :class="[
                  selectedRoomCode === room.room_code
                    ? (isLight ? 'bg-emerald-50 text-emerald-700 font-semibold' : 'bg-emerald-950/40 text-emerald-300 font-semibold')
                    : (isLight ? 'hover:bg-slate-100 text-slate-700' : 'hover:bg-white/[0.06] text-zinc-300')
                ]"
              >
                <div class="flex items-center space-x-2 truncate pr-2">
                  <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="selectedRoomCode === room.room_code ? 'bg-emerald-500' : 'bg-transparent'"></span>
                  <span class="truncate">{{ room.room_name }}</span>
                </div>

                <div class="flex items-center space-x-1.5 shrink-0">
                  <span
                    v-if="room.stats.health_status === 'OVERHEAT'"
                    class="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"
                    title="存在超温高危设备"
                  ></span>
                  <span
                    v-else-if="room.stats.health_status === 'WARNING'"
                    class="w-1.5 h-1.5 rounded-full bg-amber-400"
                    title="存在预警设备"
                  ></span>
                  <span class="font-mono text-[10px] opacity-70">{{ room.room_code }}</span>
                </div>
              </button>
            </div>
          </Transition>
        </div>

        <!-- 教师/管理员可见：+ 新建机房 -->
        <button
          v-if="canManage"
          @click="openRoomModal('create')"
          class="px-2.5 py-1.5 rounded-xl transition-all font-medium whitespace-nowrap flex items-center space-x-1 text-xs bg-emerald-600/90 hover:bg-emerald-500 text-white shadow-xs active:scale-95"
          title="新建物理机房空间"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>新建机房</span>
        </button>
      </div>
    </div>

    <!-- 2. 当前选中机房元信息说明条 (当选中单间机房时呈现) -->
    <div
      v-if="currentRoom"
      class="px-4 py-2.5 rounded-xl border text-xs flex flex-wrap items-center justify-between gap-3 glass-card"
      :class="isLight ? 'border-slate-200 text-slate-600' : 'text-zinc-400'"
    >
      <div class="flex items-center space-x-2">
        <span class="font-medium" :class="isLight ? 'text-slate-900 font-semibold' : 'text-zinc-200'">{{ currentRoom.room_name }}</span>
        <span :class="isLight ? 'text-slate-400' : 'text-zinc-600'">|</span>
        <span>位置: <strong class="font-normal" :class="isLight ? 'text-slate-800 font-medium' : 'text-zinc-300'">{{ currentRoom.location }}</strong></span>
        <span :class="isLight ? 'text-slate-400' : 'text-zinc-600'">|</span>
        <span>安全责任人: <strong class="font-normal" :class="isLight ? 'text-slate-800 font-medium' : 'text-zinc-300'">{{ currentRoom.manager_teacher }}</strong></span>
      </div>

      <div class="flex items-center space-x-3 font-mono text-[11px]">
        <span>PDU 配电容量: <strong :class="isLight ? 'text-emerald-600 font-bold' : 'text-emerald-400'">{{ currentRoom.power_capacity_kw }} kW</strong></span>
        <span>在架资产: <strong :class="isLight ? 'text-cyan-700 font-bold' : 'text-cyan-400'">{{ currentRoom.stats.in_rack_count }} 台</strong></span>
        <span>配套设施: <strong :class="isLight ? 'text-purple-700 font-bold' : 'text-purple-400'">{{ currentRoom.stats.unracked_count }} 台</strong></span>

        <!-- 教师/管理员可见：编辑机房与删除机房 -->
        <div v-if="canManage" class="flex items-center space-x-1.5 ml-2 font-sans">
          <button
            @click="openRoomModal('edit', currentRoom)"
            class="px-2 py-0.5 rounded-md border text-[11px] flex items-center space-x-1 transition-all active:scale-95"
            :class="isLight ? 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50' : 'bg-zinc-800 border-white/[0.08] text-zinc-300 hover:bg-zinc-700'"
            title="编辑当前机房属性"
          >
            <svg class="w-3 h-3 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <span>编辑机房</span>
          </button>
          <button
            @click="handleDeleteRoom(currentRoom)"
            class="px-2 py-0.5 rounded-md border text-[11px] flex items-center space-x-1 transition-all active:scale-95"
            :class="isLight ? 'bg-rose-50 border-rose-300 text-rose-700 hover:bg-rose-100' : 'bg-rose-950/40 border-rose-500/30 text-rose-300 hover:bg-rose-900/50'"
            title="注销删除该机房"
          >
            <svg class="w-3 h-3 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            <span>注销机房</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 3. 大盘总览指标 5 磁贴 Bento Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      <!-- 磁贴 1: 机柜总数 -->
      <div
        class="p-3.5 rounded-2xl glass-card border flex flex-col justify-between"
        :class="isLight ? 'border-slate-200/80 shadow-xs' : ''"
      >
        <div class="flex items-center justify-between text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">
          <span>机柜总数</span>
          <svg class="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div class="mt-2 flex items-baseline space-x-1.5">
          <span class="text-2xl font-bold font-mono tracking-tight" :class="isLight ? 'text-slate-900' : 'text-zinc-100'">{{ activeMetrics.rack_count }}</span>
          <span class="text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">架 (标准 42U)</span>
        </div>
        <div class="mt-1 text-[10px] truncate" :class="isLight ? 'text-slate-400' : 'text-zinc-500'">
          {{ selectedRoomCode === 'ALL' ? '覆盖 3 间实训机房' : `${currentRoom?.room_code} 专属机柜群` }}
        </div>
      </div>

      <!-- 磁贴 2: U位总容量 -->
      <div
        class="p-3.5 rounded-2xl glass-card border flex flex-col justify-between"
        :class="isLight ? 'border-slate-200/80 shadow-xs' : ''"
      >
        <div class="flex items-center justify-between text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">
          <span>总空间容量</span>
          <svg class="w-4 h-4 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
        </div>
        <div class="mt-2 flex items-baseline space-x-1.5">
          <span class="text-2xl font-bold font-mono tracking-tight" :class="isLight ? 'text-slate-900' : 'text-zinc-100'">{{ activeMetrics.total_u }}</span>
          <span class="text-xs font-mono font-medium" :class="isLight ? 'text-cyan-700' : 'text-cyan-400'">U 位</span>
        </div>
        <div class="mt-1 text-[10px] truncate" :class="isLight ? 'text-slate-400' : 'text-zinc-500'">
          每机柜国际标准 42U
        </div>
      </div>

      <!-- 磁贴 3: 已用 U 位 -->
      <div
        class="p-3.5 rounded-2xl glass-card border flex flex-col justify-between"
        :class="isLight ? 'border-slate-200/80 shadow-xs' : ''"
      >
        <div class="flex items-center justify-between text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">
          <span>已占用 U 位</span>
          <svg class="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
        <div class="mt-2 flex items-baseline space-x-1.5">
          <span class="text-2xl font-bold font-mono tracking-tight" :class="isLight ? 'text-indigo-600' : 'text-indigo-400'">{{ activeMetrics.used_u }}</span>
          <span class="text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">U / 空闲 {{ activeMetrics.total_u - activeMetrics.used_u }} U</span>
        </div>
        <div class="mt-1 text-[10px] truncate" :class="isLight ? 'text-slate-400' : 'text-zinc-500'">
          在架物理服务器与网络设备
        </div>
      </div>

      <!-- 磁贴 4: 空间利用率 -->
      <div
        class="p-3.5 rounded-2xl glass-card border flex flex-col justify-between"
        :class="isLight ? 'border-slate-200/80 shadow-xs' : ''"
      >
        <div class="flex items-center justify-between text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">
          <span>空间利用率</span>
          <svg class="w-4 h-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
        </div>
        <div class="mt-2 flex items-baseline space-x-1.5">
          <span class="text-2xl font-bold font-mono tracking-tight" :class="isLight ? 'text-amber-600' : 'text-amber-400'">{{ activeMetrics.usage_rate }}%</span>
        </div>
        <!-- 进度条 -->
        <div class="mt-1 w-full rounded-full h-1.5 overflow-hidden" :class="isLight ? 'bg-slate-200' : 'bg-zinc-800'">
          <div
            class="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500"
            :style="{ width: `${Math.min(Math.max(activeMetrics.usage_rate, 0), 100)}%` }"
          ></div>
        </div>
      </div>

      <!-- 磁贴 5: 最高温与均温 -->
      <div
        class="p-3.5 rounded-2xl glass-card border flex flex-col justify-between col-span-2 sm:col-span-1"
        :class="isLight ? 'border-slate-200/80 shadow-xs' : ''"
      >
        <div class="flex items-center justify-between text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">
          <span>机房温控遥测</span>
          <svg class="w-4 h-4" :class="activeMetrics.max_temperature >= 40 ? 'text-rose-500 animate-pulse' : 'text-emerald-500'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div class="mt-2 flex items-baseline space-x-2">
          <span class="text-2xl font-bold font-mono tracking-tight" :class="activeMetrics.max_temperature >= 40 ? (isLight ? 'text-rose-600' : 'text-rose-400') : (isLight ? 'text-slate-900' : 'text-zinc-100')">
            {{ activeMetrics.max_temperature }}℃
          </span>
          <span class="text-xs" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">均温 {{ activeMetrics.avg_temperature }}℃</span>
        </div>
        <div class="mt-1 text-[10px] flex items-center gap-1 font-mono" :class="activeMetrics.max_temperature >= 40 ? (isLight ? 'text-rose-600 font-semibold' : 'text-rose-400') : (isLight ? 'text-emerald-700 font-semibold' : 'text-emerald-400')">
          <span class="w-1.5 h-1.5 rounded-full" :class="activeMetrics.max_temperature >= 40 ? 'bg-rose-500 animate-ping' : 'bg-emerald-500'"></span>
          <span>{{ activeMetrics.max_temperature >= 40 ? '核心超温告警触发' : '动环温控良好' }}</span>
        </div>
      </div>
    </div>

    <!-- 4. 2D 机架阵列渲染区 -->
    <div class="space-y-3 relative z-10">
      <div class="flex items-center justify-between relative z-20">
        <div class="flex items-center space-x-2">
          <span class="w-1.5 h-3.5 rounded-full bg-emerald-500"></span>
          <h4 class="text-xs sm:text-sm font-semibold text-zinc-200">
            {{ selectedRoomCode === 'ALL' ? '全机房标准机架阵列 (42U)' : `${currentRoom?.room_name} 机架阵列` }}
          </h4>
          <span class="text-xs text-zinc-500 font-mono">
            共 {{ displayedRacks.length }} 台机柜
          </span>

          <!-- 教师/管理员可见：暗淡透明、低调不抢眼的“机柜管理”下拉框按钮 (提升层级至 z-30) -->
          <div v-if="canManage" class="relative z-30 rack-dropdown-container ml-1">
            <button
              @click.stop="rackDropdownOpen = !rackDropdownOpen"
              type="button"
              class="px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 border select-none active:scale-95"
              :class="[
                isLight
                  ? 'bg-slate-100/80 hover:bg-slate-200/90 border-slate-200 text-slate-500 hover:text-slate-800'
                  : 'bg-zinc-800/50 hover:bg-zinc-700/60 border-white/[0.08] text-zinc-400 hover:text-zinc-200',
                rackDropdownOpen ? (isLight ? 'border-slate-400 text-slate-800' : 'border-cyan-500/40 text-cyan-300') : ''
              ]"
              title="机柜管理（立项新增机柜、配置修改与注销下线）"
            >
              <!-- 工业机柜 SVG 微标 -->
              <svg class="w-3.5 h-3.5 opacity-70 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span>机柜管理</span>
              <!-- 下拉微箭头 -->
              <svg
                class="w-3 h-3 transition-transform duration-200 opacity-60 shrink-0"
                :class="{ 'rotate-180': rackDropdownOpen }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- 机柜管理下拉浮层 -->
            <Transition
              enter-active-class="transition duration-150 ease-out"
              enter-from-class="opacity-0 translate-y-1 scale-95"
              enter-to-class="opacity-100 translate-y-0 scale-100"
              leave-active-class="transition duration-100 ease-in"
              leave-from-class="opacity-100 translate-y-0 scale-100"
              leave-to-class="opacity-0 translate-y-1 scale-95"
            >
              <div
                v-if="rackDropdownOpen"
                class="glass-acrylic-popover absolute left-0 mt-1.5 w-72 rounded-xl border z-50 py-1.5 text-xs select-none"
              >
                <!-- 选项 1: 立项新增工业机柜 -->
                <button
                  @click="openRackModal('create'); rackDropdownOpen = false"
                  class="w-full px-3 py-2 text-left flex items-center space-x-2 transition-colors group"
                  :class="isLight ? 'hover:bg-cyan-50 text-slate-700 hover:text-cyan-800' : 'hover:bg-cyan-950/40 text-zinc-300 hover:text-cyan-300'"
                >
                  <span class="p-1 rounded-md bg-cyan-500/10 text-cyan-400 group-hover:scale-105 transition-transform">
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </span>
                  <div>
                    <div class="font-medium text-xs">➕ 立项设立新工业机柜</div>
                    <div class="text-[10px] opacity-60">规划 42U 标准槽位与额定功耗</div>
                  </div>
                </button>

                <div class="my-1 border-t" :class="isLight ? 'border-slate-100' : 'border-white/[0.06]'"></div>

                <!-- 标题说明 -->
                <div class="px-3 py-1 text-[10px] font-mono text-zinc-500 flex items-center justify-between">
                  <span>在册机柜管理 (编辑 / 下线)</span>
                  <span>{{ displayedRacks.length }} 台</span>
                </div>

                <!-- 机柜列表条目：展示当前视图下的各台机柜 -->
                <div class="max-h-56 overflow-y-auto py-0.5 space-y-0.5">
                  <div
                    v-if="displayedRacks.length === 0"
                    class="px-3 py-3 text-center text-[11px] text-zinc-500"
                  >
                    当前区域暂无在册机柜
                  </div>
                  <div
                    v-for="rack in displayedRacks"
                    :key="rack.rack_id + rack.room_code"
                    class="px-3 py-1.5 flex items-center justify-between rounded-lg transition-colors group"
                    :class="isLight ? 'hover:bg-slate-100' : 'hover:bg-white/[0.04]'"
                  >
                    <!-- 机柜信息 -->
                    <div class="min-w-0 pr-2 space-y-0.5">
                      <div class="flex items-center space-x-1.5">
                        <span class="font-mono font-bold text-xs" :class="isLight ? 'text-slate-800' : 'text-zinc-200'">{{ rack.rack_id }}</span>
                        <span class="text-[10px] px-1 rounded font-mono" :class="isLight ? 'bg-slate-200/80 text-slate-600' : 'bg-zinc-800 text-zinc-400'">{{ rack.room_code }}</span>
                      </div>
                      <div class="text-[10px] truncate max-w-[150px] opacity-70" :title="rack.rack_name">
                        {{ rack.rack_name }}
                      </div>
                    </div>

                    <!-- 操作按钮组 -->
                    <div class="flex items-center space-x-1 shrink-0">
                      <button
                        @click="openRackModal('edit', rack); rackDropdownOpen = false"
                        class="p-1 rounded-md transition-colors"
                        :class="isLight ? 'text-slate-500 hover:text-cyan-700 hover:bg-slate-200' : 'text-zinc-400 hover:text-cyan-300 hover:bg-zinc-800'"
                        title="编辑该机柜配置参数"
                      >
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        @click="handleDeleteRack(rack); rackDropdownOpen = false"
                        class="p-1 rounded-md transition-colors"
                        :class="isLight ? 'text-slate-500 hover:text-rose-700 hover:bg-rose-50' : 'text-zinc-400 hover:text-rose-400 hover:bg-zinc-800'"
                        title="下线注销该机柜"
                      >
                        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <!-- 图例标识说明 -->
        <div class="hidden sm:flex items-center space-x-3 text-[11px] text-zinc-400">
          <span class="flex items-center space-x-1"><span class="w-2 h-2 rounded-full bg-emerald-400"></span><span>健康 (HEALTHY)</span></span>
          <span class="flex items-center space-x-1"><span class="w-2 h-2 rounded-full bg-amber-400"></span><span>预警 (WARNING)</span></span>
          <span class="flex items-center space-x-1"><span class="w-2 h-2 rounded-full bg-rose-400"></span><span>超温 (OVERHEAT)</span></span>
          <span class="flex items-center space-x-1"><span class="w-2 h-2 rounded-full bg-zinc-500"></span><span>离线 (OFFLINE)</span></span>
        </div>
      </div>

      <!-- 机柜网格排列容器 (items-stretch 开启等高对齐，gap-5 lg:gap-6 自适应紧凑间距) -->
      <div v-if="displayedRacks.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-5 lg:gap-6 items-stretch">
        <div
          v-for="rack in displayedRacks"
          :key="rack.rack_id + rack.room_code"
          class="rack-cabinet-wrapper rounded-2xl border p-3 flex flex-col justify-between h-full transition-all shadow-lg min-w-[200px]"
          :class="[
            isDragging && hoverRackId === rack.rack_id
              ? (hoverValid
                ? (isLight ? 'ring-2 ring-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.35)]' : 'ring-2 ring-emerald-400 shadow-[0_0_20px_rgba(52,211,153,0.35)]')
                : (isLight ? 'ring-2 ring-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.35)]' : 'ring-2 ring-rose-500 shadow-[0_0_20px_rgba(244,63,94,0.35)]'))
              : '',
            rack.health_status === 'OVERHEAT'
              ? (isLight ? 'border-rose-300/90 bg-rose-50/40 shadow-rose-200/50' : 'border-rose-500/40 bg-rose-950/10 shadow-rose-950/20')
              : rack.health_status === 'WARNING'
                ? (isLight ? 'border-amber-300/90 bg-amber-50/40 shadow-amber-200/50' : 'border-amber-500/30 bg-amber-950/10 shadow-amber-950/20')
                : 'glass-card'
          ]"
        >
          <!-- 机柜顶部控制门楣与铭牌 (通解架构：温度与机房位置对调，彻底杜绝任何字元溢出) -->
          <div
            class="rack-cabinet-header rounded-xl px-2.5 py-2 mb-2.5 border glass-card-sub flex flex-col justify-between space-y-1.5 shadow-inner shrink-0 overflow-hidden"
          >
            <!-- 第一行：机柜编号 (hover 提示机柜全称) 与 所属机房编号 (对调后居右) -->
            <div class="flex items-center justify-between gap-1.5 min-w-0">
              <div
                class="flex items-center space-x-1.5 min-w-0 shrink-0 cursor-help group/rackname"
                :title="`机柜全称: ${rack.rack_name}\n机柜编号: ${rack.rack_id}\n所属机房: ${rack.room_code}\n物理空间: 标准 42U 工业机架`"
              >
                <!-- 机柜工业指示灯 -->
                <span
                  class="w-2 h-2 rounded-full shrink-0"
                  :class="[
                    rack.health_status === 'OVERHEAT'
                      ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.9)] animate-ping'
                      : rack.health_status === 'WARNING'
                        ? 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.9)] animate-pulse'
                        : rack.assets.length === 0
                          ? (isLight ? 'bg-slate-300' : 'bg-zinc-600')
                          : 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]'
                  ]"
                ></span>
                <!-- 机柜编号 (鼠标悬停显示完整全称) -->
                <span
                  class="font-bold text-xs tracking-wide font-mono uppercase whitespace-nowrap shrink-0 group-hover/rackname:text-cyan-400 transition-colors"
                  :class="isLight ? 'text-slate-800' : 'text-zinc-100'"
                >{{ rack.rack_id }}</span>
              </div>

              <!-- 所属机房编号标签 (居右规范排版) -->
              <span
                class="text-[10px] px-1.5 py-0.2 rounded border font-sans whitespace-nowrap shrink-0 font-medium"
                :class="isLight ? 'bg-white border-slate-200 text-slate-600 shadow-xs' : 'bg-zinc-800 border-white/[0.06] text-zinc-400'"
                :title="`所属机房编号: ${rack.room_code}`"
              >
                {{ rack.room_code }}
              </span>
            </div>

            <!-- 第二行：柜内最高温 (对调至第二行左侧) 与 空间占用率 (精炼排版，100% 不溢出) -->
            <div class="flex items-center justify-between gap-1.5 min-w-0">
              <!-- 柜内最高温胶囊 (对调至第二行左侧) -->
              <span
                class="text-[10px] font-mono px-1.5 py-0.5 rounded-full border whitespace-nowrap shrink-0 shadow-xs flex items-center gap-1"
                :class="[
                  rack.max_temperature >= 40
                    ? (isLight ? 'bg-rose-100 border-rose-300 text-rose-700 font-bold' : 'bg-rose-500/15 border-rose-500/30 text-rose-300 font-semibold')
                    : (isLight ? 'bg-slate-200/80 border-slate-300 text-slate-700' : 'bg-zinc-800 border-white/[0.06] text-zinc-300')
                ]"
                :title="`机柜最高遥测温度: ${rack.max_temperature}℃`"
              >
                <span class="w-1 h-1 rounded-full shrink-0" :class="rack.max_temperature >= 40 ? 'bg-rose-500 animate-ping' : 'bg-emerald-400'"></span>
                <span>{{ rack.max_temperature }}℃</span>
              </span>

              <!-- 空间占用率与 U 位负载 (精简排版，彻底消除溢出) -->
              <span
                class="font-mono text-[10px] shrink-0 whitespace-nowrap"
                :class="isLight ? 'text-slate-600' : 'text-zinc-400'"
                :title="`在架空间占用: ${rack.used_u}U / 总容量: ${rack.total_u}U (负载率: ${rack.usage_rate}%)`"
              >
                <strong :class="isLight ? 'text-cyan-700 font-bold' : 'text-cyan-400'">{{ rack.used_u }}</strong>/{{ rack.total_u }}U <span class="opacity-80 font-normal">({{ rack.usage_rate }}%)</span>
              </span>
            </div>

            <!-- 第三行：机柜占用率微型进度条 -->
            <div class="w-full rounded-full h-1 overflow-hidden shrink-0" :class="isLight ? 'bg-slate-200' : 'bg-zinc-950'">
              <div
                class="h-full rounded-full transition-all duration-300"
                :class="rack.health_status === 'OVERHEAT' ? 'bg-rose-500' : 'bg-emerald-500'"
                :style="{ width: `${rack.usage_rate}%` }"
              ></div>
            </div>
          </div>

          <!-- 机柜主体：42U 真实物理金属导轨与槽位栅格 -->
          <div
            class="rack-cabinet-body relative rounded-xl border p-1.5 flex flex-1"
            :class="isLight ? 'border-slate-300 bg-slate-50/80 shadow-inner' : 'border-zinc-700/60 bg-zinc-950 shadow-[inset_0_2px_8px_rgba(0,0,0,0.8)]'"
            @dragover.prevent
            @dragleave="handleRackDragLeave($event, rack)"
          >
            <!-- 左侧导轨刻度标尺 (42U -> 1U) - 采用 42 行 CSS Grid 绝对行对齐 -->
            <div
              class="w-6 shrink-0 grid grid-cols-1 select-none text-[8px] font-mono text-right pr-1"
              :class="isLight ? 'border-r border-slate-200 text-slate-400' : 'border-r border-zinc-800/80 text-zinc-500'"
              style="grid-template-rows: repeat(42, minmax(0, 1fr)); height: 460px;"
            >
              <span
                v-for="u in [42, 38, 34, 30, 26, 22, 18, 14, 10, 6, 1]"
                :key="'l-' + u"
                class="flex items-center justify-end leading-none"
                :style="{ gridRowStart: 43 - u }"
              >
                {{ u }}
              </span>
            </div>

            <!-- 中间核心 42U CSS Grid 区域 (高度固化为 460px，支持紧凑工业布局) -->
            <div
              class="flex-1 grid grid-cols-1 gap-[1px] px-1 overflow-hidden relative"
              style="grid-template-rows: repeat(42, minmax(0, 1fr)); height: 460px;"
              @dragover.prevent="handleGridDragOver($event, rack)"
              @drop.prevent.stop="handleGridDrop($event, rack)"
            >
              <!-- 实时拖拽吸附高亮预览层 (Ghost Slot) -->
              <div
                v-if="isDragging && hoverRackId === rack.rack_id && hoverStartU !== null"
                class="z-30 pointer-events-none rounded flex flex-col justify-center items-center px-1 text-center font-mono select-none transition-all duration-75 overflow-hidden"
                :style="getGhostSlotStyle(hoverStartU, draggedHeight)"
                :class="hoverValid
                  ? (isLight
                    ? 'bg-emerald-500/35 border-2 border-dashed border-emerald-600 text-emerald-950 ring-2 ring-emerald-400 shadow-[0_0_16px_rgba(16,185,129,0.35)] animate-pulse'
                    : 'bg-emerald-500/30 border-2 border-dashed border-emerald-400 text-emerald-200 ring-2 ring-emerald-400/40 shadow-[0_0_16px_rgba(52,211,153,0.35)] animate-pulse')
                  : (isLight
                    ? 'bg-rose-500/35 border-2 border-dashed border-rose-600 text-rose-950 ring-2 ring-rose-400 shadow-[0_0_16px_rgba(244,63,94,0.35)]'
                    : 'bg-rose-500/30 border-2 border-dashed border-rose-500 text-rose-200 ring-2 ring-rose-500/40 shadow-[0_0_16px_rgba(244,63,94,0.35)]')"
              >
                <div class="text-[10px] font-bold leading-tight" :class="hoverValid ? (isLight ? 'text-emerald-950 font-extrabold' : 'text-emerald-300') : (isLight ? 'text-rose-950 font-extrabold' : 'text-rose-300')">
                  {{ hoverValid ? `✔ ${hoverReason}` : `⛔ ${hoverReason}` }}
                </div>
                <div v-if="hoverValid" class="text-[8px] leading-none mt-0.5 opacity-90">
                  释放鼠标即可完成物理调拨
                </div>
              </div>

              <!-- 渲染在架设备 (按 row-start 与 row-span 绝对跨越) -->
              <div
                v-for="asset in rack.assets"
                :key="asset.id"
                @click="onAssetClick(asset)"
                draggable="true"
                @dragstart="onDragStart($event, asset, rack)"
                @dragend="onDragEnd"
                class="rack-device-slot group cursor-grab active:cursor-grabbing relative rounded flex flex-col justify-center px-1.5 py-0.5 transition-all select-none shadow-md overflow-hidden"
                :style="{
                  gridRowStart: getRowStart(asset.start_u, asset.u_height),
                  gridRowEnd: `span ${asset.u_height}`,
                }"
                :class="[
                  deviceSlotClass(asset),
                  isDragging && draggedAsset?.id === asset.id ? 'opacity-35 scale-95 border-dashed ring-2 ring-cyan-400/60' : ''
                ]"
                :title="`【按住拖拽调度U位或跨柜迁移 | 点击查看全景档案】\n${asset.name} (${asset.asset_no})\n槽位: U${asset.start_u}~U${asset.start_u + asset.u_height - 1} (${asset.u_height}U)`"
              >
                <!-- 左右金属拉手仿真凹槽 -->
                <div
                  class="absolute left-0.5 top-1 bottom-1 w-0.5 rounded-full"
                  :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'bg-rose-300' : 'bg-slate-300') : 'bg-white/20'"
                ></div>
                <div
                  class="absolute right-0.5 top-1 bottom-1 w-0.5 rounded-full"
                  :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'bg-rose-300' : 'bg-slate-300') : 'bg-white/20'"
                ></div>

                <!-- 1U 紧凑单行呈现 -->
                <div v-if="asset.u_height === 1" class="flex items-center justify-between text-[9px] font-mono leading-none pl-1 pr-1">
                  <div class="flex items-center space-x-1 min-w-0">
                    <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="ledClass(asset.health_status)"></span>
                    <strong
                      class="truncate"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-950 font-bold' : 'text-slate-900 font-bold') : 'text-zinc-200 font-bold'"
                    >{{ asset.asset_no }}</strong>
                    <span
                      class="truncate hidden xs:inline"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-800' : 'text-slate-600') : 'text-zinc-400'"
                    >{{ asset.name }}</span>
                  </div>
                  <div class="flex items-center space-x-1.5 shrink-0">
                    <span :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-700 font-bold' : 'text-slate-600') : 'text-zinc-400'">{{ asset.metrics?.temperature }}℃</span>
                    <span
                      class="text-[8px] px-1 rounded font-bold"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'bg-rose-200 text-rose-900 border border-rose-300' : 'bg-cyan-100 text-cyan-900 border border-cyan-300') : 'bg-black/40 text-cyan-400'"
                    >1U</span>
                  </div>
                </div>

                <!-- 2U 规范两行呈现 -->
                <div v-else-if="asset.u_height === 2" class="flex flex-col justify-between h-full py-0.5 pl-1 pr-1">
                  <div class="flex items-center justify-between text-[10px] font-mono leading-tight">
                    <div class="flex items-center space-x-1.5 min-w-0">
                      <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="ledClass(asset.health_status)"></span>
                      <strong
                        class="truncate"
                        :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-950 font-bold' : 'text-slate-900 font-bold') : 'text-zinc-100 font-bold'"
                      >{{ asset.asset_no }}</strong>
                      <span
                        class="truncate text-[9px]"
                        :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-800' : 'text-slate-600') : 'text-zinc-400'"
                      >{{ asset.detail?.model_name || asset.name }}</span>
                    </div>
                    <span
                      class="text-[8px] px-1 rounded font-mono font-bold"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'bg-rose-200 text-rose-900 border border-rose-300' : 'bg-cyan-100 text-cyan-900 border border-cyan-300') : 'bg-black/40 text-cyan-300'"
                    >2U</span>
                  </div>
                  <div class="flex items-center justify-between text-[9px] font-mono mt-0.5">
                    <span
                      class="truncate font-semibold"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-700' : 'text-cyan-700') : 'text-cyan-400'"
                    >IP: {{ asset.detail?.management_ip || 'DHCP' }}</span>
                    <span
                      :class="[
                        asset.metrics?.temperature >= 40
                          ? (isLight ? 'text-rose-600 font-bold' : 'text-rose-400 font-bold')
                          : (isLight ? 'text-slate-600' : 'text-zinc-300')
                      ]"
                    >
                      {{ asset.metrics?.temperature }}℃ · {{ asset.metrics?.power_watts }}W
                    </span>
                  </div>
                </div>

                <!-- 4U 高密算力/海量存储多行完整呈现 (用户重点关注的超温设备清晰明亮展示) -->
                <div v-else class="flex flex-col justify-between h-full py-1 pl-1 pr-1">
                  <!-- 第一行：编号、状态与 4U 徽章 -->
                  <div class="flex items-center justify-between text-xs font-mono">
                    <div class="flex items-center space-x-1.5 min-w-0">
                      <span class="w-2 h-2 rounded-full shrink-0" :class="ledClass(asset.health_status)"></span>
                      <strong
                        class="truncate text-[11px]"
                        :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-950 font-bold' : 'text-slate-900 font-bold') : 'text-zinc-100 font-bold'"
                      >{{ asset.asset_no }}</strong>
                      <span class="text-[9px] px-1.5 py-0.5 rounded border shadow-xs" :class="healthBadgeClass(asset.health_status)">
                        {{ asset.health_status }}
                      </span>
                    </div>
                    <span
                      class="text-[9px] px-1.5 py-0.5 rounded font-mono font-bold border"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'bg-rose-200 text-rose-900 border-rose-300' : 'bg-cyan-100 text-cyan-900 border-cyan-300') : 'bg-black/50 text-cyan-300 border-cyan-500/20'"
                    >4U</span>
                  </div>

                  <!-- 第二行：设备主名称 -->
                  <div
                    class="text-[10px] font-medium truncate"
                    :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-900 font-semibold' : 'text-slate-800') : 'text-zinc-200'"
                  >
                    {{ asset.name }}
                  </div>

                  <!-- 第三行：型号与管理 IP -->
                  <div class="text-[9px] font-mono flex items-center justify-between">
                    <span
                      class="truncate"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-800/80' : 'text-slate-500') : 'text-zinc-400'"
                    >{{ asset.detail?.model_name || '4U Rack Server' }}</span>
                    <span
                      class="font-semibold"
                      :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'text-rose-700 font-bold' : 'text-cyan-700 font-bold') : 'text-cyan-400'"
                    >{{ asset.detail?.management_ip }}</span>
                  </div>

                  <!-- 第四行：传感器指标状态 -->
                  <div
                    class="text-[9px] font-mono flex items-center justify-between pt-0.5 border-t"
                    :class="isLight ? (asset.health_status === 'OVERHEAT' ? 'border-rose-300/80' : 'border-slate-200') : 'border-white/[0.08]'"
                  >
                    <span
                      :class="[
                        asset.metrics?.temperature >= 40
                          ? (isLight ? 'text-rose-600 font-bold' : 'text-rose-400 font-bold')
                          : (isLight ? 'text-slate-600' : 'text-zinc-300')
                      ]"
                    >
                      核心温度: {{ asset.metrics?.temperature }}℃
                    </span>
                    <span :class="isLight ? 'text-amber-700 font-medium' : 'text-amber-300'">功耗: {{ asset.metrics?.power_watts }}W</span>
                  </div>
                </div>
              </div>

              <!-- 渲染未占用的空闲 U 位 (微细网格插槽) -->
              <div
                v-for="slot in getFreeSlots(rack)"
                :key="'free-' + slot.u"
                @dragover.prevent="onSlotHover($event, rack, slot.u)"
                @drop.prevent.stop="handleGridDrop($event, rack)"
                class="free-u-slot group border-t transition-colors flex items-center justify-between px-1.5 text-[8px] font-mono select-none"
                :class="isLight ? 'border-slate-200/80 hover:border-cyan-400 hover:bg-cyan-50/50 text-slate-400' : 'border-zinc-800/40 hover:border-cyan-500/40 hover:bg-cyan-500/5 text-zinc-600'"
                :style="{
                  gridRowStart: 43 - slot.u,
                  gridRowEnd: 'span 1',
                }"
                :title="`U${slot.u} 槽位空闲 (支持 19寸 标准导轨设备上架)`"
              >
                <span>U{{ slot.u }}</span>
                <span class="hidden group-hover:inline text-[7px]" :class="isLight ? 'text-cyan-600' : 'text-cyan-400/80'">空闲</span>
              </div>
            </div>

            <!-- 右侧导轨刻度标尺 (42U -> 1U) - 采用 42 行 CSS Grid 绝对行对齐 -->
            <div
              class="w-6 shrink-0 grid grid-cols-1 select-none text-[8px] font-mono text-left pl-1"
              :class="isLight ? 'border-l border-slate-200 text-slate-400' : 'border-l border-zinc-800/80 text-zinc-500'"
              style="grid-template-rows: repeat(42, minmax(0, 1fr)); height: 460px;"
            >
              <span
                v-for="u in [42, 38, 34, 30, 26, 22, 18, 14, 10, 6, 1]"
                :key="'r-' + u"
                class="flex items-center justify-start leading-none"
                :style="{ gridRowStart: 43 - u }"
              >
                {{ u }}
              </span>
            </div>
          </div>

          <!-- 机柜底座承重轮脚与接地标志仿真 (mt-auto 固定沉底，保证三柜底边绝对水平对齐) -->
          <div
            class="rack-cabinet-footer mt-2.5 pt-1.5 border-t flex items-center justify-between text-[9px] font-mono px-1 shrink-0"
            :class="isLight ? 'border-slate-200/90 text-slate-500' : 'border-white/[0.06] text-zinc-500'"
          >
            <span class="flex items-center space-x-1">
              <span class="w-1 h-1 rounded-full bg-emerald-500"></span>
              <span :class="isLight ? 'text-slate-600' : 'text-zinc-400'">PE 接地正常</span>
            </span>
            <span :class="isLight ? 'text-slate-500' : 'text-zinc-500'">220V/380V DUAL PDU</span>
          </div>
        </div>
      </div>
      <div v-else class="p-8 rounded-2xl border border-white/[0.08] bg-zinc-900/40 text-center flex flex-col items-center justify-center space-y-2 text-zinc-400">
        <svg class="w-8 h-8 text-zinc-500 mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
        <span class="text-xs font-medium text-zinc-300">当前区域未设立机架式机柜（纯仓储/备用存放区）</span>
        <span class="text-[11px] text-zinc-500">在册资产全量列入下方周边配套与实验仪器区登记管理</span>
        <button
          v-if="canManage"
          @click="openRackModal('create')"
          class="mt-2 px-3.5 py-1.5 rounded-xl bg-cyan-600/90 hover:bg-cyan-500 text-white text-xs font-medium flex items-center space-x-1.5 transition-all shadow-sm active:scale-95"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>在当前区域立项设立新机柜</span>
        </button>
      </div>
    </div>

    <!-- 5. 底部：周边配套与实验仪器区 (确保全机房 15 台在册资产 100% 物理可视) -->
    <div class="space-y-3 pt-2 border-t border-white/[0.08]">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-purple-400">
            <!-- 配套外设图标 -->
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </span>
          <h4 class="text-xs sm:text-sm font-semibold text-zinc-200">
            周边配套与实验仪器区 (动力温控 / 实验教学 / 备用仓储)
          </h4>
          <span class="text-xs text-zinc-400 font-mono">
            ({{ displayedUnrackedAssets.length }} 台设备)
          </span>
        </div>
        <span class="text-[11px] text-zinc-500">
          点击卡片查看详细参数 · 服务器与网络设备支持直接拖拽至上方机柜
        </span>
      </div>

      <!-- 非机架外设资产网格：优化响应式断点与 min-w-0 保护，杜绝窄屏挤压 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-3.5">
        <div
          v-for="asset in displayedUnrackedAssets"
          :key="asset.id"
          @click="onAssetClick(asset)"
          :draggable="isUnrackedDraggable(asset)"
          @dragstart="isUnrackedDraggable(asset) && onDragStart($event, asset, null)"
          @dragend="onDragEnd"
          class="unracked-card p-3.5 rounded-xl border glass-card hover:border-purple-400/40 transition-all flex flex-col justify-between space-y-2.5 group shadow-sm active:scale-[0.99] min-w-0 overflow-hidden"
          :class="[
            isUnrackedDraggable(asset) ? 'cursor-grab active:cursor-grabbing hover:border-cyan-400/50 hover:shadow-cyan-400/10' : 'cursor-pointer',
            isDragging && draggedAsset?.id === asset.id ? 'opacity-35 scale-95 border-dashed ring-2 ring-cyan-400/60' : ''
          ]"
        >
          <!-- 头部：分类徽章、资产编号、名称与健康状态胶囊 -->
          <div class="flex items-start justify-between gap-2 min-w-0">
            <div class="flex items-center space-x-2 min-w-0 flex-1">
              <span class="p-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400 shrink-0">
                <!-- 配电温控 -->
                <svg v-if="asset.category === '配电温控'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <!-- 实验教学 -->
                <svg v-else-if="asset.category === '实验教学'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
                <!-- 服务器/网络外设 -->
                <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </span>
              <div class="min-w-0 flex-1">
                <div class="text-xs font-bold text-zinc-100 group-hover:text-purple-300 transition-colors truncate font-mono">
                  {{ asset.asset_no }}
                </div>
                <div class="text-[10px] text-zinc-400 truncate mt-0.5" :title="asset.name">
                  {{ asset.name }}
                </div>
              </div>
            </div>

            <!-- 可拖拽上架徽章与健康胶囊 -->
            <div class="flex items-center space-x-1.5 shrink-0">
              <span
                v-if="isUnrackedDraggable(asset)"
                class="text-[9px] px-1.5 py-0.5 rounded border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 font-mono flex items-center gap-1 shrink-0 select-none cursor-grab"
                title="按住鼠标拖拽此卡片，可直接拖入上方机柜空闲槽位完成物理上架入柜"
              >
                <svg class="w-2.5 h-2.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                </svg>
                <span>可拖拽上架</span>
              </span>

              <!-- 健康胶囊：强制 shrink-0 与 whitespace-nowrap，内嵌呼吸微标点，杜绝溢出截断 -->
              <span
                class="text-[9px] px-2 py-0.5 rounded-full border font-mono shrink-0 whitespace-nowrap flex items-center gap-1 shadow-sm"
                :class="healthBadgeClass(asset.health_status)"
              >
                <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="ledClass(asset.health_status)"></span>
                <span>{{ asset.health_status }}</span>
              </span>
            </div>
          </div>

          <!-- 规格说明与位置：自适应省略截断，杜绝溢出 -->
          <div class="text-[11px] text-zinc-400 space-y-1 min-w-0">
            <div class="flex items-center space-x-1.5 min-w-0">
              <span class="text-zinc-500 shrink-0">位置:</span>
              <span class="text-zinc-200 truncate min-w-0 flex-1" :title="asset.location">{{ asset.location }}</span>
            </div>
            <div class="flex items-center space-x-1.5 min-w-0">
              <span class="text-zinc-500 shrink-0">规格:</span>
              <span class="text-zinc-300 truncate min-w-0 flex-1" :title="asset.specs || asset.detail?.model_name">{{ asset.specs || asset.detail?.model_name || '标准实验设施' }}</span>
            </div>
          </div>

          <!-- 底部参数指标与借用状态 -->
          <div class="pt-2 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono gap-1 min-w-0">
            <span class="truncate min-w-0" :class="asset.borrow_status === 'AVAILABLE' ? 'text-emerald-400' : 'text-amber-400'">
              {{ asset.borrow_status === 'AVAILABLE' ? '● 空闲可用' : `● ${asset.borrower || '在用'}` }}
            </span>
            <span class="text-zinc-400 shrink-0 whitespace-nowrap">
              {{ asset.metrics?.temperature }}℃ · {{ asset.metrics?.power_watts }}W
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 6. 机房管理模态框 (新增/编辑) -->
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
          v-if="showRoomModal"
          class="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/75 backdrop-blur-md"
          @click.self="showRoomModal = false"
        >
          <div
            class="w-full max-w-md rounded-3xl border p-5 sm:p-6 space-y-4 shadow-2xl backdrop-blur-2xl text-xs"
            :class="isLight ? 'bg-white border-slate-200 text-slate-800' : 'bg-zinc-900 border-white/[0.12] text-zinc-200'"
          >
            <!-- 头部 -->
            <div class="flex items-center justify-between border-b pb-3" :class="isLight ? 'border-slate-200' : 'border-white/[0.08]'">
              <div class="flex items-center space-x-2.5">
                <span class="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </span>
                <h3 class="text-sm font-semibold" :class="isLight ? 'text-slate-900' : 'text-zinc-100'">
                  {{ roomModalMode === 'create' ? '新建物理机房空间' : '编辑机房信息' }}
                </h3>
              </div>
              <button
                @click="showRoomModal = false"
                class="text-zinc-400 hover:text-zinc-100 p-1.5 rounded-lg hover:bg-white/[0.08] transition-colors"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- 表单 -->
            <form @submit.prevent="handleSaveRoom" class="space-y-3">
              <div class="space-y-1">
                <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                  机房编号 <span class="text-rose-400">*</span>
                </label>
                <input
                  v-model="roomForm.room_code"
                  type="text"
                  placeholder="如: ROOM-401"
                  required
                  :disabled="roomModalMode === 'edit'"
                  class="w-full rounded-lg px-3 py-2 border font-mono disabled:opacity-50 focus:outline-none transition-colors"
                  :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-emerald-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-emerald-500 text-zinc-200'"
                />
              </div>

              <div class="space-y-1">
                <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                  机房显示名称 <span class="text-rose-400">*</span>
                </label>
                <input
                  v-model="roomForm.room_name"
                  type="text"
                  placeholder="如: 实训楼401 工业互联网与边缘实训室"
                  required
                  class="w-full rounded-lg px-3 py-2 border focus:outline-none transition-colors"
                  :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-emerald-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-emerald-500 text-zinc-200'"
                />
              </div>

              <div class="space-y-1">
                <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                  物理位置 <span class="text-rose-400">*</span>
                </label>
                <input
                  v-model="roomForm.location"
                  type="text"
                  placeholder="如: 实训楼4层西侧401室"
                  required
                  class="w-full rounded-lg px-3 py-2 border focus:outline-none transition-colors"
                  :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-emerald-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-emerald-500 text-zinc-200'"
                />
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                  <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                    责任教师/安全员 <span class="text-rose-400">*</span>
                  </label>
                  <input
                    v-model="roomForm.manager_teacher"
                    type="text"
                    placeholder="如: 王主管 / 李老师"
                    required
                    class="w-full rounded-lg px-3 py-2 border focus:outline-none transition-colors"
                    :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-emerald-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-emerald-500 text-zinc-200'"
                  />
                </div>

                <div class="space-y-1">
                  <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                    PDU配电容量(kW)
                  </label>
                  <input
                    v-model.number="roomForm.power_capacity_kw"
                    type="number"
                    step="0.5"
                    min="0"
                    placeholder="如: 50.0"
                    class="w-full rounded-lg px-3 py-2 border font-mono focus:outline-none transition-colors"
                    :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-emerald-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-emerald-500 text-zinc-200'"
                  />
                </div>
              </div>

              <div class="pt-3 border-t flex items-center justify-end space-x-2" :class="isLight ? 'border-slate-200' : 'border-white/[0.08]'">
                <button
                  type="button"
                  @click="showRoomModal = false"
                  class="px-3.5 py-1.5 rounded-xl border transition-colors"
                  :class="isLight ? 'border-slate-300 hover:bg-slate-100 text-slate-600' : 'border-white/[0.08] hover:bg-zinc-800 text-zinc-300'"
                >
                  取消
                </button>
                <button
                  type="submit"
                  :disabled="isSubmittingRoom"
                  class="px-4 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition-all shadow-sm disabled:opacity-50 flex items-center space-x-1"
                >
                  <span v-if="isSubmittingRoom" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span>{{ roomModalMode === 'create' ? '保存并创建' : '保存修改' }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 7. 机柜管理模态框 (新增/编辑) -->
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
          v-if="showRackModal"
          class="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/75 backdrop-blur-md"
          @click.self="showRackModal = false"
        >
          <div
            class="w-full max-w-md rounded-3xl border p-5 sm:p-6 space-y-4 shadow-2xl backdrop-blur-2xl text-xs"
            :class="isLight ? 'bg-white border-slate-200 text-slate-800' : 'bg-zinc-900 border-white/[0.12] text-zinc-200'"
          >
            <!-- 头部 -->
            <div class="flex items-center justify-between border-b pb-3" :class="isLight ? 'border-slate-200' : 'border-white/[0.08]'">
              <div class="flex items-center space-x-2.5">
                <span class="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </span>
                <h3 class="text-sm font-semibold" :class="isLight ? 'text-slate-900' : 'text-zinc-100'">
                  {{ rackModalMode === 'create' ? '立项新增工业标准机柜' : '编辑机柜配置参数' }}
                </h3>
              </div>
              <button
                @click="showRackModal = false"
                class="text-zinc-400 hover:text-zinc-100 p-1.5 rounded-lg hover:bg-white/[0.08] transition-colors"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- 表单 -->
            <form @submit.prevent="handleSaveRack" class="space-y-3">
              <div class="space-y-1">
                <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                  所属机房 <span class="text-rose-400">*</span>
                </label>
                <select
                  v-model="rackForm.room_code"
                  required
                  class="w-full rounded-lg px-3 py-2 border focus:outline-none transition-colors"
                  :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-cyan-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-cyan-500 text-zinc-200'"
                >
                  <option
                    v-for="r in topologyData?.rooms || []"
                    :key="r.room_code"
                    :value="r.room_code"
                  >
                    {{ r.room_code }} - {{ r.room_name }}
                  </option>
                </select>
              </div>

              <div class="space-y-1">
                <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                  机柜编号 <span class="text-rose-400">*</span>
                </label>
                <input
                  v-model="rackForm.rack_id"
                  type="text"
                  placeholder="如: 机柜A03, 机柜B02"
                  required
                  :disabled="rackModalMode === 'edit'"
                  class="w-full rounded-lg px-3 py-2 border font-mono disabled:opacity-50 focus:outline-none transition-colors"
                  :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-cyan-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-cyan-500 text-zinc-200'"
                />
              </div>

              <div class="space-y-1">
                <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                  机柜显示名称 <span class="text-rose-400">*</span>
                </label>
                <input
                  v-model="rackForm.rack_name"
                  type="text"
                  placeholder="如: A03 智算高通量扩展机柜"
                  required
                  class="w-full rounded-lg px-3 py-2 border focus:outline-none transition-colors"
                  :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-cyan-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-cyan-500 text-zinc-200'"
                />
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                  <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                    可用槽位空间(U)
                  </label>
                  <input
                    v-model.number="rackForm.total_u"
                    type="number"
                    min="1"
                    max="100"
                    placeholder="默认 42"
                    class="w-full rounded-lg px-3 py-2 border font-mono focus:outline-none transition-colors"
                    :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-cyan-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-cyan-500 text-zinc-200'"
                  />
                </div>

                <div class="space-y-1">
                  <label class="font-medium" :class="isLight ? 'text-slate-700' : 'text-zinc-300'">
                    额定功耗(W)
                  </label>
                  <input
                    v-model.number="rackForm.power_rating_w"
                    type="number"
                    min="0"
                    placeholder="默认 4500"
                    class="w-full rounded-lg px-3 py-2 border font-mono focus:outline-none transition-colors"
                    :class="isLight ? 'bg-slate-50 border-slate-300 focus:border-cyan-500 text-slate-800' : 'bg-zinc-950/70 border-white/[0.08] focus:border-cyan-500 text-zinc-200'"
                  />
                </div>
              </div>

              <div class="pt-3 border-t flex items-center justify-end space-x-2" :class="isLight ? 'border-slate-200' : 'border-white/[0.08]'">
                <button
                  type="button"
                  @click="showRackModal = false"
                  class="px-3.5 py-1.5 rounded-xl border transition-colors"
                  :class="isLight ? 'border-slate-300 hover:bg-slate-100 text-slate-600' : 'border-white/[0.08] hover:bg-zinc-800 text-zinc-300'"
                >
                  取消
                </button>
                <button
                  type="submit"
                  :disabled="isSubmittingRack"
                  class="px-4 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium transition-all shadow-sm disabled:opacity-50 flex items-center space-x-1"
                >
                  <span v-if="isSubmittingRack" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span>{{ rackModalMode === 'create' ? '确认立柜投产' : '保存机柜配置' }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  theme: {
    type: String,
    default: 'dark',
  },
  currentUser: {
    type: Object,
    default: () => ({ role: 'ADMIN' }),
  },
})

const emit = defineEmits(['inspectAsset', 'refresh'])

// 教师与管理员权限感知
const canManage = computed(() => {
  const role = props.currentUser?.role
  return role === 'ADMIN' || role === 'TEACHER'
})

// 主题动态感知 (双重判定：props 优先，fallback 到 html 根类)
const isLight = computed(() => {
  return props.theme === 'light' || (typeof document !== 'undefined' && document.documentElement.classList.contains('light'))
})

// ==========================================
// 机房管理模态框与全生命周期交互逻辑
// ==========================================
const showRoomModal = ref(false)
const roomModalMode = ref('create') // 'create' | 'edit'
const isSubmittingRoom = ref(false)
const roomForm = reactive({
  room_code: '',
  room_name: '',
  location: '',
  manager_teacher: '',
  power_capacity_kw: 50.0,
})

function openRoomModal(mode, room = null) {
  roomModalMode.value = mode
  if (mode === 'edit' && room) {
    roomForm.room_code = room.room_code
    roomForm.room_name = room.room_name
    roomForm.location = room.location
    roomForm.manager_teacher = room.manager_teacher
    roomForm.power_capacity_kw = room.power_capacity_kw || 0.0
  } else {
    roomForm.room_code = ''
    roomForm.room_name = ''
    roomForm.location = ''
    roomForm.manager_teacher = props.currentUser?.real_name || '王主管'
    roomForm.power_capacity_kw = 50.0
  }
  showRoomModal.value = true
}

async function handleSaveRoom() {
  if (!roomForm.room_code || !roomForm.room_name || !roomForm.location || !roomForm.manager_teacher) {
    showToast('请填写所有必填字段', 'error')
    return
  }
  isSubmittingRoom.value = true
  try {
    if (roomModalMode.value === 'create') {
      await api.createRoom({
        room_code: roomForm.room_code.trim(),
        room_name: roomForm.room_name.trim(),
        location: roomForm.location.trim(),
        manager_teacher: roomForm.manager_teacher.trim(),
        power_capacity_kw: Number(roomForm.power_capacity_kw) || 0,
      })
      showToast(`机房 ${roomForm.room_code} 创建成功`, 'success')
      selectedRoomCode.value = roomForm.room_code.trim()
    } else {
      await api.updateRoom(roomForm.room_code, {
        room_name: roomForm.room_name.trim(),
        location: roomForm.location.trim(),
        manager_teacher: roomForm.manager_teacher.trim(),
        power_capacity_kw: Number(roomForm.power_capacity_kw) || 0,
      })
      showToast(`机房 ${roomForm.room_code} 配置更新成功`, 'success')
    }
    showRoomModal.value = false
    await loadTopology()
    emit('refresh')
  } catch (err) {
    showToast(err.message || '操作机房失败', 'error')
  } finally {
    isSubmittingRoom.value = false
  }
}

async function handleDeleteRoom(room) {
  if (!room) return
  if (!window.confirm(`确定要注销机房「${room.room_name} (${room.room_code})」吗？\n若机房下仍有在册机柜或设备，安全联锁将阻断注销。`)) {
    return
  }
  try {
    const res = await api.deleteRoom(room.room_code)
    showToast(res?.message || `机房 ${room.room_code} 已注销`, 'success')
    selectedRoomCode.value = 'ALL'
    await loadTopology()
    emit('refresh')
  } catch (err) {
    showToast(err.message || '注销机房失败', 'error')
  }
}

// ==========================================
// 工业机柜管理模态框与全生命周期交互逻辑
// ==========================================
const showRackModal = ref(false)
const rackModalMode = ref('create') // 'create' | 'edit'
const isSubmittingRack = ref(false)
const rackForm = reactive({
  room_code: '',
  rack_id: '',
  rack_name: '',
  total_u: 42,
  power_rating_w: 4500,
})

function openRackModal(mode, rack = null) {
  rackModalMode.value = mode
  if (mode === 'edit' && rack) {
    rackForm.room_code = rack.room_code
    rackForm.rack_id = rack.rack_id
    rackForm.rack_name = rack.rack_name
    rackForm.total_u = rack.total_u || 42
    rackForm.power_rating_w = rack.power_rating_w || 4500
  } else {
    const defaultRoom = (currentRoom.value ? currentRoom.value.room_code : topologyData.value?.rooms?.[0]?.room_code) || 'ROOM-201'
    rackForm.room_code = defaultRoom
    rackForm.rack_id = ''
    rackForm.rack_name = ''
    rackForm.total_u = 42
    rackForm.power_rating_w = 4500
  }
  showRackModal.value = true
}

async function handleSaveRack() {
  if (!rackForm.room_code || !rackForm.rack_id || !rackForm.rack_name) {
    showToast('请填写所有必填字段', 'error')
    return
  }
  isSubmittingRack.value = true
  try {
    if (rackModalMode.value === 'create') {
      await api.createRack({
        room_code: rackForm.room_code,
        rack_id: rackForm.rack_id.trim(),
        rack_name: rackForm.rack_name.trim(),
        total_u: Number(rackForm.total_u) || 42,
        power_rating_w: Number(rackForm.power_rating_w) || 4500,
      })
      showToast(`机柜 ${rackForm.rack_id} 立项投产成功`, 'success')
      if (selectedRoomCode.value !== 'ALL' && selectedRoomCode.value !== rackForm.room_code) {
        selectedRoomCode.value = rackForm.room_code
      }
    } else {
      await api.updateRack(rackForm.rack_id, {
        room_code: rackForm.room_code,
        rack_name: rackForm.rack_name.trim(),
        total_u: Number(rackForm.total_u) || 42,
        power_rating_w: Number(rackForm.power_rating_w) || 4500,
      })
      showToast(`机柜 ${rackForm.rack_id} 配置已更新`, 'success')
    }
    showRackModal.value = false
    await loadTopology()
    emit('refresh')
  } catch (err) {
    showToast(err.message || '操作机柜失败', 'error')
  } finally {
    isSubmittingRack.value = false
  }
}

async function handleDeleteRack(rack) {
  if (!rack) return
  // 安全联锁前端先行友好拦截
  if (rack.assets && rack.assets.length > 0) {
    showToast(`该机柜内尚有 ${rack.assets.length} 台在架设备，请先将设备拖拽迁出至其他机柜或下架后再下线该机柜`, 'error')
    return
  }
  if (!window.confirm(`确定要下线注销机柜「${rack.rack_name} (${rack.rack_id})」吗？`)) {
    return
  }
  try {
    const res = await api.deleteRack(rack.rack_id)
    showToast(res?.message || `机柜 ${rack.rack_id} 已成功下线注销`, 'success')
    await loadTopology()
    emit('refresh')
  } catch (err) {
    showToast(err.message || '下线机柜失败', 'error')
  }
}

// 状态定义
const loading = ref(false)
const topologyData = ref(null)
const selectedRoomCode = ref('ALL') // 'ALL' 或 'ROOM-201', 'ROOM-101', 'ROOM-301'
const roomDropdownOpen = ref(false)
const rackDropdownOpen = ref(false)

function closeDropdownsOnClickOutside(e) {
  if (roomDropdownOpen.value && !e.target.closest('.room-dropdown-container')) {
    roomDropdownOpen.value = false
  }
  if (rackDropdownOpen.value && !e.target.closest('.rack-dropdown-container')) {
    rackDropdownOpen.value = false
  }
}

// 加载机架拓扑大盘
async function loadTopology() {
  loading.value = true
  try {
    const data = await api.getTopology()
    topologyData.value = data
  } catch (err) {
    console.error('加载拓扑数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTopology()
  window.addEventListener('click', closeDropdownsOnClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', closeDropdownsOnClickOutside)
})

// 计算当前选中的机房对象 (若为 ALL 则为 null)
const currentRoom = computed(() => {
  if (!topologyData.value?.rooms || selectedRoomCode.value === 'ALL') return null
  return topologyData.value.rooms.find((r) => r.room_code === selectedRoomCode.value) || null
})

// 顶部标题文本
const activeRoomTitle = computed(() => {
  if (selectedRoomCode.value === 'ALL') return '实训大楼全部机房'
  return currentRoom.value?.room_name || selectedRoomCode.value
})

// 核心 5 磁贴大盘指标计算 (默认 3 柜，126U)
const activeTotalRacks = computed(() => topologyData.value?.summary?.total_racks ?? 3)
const activeTotalAssets = computed(() => topologyData.value?.summary?.total_assets ?? 15)

const activeMetrics = computed(() => {
  if (currentRoom.value) {
    return {
      rack_count: currentRoom.value.stats.rack_count,
      total_u: currentRoom.value.stats.total_u,
      used_u: currentRoom.value.stats.used_u,
      usage_rate: currentRoom.value.stats.usage_rate,
      max_temperature: currentRoom.value.stats.max_temperature,
      avg_temperature: currentRoom.value.stats.avg_temperature,
    }
  }
  const summary = topologyData.value?.summary
  return {
    rack_count: summary?.total_racks ?? 3,
    total_u: summary?.total_u ?? 126,
    used_u: summary?.used_u ?? 17,
    usage_rate: summary?.usage_rate ?? 13.5,
    max_temperature: summary?.max_temperature ?? 22.0,
    avg_temperature: summary?.avg_temperature ?? 22.0,
  }
})

// 需渲染的机柜列表
const displayedRacks = computed(() => {
  if (!topologyData.value?.rooms) return []
  if (currentRoom.value) {
    return currentRoom.value.racks
  }
  // 全部机房：合并所有机房的所有机柜
  return topologyData.value.rooms.flatMap((r) => r.racks)
})

// 需渲染的非机架外设
const displayedUnrackedAssets = computed(() => {
  if (!topologyData.value) return []
  if (currentRoom.value) {
    return currentRoom.value.unracked_assets
  }
  return topologyData.value.unracked_assets || []
})

// 辅助计算：CSS Grid 起始行计算 (自底向上映射到从顶向下的 grid-row，带严格边界保护)
function getRowStart(startU, uHeight) {
  const st = Math.max(1, Math.min(42, Number(startU) || 1))
  const h = Math.max(1, Math.min(42 - st + 1, Number(uHeight) || 1))
  return 43 - (st + h - 1)
}

// 辅助计算：拖拽吸附槽位精确样式 (防止多U设备越界拖拽时向上溢出导致视觉向下反向渗透)
function getGhostSlotStyle(startU, uHeight) {
  const st = Math.max(1, Math.min(42, Number(startU) || 1))
  const rawH = Math.max(1, Number(uHeight) || 1)
  const clampedH = Math.max(1, Math.min(42 - st + 1, rawH))
  const rowStart = 43 - (st + clampedH - 1)
  return {
    gridRowStart: rowStart,
    gridRowEnd: `span ${clampedH}`,
  }
}

// 辅助计算：获取该机柜未被占用的空闲插槽列表
function getFreeSlots(rack) {
  const occupiedSet = new Set()
  for (const asset of rack.assets || []) {
    const st = Number(asset.start_u) || 1
    const h = Number(asset.u_height) || 1
    for (let u = st; u < st + h; u++) {
      occupiedSet.add(u)
    }
  }
  const free = []
  const totalU = rack.total_u || 42
  for (let u = 1; u <= totalU; u++) {
    if (!occupiedSet.has(u)) {
      free.push({ u })
    }
  }
  return free
}

// 数字孪生拖拽调度引擎状态
const isDragging = ref(false)
const draggedAsset = ref(null)
const draggedSourceRack = ref(null)
const draggedHeight = ref(1)
const isSubmittingDrop = ref(false)
let hasDragged = false

const hoverRackId = ref(null)
const hoverStartU = ref(null)
const hoverValid = ref(false)
const hoverReason = ref('')

const toastMessage = ref('')
const toastType = ref('success')
let toastTimer = null

function showToast(msg, type = 'success') {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = msg
  toastType.value = type
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 3500)
}

function isUnrackedDraggable(asset) {
  return asset.category === '服务器' || asset.category === '网络设备'
}

function onDragStart(e, asset, sourceRack) {
  hasDragged = true
  isDragging.value = true
  draggedAsset.value = asset
  draggedSourceRack.value = sourceRack

  let h = Number(asset.u_height) || 0
  if (!h && asset.detail?.extra_params) {
    try {
      const ep = JSON.parse(asset.detail.extra_params)
      if (ep.u_height) h = Number(ep.u_height)
      else if (ep.rack_units) {
        const match = String(ep.rack_units).match(/(\d+)/)
        if (match) h = Number(match[1])
      }
    } catch (err) {}
  }
  if (!h) {
    if (asset.category === '服务器') {
      h = (asset.specs?.includes('GPU') || asset.name?.includes('GPU')) ? 4 : 2
    } else if (asset.category === '网络设备') {
      h = 1
    } else {
      h = 1
    }
  }
  draggedHeight.value = h

  e.dataTransfer.effectAllowed = 'move'
  try {
    e.dataTransfer.setData('text/plain', String(asset.id))
  } catch (err) {}
}

function onDragEnd() {
  isDragging.value = false
  draggedAsset.value = null
  draggedSourceRack.value = null
  draggedHeight.value = 1
  hoverRackId.value = null
  hoverStartU.value = null
  hoverValid.value = false
  hoverReason.value = ''
  setTimeout(() => {
    hasDragged = false
  }, 100)
}

function checkPlacement(rack, targetStartU, height, currentAssetId) {
  const st = Number(targetStartU) || 1
  const h = Number(height) || 1
  const ed = st + h - 1

  // 1. 越界检测
  if (st < 1 || ed > 42) {
    return {
      valid: false,
      reason: st < 1
        ? '空间不足: 槽位越界 (低于 U1)'
        : `空间不足: ${h}U 设备拖至 U${st} 会超出 42U 机柜顶端 (越界至 U${ed})`,
    }
  }

  // 2. 槽位碰撞冲突检测
  for (const other of rack.assets || []) {
    if (currentAssetId && String(other.id) === String(currentAssetId)) {
      continue // 同机柜内调整U位，排除自身既有空间
    }
    const otherSt = Number(other.start_u) || 1
    const otherH = Number(other.u_height) || 1
    const otherEd = otherSt + otherH - 1

    if (Math.max(st, otherSt) <= Math.min(ed, otherEd)) {
      const otherRange = otherH > 1 ? `U${otherSt}~U${otherEd}` : `U${otherSt}`
      return {
        valid: false,
        reason: `槽位冲突: 与既有在架设备 ${other.asset_no} (${otherRange}) 重叠`,
      }
    }
  }

  const placeRange = h > 1 ? `U${st}~U${ed}` : `U${st}`
  return {
    valid: true,
    reason: `可放置: ${placeRange} (${h}U)`,
  }
}

function onSlotHover(e, rack, slotU) {
  if (!draggedAsset.value) return
  e.preventDefault()
  e.stopPropagation()

  hoverRackId.value = rack.rack_id
  hoverStartU.value = slotU

  const check = checkPlacement(rack, slotU, draggedHeight.value, draggedAsset.value?.id)
  hoverValid.value = check.valid
  hoverReason.value = check.reason

  e.dataTransfer.dropEffect = check.valid ? 'move' : 'none'
}

function handleGridDragOver(e, rack) {
  if (!draggedAsset.value) return
  e.preventDefault()

  const gridEl = e.currentTarget
  const rect = gridEl.getBoundingClientRect()
  const offsetY = e.clientY - rect.top
  const percentage = Math.max(0, Math.min(1, offsetY / rect.height))
  const rowFromTop = Math.floor(percentage * 42)
  let u = 42 - rowFromTop
  u = Math.max(1, Math.min(42, u))

  hoverRackId.value = rack.rack_id
  hoverStartU.value = u

  const check = checkPlacement(rack, u, draggedHeight.value, draggedAsset.value?.id)
  hoverValid.value = check.valid
  hoverReason.value = check.reason

  e.dataTransfer.dropEffect = check.valid ? 'move' : 'none'
}

function handleRackDragLeave(e, rack) {
  if (!e.currentTarget.contains(e.relatedTarget)) {
    if (hoverRackId.value === rack.rack_id) {
      hoverRackId.value = null
      hoverStartU.value = null
      hoverValid.value = false
      hoverReason.value = ''
    }
  }
}

async function handleGridDrop(e, rack) {
  if (!draggedAsset.value || isSubmittingDrop.value) return
  e.preventDefault()
  e.stopPropagation()

  const targetU = hoverStartU.value
  if (targetU === null || targetU === undefined || targetU < 1 || targetU > 42) {
    onDragEnd()
    return
  }

  const h = draggedHeight.value
  const asset = draggedAsset.value
  const isSourceSame = draggedSourceRack.value?.rack_id === rack.rack_id && Number(asset.start_u) === Number(targetU)

  if (isSourceSame) {
    onDragEnd()
    return
  }

  const check = checkPlacement(rack, targetU, h, asset.id)
  if (!check.valid) {
    showToast(check.reason, 'error')
    onDragEnd()
    return
  }

  // 计算目标规范位置与所属机房
  const roomNum = rack.room_code.replace('ROOM-', '')
  const newLocation = `实训楼${roomNum}-${rack.rack_id}-U${targetU}(${h}U)`

  let newExtraParams = {}
  if (asset.detail?.extra_params) {
    try {
      newExtraParams = JSON.parse(asset.detail.extra_params)
    } catch (err) {}
  }
  newExtraParams.start_u = targetU
  newExtraParams.u_height = h
  newExtraParams.rack_units = `${h}U`

  isSubmittingDrop.value = true
  try {
    await api.updateAsset(asset.id, {
      location: newLocation,
      detail: {
        extra_params: JSON.stringify(newExtraParams),
      },
    })

    await loadTopology()
    const placeRange = h > 1 ? `U${targetU}~U${targetU + h - 1}` : `U${targetU}`
    showToast(`设备 ${asset.asset_no} 已成功调拨至 ${rack.rack_id} (${placeRange})`, 'success')
    emit('refresh')
  } catch (err) {
    showToast(`调拨失败: ${err.message || '网络或接口异常'}`, 'error')
  } finally {
    isSubmittingDrop.value = false
    onDragEnd()
  }
}

// 点击设备插槽向外派发事件
function onAssetClick(asset) {
  if (hasDragged) return
  emit('inspectAsset', asset)
}

// 设备槽位整体双模态高颜值样式 (明亮模式告别暗沉，高对比晶透报警红)
function deviceSlotClass(asset) {
  const isL = isLight.value
  const status = asset.health_status
  if (isL) {
    switch (status) {
      case 'OVERHEAT':
        return 'bg-gradient-to-r from-rose-100/95 via-red-50 to-rose-100/90 border-2 border-rose-400 shadow-[0_2px_12px_rgba(244,63,94,0.22)] hover:border-rose-500 hover:bg-rose-100'
      case 'WARNING':
        return 'bg-gradient-to-r from-amber-100/90 via-orange-50 to-amber-50 border-2 border-amber-400 shadow-[0_2px_10px_rgba(245,158,11,0.18)] hover:border-amber-500 hover:bg-amber-100/90'
      case 'OFFLINE':
        return 'bg-slate-100 border-2 border-slate-300 opacity-60'
      default:
        return 'bg-gradient-to-r from-sky-50 via-cyan-50 to-slate-50 border-2 border-cyan-400/80 shadow-[0_2px_8px_rgba(6,182,212,0.15)] hover:border-cyan-500 hover:bg-cyan-50'
    }
  }

  // 暗黑模式
  switch (status) {
    case 'OVERHEAT':
      return 'bg-rose-950/70 border-rose-500/70 hover:border-rose-400 hover:bg-rose-900/80 shadow-rose-950/40'
    case 'WARNING':
      return 'bg-amber-950/60 border-amber-500/60 hover:border-amber-400 hover:bg-amber-900/70 shadow-amber-950/30'
    case 'OFFLINE':
      return 'bg-zinc-900 border-zinc-700 hover:border-zinc-500 opacity-60'
    default:
      return 'bg-zinc-900/90 border-cyan-500/40 hover:border-cyan-400 hover:bg-zinc-800/90 shadow-cyan-950/30'
  }
}

// 指示灯动态样式 (明亮模式增加外发光环与高对比色阶)
function ledClass(status) {
  const isL = isLight.value
  if (isL) {
    switch (status) {
      case 'OVERHEAT':
        return 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.95)] animate-pulse ring-2 ring-rose-300'
      case 'WARNING':
        return 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.95)] animate-pulse ring-2 ring-amber-300'
      case 'OFFLINE':
        return 'bg-slate-400'
      default:
        return 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.9)] ring-2 ring-emerald-300'
    }
  }

  switch (status) {
    case 'OVERHEAT':
      return 'bg-rose-500 shadow-[0_0_6px_rgba(244,63,94,0.9)] animate-pulse'
    case 'WARNING':
      return 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.9)] animate-pulse'
    case 'OFFLINE':
      return 'bg-zinc-600'
    default:
      return 'bg-emerald-400 shadow-[0_0_5px_rgba(52,211,153,0.8)]'
  }
}

// 状态徽章动态样式 (明亮模式下采用高辨识度白字鲜艳彩底)
function healthBadgeClass(status) {
  const isL = isLight.value
  if (isL) {
    switch (status) {
      case 'OVERHEAT':
        return 'bg-rose-500 text-white font-bold border border-rose-600 shadow-sm'
      case 'WARNING':
        return 'bg-amber-500 text-white font-bold border border-amber-600 shadow-sm'
      case 'OFFLINE':
        return 'bg-slate-200 text-slate-700 border border-slate-300'
      default:
        return 'bg-emerald-500 text-white font-bold border border-emerald-600 shadow-sm'
    }
  }

  switch (status) {
    case 'OVERHEAT':
      return 'bg-rose-500/15 border-rose-500/30 text-rose-300 font-semibold'
    case 'WARNING':
      return 'bg-amber-500/15 border-amber-500/30 text-amber-300'
    case 'OFFLINE':
      return 'bg-zinc-800 border-zinc-700 text-zinc-400'
    default:
      return 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
  }
}

// 允许父级组件直接唤醒拓扑刷新
defineExpose({
  loadTopology,
})
</script>

<style scoped>
/* 逼真金属机架与槽位微质感 */
.rack-cabinet-wrapper {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.rack-device-slot {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12), 0 2px 4px rgba(0, 0, 0, 0.4);
}

.free-u-slot {
  background-image: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 4px,
    rgba(255, 255, 255, 0.015) 4px,
    rgba(255, 255, 255, 0.015) 8px
  );
}

/* 明亮模态色彩细腻适配 */
:global(html.light) .rack-cabinet-wrapper {
  background-color: rgba(248, 250, 252, 0.95);
  border-color: rgba(203, 213, 225, 0.9);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.03);
}

:global(html.light) .rack-cabinet-header {
  background-color: rgba(241, 245, 249, 0.98);
  border-color: rgba(226, 232, 240, 1);
}

:global(html.light) .rack-cabinet-body {
  background-color: rgba(248, 250, 252, 0.95) !important;
  border-color: rgba(203, 213, 225, 0.8) !important;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.04);
}

:global(html.light) .rack-device-slot {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.85);
}

:global(html.light) .free-u-slot {
  background-image: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 4px,
    rgba(0, 0, 0, 0.02) 4px,
    rgba(0, 0, 0, 0.02) 8px
  );
}

:global(html.light) .unracked-card {
  background-color: rgba(255, 255, 255, 0.95);
  border-color: rgba(226, 232, 240, 0.9);
}

:global(html.light) .unracked-card:hover {
  border-color: rgba(168, 85, 247, 0.5);
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.1);
}
</style>
