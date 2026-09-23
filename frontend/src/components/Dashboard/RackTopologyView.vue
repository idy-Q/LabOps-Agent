<template>
  <div class="space-y-4">
    <!-- 1. 顶部控制栏：机房切换器与实时同步控制 -->
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 rounded-2xl glass-card border"
      :class="isLight ? 'bg-white/80 border-slate-200 shadow-sm' : ''"
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
          </div>
          <p class="text-xs mt-0.5" :class="isLight ? 'text-slate-500' : 'text-zinc-400'">
            {{ activeRoomTitle }} · 42U 标准工业级机架槽位与配套设施
          </p>
        </div>
      </div>

      <!-- 机房切换器 Segmented Controls -->
      <div
        class="flex items-center space-x-1 p-1 rounded-xl border shadow-sm text-xs self-start sm:self-auto overflow-x-auto max-w-full"
        :class="isLight ? 'bg-slate-100/90 border-slate-200' : 'bg-zinc-900/90 border-white/[0.08]'"
      >
        <button
          @click="selectedRoomCode = 'ALL'"
          :class="[
            'px-2.5 py-1 rounded-lg font-medium transition-all whitespace-nowrap',
            selectedRoomCode === 'ALL'
              ? 'bg-emerald-600 text-white shadow-sm border border-emerald-400/40'
              : (isLight ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50')
          ]"
        >
          全部机房 ({{ activeTotalRacks }}柜/{{ activeTotalAssets }}设备)
        </button>

        <button
          v-for="room in topologyData?.rooms || []"
          :key="room.room_code"
          @click="selectedRoomCode = room.room_code"
          :class="[
            'px-2.5 py-1 rounded-lg font-medium transition-all whitespace-nowrap flex items-center space-x-1.5',
            selectedRoomCode === room.room_code
              ? 'bg-emerald-600 text-white shadow-sm border border-emerald-400/40'
              : (isLight ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/70' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50')
          ]"
        >
          <span>{{ room.room_code.replace('ROOM-', '') }} {{ room.total_racks === 0 ? '库房' : '机房' }}</span>
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
        </button>

        <button
          @click="loadTopology"
          :disabled="loading"
          class="p-1.5 rounded-lg transition-colors ml-1"
          :class="isLight ? 'text-slate-500 hover:text-slate-800 hover:bg-slate-200/70' : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800'"
          title="刷新机柜拓扑数据"
        >
          <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 2. 当前选中机房元信息说明条 (当选中单间机房时呈现) -->
    <div
      v-if="currentRoom"
      class="px-4 py-2.5 rounded-xl border text-xs flex flex-wrap items-center justify-between gap-3"
      :class="isLight ? 'bg-slate-100/90 border-slate-200 text-slate-600' : 'bg-zinc-900/50 border-white/[0.06] text-zinc-400'"
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
      </div>
    </div>

    <!-- 3. 大盘总览指标 5 磁贴 Bento Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      <!-- 磁贴 1: 机柜总数 -->
      <div
        class="p-3.5 rounded-2xl glass-card border flex flex-col justify-between"
        :class="isLight ? 'bg-white/80 border-slate-200/80 shadow-xs' : ''"
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
        :class="isLight ? 'bg-white/80 border-slate-200/80 shadow-xs' : ''"
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
        :class="isLight ? 'bg-white/80 border-slate-200/80 shadow-xs' : ''"
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
        :class="isLight ? 'bg-white/80 border-slate-200/80 shadow-xs' : ''"
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
        :class="isLight ? 'bg-white/80 border-slate-200/80 shadow-xs' : ''"
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
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="w-1.5 h-3.5 rounded-full bg-emerald-500"></span>
          <h4 class="text-xs sm:text-sm font-semibold text-zinc-200">
            {{ selectedRoomCode === 'ALL' ? '全机房标准机架阵列 (42U)' : `${currentRoom?.room_name} 机架阵列` }}
          </h4>
          <span class="text-xs text-zinc-500">
            共 {{ displayedRacks.length }} 台机柜
          </span>
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
            rack.health_status === 'OVERHEAT'
              ? (isLight ? 'border-rose-300/90 bg-rose-50/40 shadow-rose-200/50' : 'border-rose-500/40 bg-rose-950/10 shadow-rose-950/20')
              : rack.health_status === 'WARNING'
                ? (isLight ? 'border-amber-300/90 bg-amber-50/40 shadow-amber-200/50' : 'border-amber-500/30 bg-amber-950/10 shadow-amber-950/20')
                : (isLight ? 'border-slate-200 bg-white/95 shadow-slate-200/60' : 'border-white/[0.1] bg-zinc-950/70 shadow-black/40')
          ]"
        >
          <!-- 机柜顶部控制门楣与铭牌 (通解架构：温度与机房位置对调，彻底杜绝任何字元溢出) -->
          <div
            class="rack-cabinet-header rounded-xl px-2.5 py-2 mb-2.5 border flex flex-col justify-between space-y-1.5 shadow-inner shrink-0 overflow-hidden"
            :class="isLight ? 'border-slate-200 bg-slate-100/90' : 'border-white/[0.08] bg-zinc-900/90'"
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

              <!-- 所属机房编号标签 (对调至第一行右上角，稳固展示) -->
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
              class="flex-1 grid grid-cols-1 gap-[1px] px-1 overflow-hidden"
              style="grid-template-rows: repeat(42, minmax(0, 1fr)); height: 460px;"
            >
              <!-- 渲染在架设备 (按 row-start 与 row-span 绝对跨越) -->
              <div
                v-for="asset in rack.assets"
                :key="asset.id"
                @click="onAssetClick(asset)"
                class="rack-device-slot group cursor-pointer relative rounded flex flex-col justify-center px-1.5 py-0.5 transition-all active:scale-[0.99] select-none shadow-md overflow-hidden"
                :style="{
                  gridRowStart: getRowStart(asset.start_u, asset.u_height),
                  gridRowEnd: `span ${asset.u_height}`,
                }"
                :class="deviceSlotClass(asset)"
                :title="`点击查看设备全景档案: ${asset.name} (${asset.asset_no}) - 槽位 U${asset.start_u}~U${asset.start_u + asset.u_height - 1} (${asset.u_height}U)`"
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
          点击任意卡片查看详细硬件物理规格参数
        </span>
      </div>

      <!-- 非机架外设资产网格：优化响应式断点与 min-w-0 保护，杜绝窄屏挤压 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-3.5">
        <div
          v-for="asset in displayedUnrackedAssets"
          :key="asset.id"
          @click="onAssetClick(asset)"
          class="unracked-card p-3.5 rounded-xl border glass-card hover:border-purple-400/40 transition-all cursor-pointer flex flex-col justify-between space-y-2.5 group shadow-sm active:scale-[0.99] min-w-0 overflow-hidden"
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

            <!-- 健康胶囊：强制 shrink-0 与 whitespace-nowrap，内嵌呼吸微标点，杜绝溢出截断 -->
            <span
              class="text-[9px] px-2 py-0.5 rounded-full border font-mono shrink-0 whitespace-nowrap flex items-center gap-1 shadow-sm"
              :class="healthBadgeClass(asset.health_status)"
            >
              <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="ledClass(asset.health_status)"></span>
              <span>{{ asset.health_status }}</span>
            </span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  theme: {
    type: String,
    default: 'dark',
  },
})

const emit = defineEmits(['inspectAsset', 'refresh'])

// 主题动态感知 (双重判定：props 优先，fallback 到 html 根类)
const isLight = computed(() => {
  return props.theme === 'light' || (typeof document !== 'undefined' && document.documentElement.classList.contains('light'))
})

// 状态定义
const loading = ref(false)
const topologyData = ref(null)
const selectedRoomCode = ref('ALL') // 'ALL' 或 'ROOM-201', 'ROOM-101', 'ROOM-301'

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

// 点击设备插槽向外派发事件
function onAssetClick(asset) {
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
