<template>
  <div class="space-y-3.5">
    <!-- 顶部状态栏与刷新控制 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-indigo-400">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-medium text-zinc-100">全景态势控制台</h3>
        <span class="flex h-1.5 w-1.5 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-400"></span>
        </span>
      </div>

      <div class="flex items-center space-x-2">
        <button
          @click="$emit('refresh')"
          class="text-zinc-400 hover:text-zinc-200 text-xs flex items-center space-x-1.5 transition-all px-2.5 py-1 rounded-md bg-zinc-900/90 hover:bg-zinc-800 border border-white/[0.08] hover:border-white/[0.15] active:scale-95 shadow-sm"
          title="刷新大盘指标"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span>实时同步</span>
        </button>
      </div>
    </div>

    <!-- 1. 顶部 4 大核心 KPI 磁贴卡片 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5">
      <!-- KPI 1: 平均温度 -->
      <div class="p-3.5 rounded-xl glass-card border hover:border-white/[0.22] transition-all duration-200 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-zinc-400">
          <span class="text-[11px] glass-text">环境均温</span>
          <svg class="w-3.5 h-3.5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div class="flex items-baseline space-x-1.5 my-1.5">
          <span
            :class="[
              'text-2xl font-semibold font-mono tracking-tight glass-text',
              avgTemp > 40 ? 'text-rose-400 animate-pulse' : avgTemp > 35 ? 'text-amber-400' : 'text-zinc-100'
            ]"
          >
            {{ avgTemp }}
          </span>
          <span class="text-xs text-zinc-500 font-mono">℃</span>
        </div>
        <div class="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-white/[0.04] font-mono">
          <span>红线: 40℃</span>
          <span :class="avgTemp > 40 ? 'text-rose-400 font-medium' : 'text-emerald-400'">
            {{ avgTemp > 40 ? '超温触发提单' : '温控状态平稳' }}
          </span>
        </div>
      </div>

      <!-- KPI 2: 算力集群均载 -->
      <div class="p-3.5 rounded-xl glass-card border hover:border-white/[0.22] transition-all duration-200 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-zinc-400">
          <span class="text-[11px] glass-text">算力集群均载</span>
          <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
        <div class="flex items-baseline space-x-1.5 my-1.5">
          <span class="text-2xl font-semibold font-mono tracking-tight text-zinc-100 glass-text">{{ avgCpu }}</span>
          <span class="text-xs text-zinc-500 font-mono">%</span>
        </div>
        <!-- 负载微型进度条 -->
        <div class="w-full bg-zinc-800/80 rounded-full h-1.5 overflow-hidden">
          <div
            class="bg-cyan-400 h-1.5 rounded-full transition-all duration-500"
            :style="{ width: `${Math.min(avgCpu, 100)}%` }"
          ></div>
        </div>
      </div>

      <!-- KPI 3: 实时供电动力负荷 -->
      <div class="p-3.5 rounded-xl glass-card border hover:border-white/[0.22] transition-all duration-200 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-zinc-400">
          <span class="text-[11px] glass-text">供电动力负荷</span>
          <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div class="flex items-baseline space-x-1.5 my-1.5">
          <span class="text-2xl font-semibold font-mono tracking-tight text-zinc-100 glass-text">{{ totalPower }}</span>
          <span class="text-xs text-zinc-500 font-mono">W</span>
        </div>
        <div class="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-white/[0.04] font-mono">
          <span>额定: 4500W</span>
          <span class="text-zinc-400">{{ Math.round((totalPower / 4500) * 100) }}% 载荷</span>
        </div>
      </div>

      <!-- KPI 4: 设备健康率 -->
      <div class="p-3.5 rounded-xl glass-card border hover:border-white/[0.22] transition-all duration-200 shadow-sm flex flex-col justify-between">
        <div class="flex items-center justify-between text-zinc-400">
          <span class="text-[11px] glass-text">设备健康率</span>
          <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div class="flex items-baseline space-x-1.5 my-1.5">
          <span class="text-2xl font-semibold font-mono tracking-tight text-emerald-400 glass-text">{{ healthRate }}</span>
          <span class="text-xs text-zinc-500 font-mono">%</span>
        </div>
        <div class="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-white/[0.04] font-mono">
          <span>在册: {{ totalAssetsCount }} 台</span>
          <span :class="alertsCount > 0 ? 'text-amber-400' : 'text-zinc-500'">
            {{ alertsCount }} 条告警
          </span>
        </div>
      </div>
    </div>

    <!-- 2. 中层 Bento: 设备健康分布环图 (5 Cols) + 最新工单事件快照 (7 Cols) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5">
      <!-- 左磁贴：纯原生 SVG 设备健康度圆环分布图 (5 Cols) -->
      <div class="lg:col-span-5 rounded-xl glass-card border p-4 flex flex-col justify-between shadow-sm">
        <div class="flex items-center justify-between pb-2 border-b border-white/[0.06]">
          <div class="flex items-center space-x-2">
            <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-emerald-400">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
              </svg>
            </span>
            <span class="text-xs font-medium text-zinc-200">资产健康与运行分布</span>
          </div>
          <button
            @click="$emit('switchTab', 'assets')"
            class="text-[11px] text-zinc-400 hover:text-zinc-200 flex items-center space-x-1 transition-colors"
          >
            <span>台账明细</span>
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- 纯 SVG Donut Chart -->
        <div class="py-3 flex flex-col sm:flex-row items-center justify-around gap-4">
          <div class="relative w-32 h-32 flex items-center justify-center shrink-0">
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <!-- 底环 -->
              <circle
                cx="50"
                cy="50"
                r="38"
                stroke="currentColor"
                stroke-width="11"
                fill="transparent"
                class="text-zinc-800/60"
              />
              <!-- 正常 HEALTHY (Emerald) -->
              <circle
                v-if="chartData.healthyLength > 0"
                cx="50"
                cy="50"
                r="38"
                stroke="#10B981"
                stroke-width="11"
                fill="transparent"
                :stroke-dasharray="`${chartData.healthyLength} ${chartData.circumference - chartData.healthyLength}`"
                :stroke-dashoffset="chartData.healthyOffset"
                class="transition-all duration-700 ease-out"
              />
              <!-- 预警 WARNING (Amber) -->
              <circle
                v-if="chartData.warningLength > 0"
                cx="50"
                cy="50"
                r="38"
                stroke="#F59E0B"
                stroke-width="11"
                fill="transparent"
                :stroke-dasharray="`${chartData.warningLength} ${chartData.circumference - chartData.warningLength}`"
                :stroke-dashoffset="chartData.warningOffset"
                class="transition-all duration-700 ease-out"
              />
              <!-- 超温 OVERHEAT (Rose) -->
              <circle
                v-if="chartData.overheatLength > 0"
                cx="50"
                cy="50"
                r="38"
                stroke="#F43F5E"
                stroke-width="11"
                fill="transparent"
                :stroke-dasharray="`${chartData.overheatLength} ${chartData.circumference - chartData.overheatLength}`"
                :stroke-dashoffset="chartData.overheatOffset"
                class="transition-all duration-700 ease-out"
              />
              <!-- 离线 OFFLINE (Zinc) -->
              <circle
                v-if="chartData.offlineLength > 0"
                cx="50"
                cy="50"
                r="38"
                stroke="#71717A"
                stroke-width="11"
                fill="transparent"
                :stroke-dasharray="`${chartData.offlineLength} ${chartData.circumference - chartData.offlineLength}`"
                :stroke-dashoffset="chartData.offlineOffset"
                class="transition-all duration-700 ease-out"
              />
            </svg>
            <!-- 环中心文字 -->
            <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span class="text-xl font-bold font-mono text-zinc-100">{{ totalAssetsCount }}</span>
              <span class="text-[9px] text-zinc-500 uppercase tracking-wider">总设备数</span>
            </div>
          </div>

          <!-- 图例清单 -->
          <div class="space-y-2 text-xs flex-1 max-w-[180px]">
            <div class="flex items-center justify-between text-zinc-300">
              <span class="flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>正常运行</span>
              </span>
              <span class="font-mono text-[11px] text-zinc-400">{{ healthyCount }} ({{ chartData.healthyPct }}%)</span>
            </div>
            <div class="flex items-center justify-between text-zinc-300">
              <span class="flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                <span>异常预警</span>
              </span>
              <span class="font-mono text-[11px] text-zinc-400">{{ warningCount }} ({{ chartData.warningPct }}%)</span>
            </div>
            <div class="flex items-center justify-between text-zinc-300">
              <span class="flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-rose-400"></span>
                <span>超温高温</span>
              </span>
              <span class="font-mono text-[11px] text-rose-400">{{ overheatCount }} ({{ chartData.overheatPct }}%)</span>
            </div>
            <div class="flex items-center justify-between text-zinc-300">
              <span class="flex items-center space-x-1.5">
                <span class="w-2 h-2 rounded-full bg-zinc-500"></span>
                <span>脱网离线</span>
              </span>
              <span class="font-mono text-[11px] text-zinc-500">{{ offlineCount }} ({{ chartData.offlinePct }}%)</span>
            </div>
          </div>
        </div>

        <div class="pt-2 border-t border-white/[0.04] flex items-center justify-between text-[11px] text-zinc-500">
          <span>在用借调: {{ inUseCount }} 台</span>
          <span class="text-zinc-400">可用空闲: {{ totalAssetsCount - inUseCount }} 台</span>
        </div>
      </div>

      <!-- 右磁贴：最新运维工单与事件流快照 (7 Cols) -->
      <div class="lg:col-span-7 rounded-xl glass-card border p-4 flex flex-col justify-between shadow-sm">
        <div class="flex items-center justify-between pb-2 border-b border-white/[0.06]">
          <div class="flex items-center space-x-2">
            <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-amber-400">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <span class="text-xs font-medium text-zinc-200 glass-text">最新工单事件快照流</span>
            <span class="px-2 py-0.5 rounded-md bg-zinc-900/80 border border-white/[0.06] text-[10px] text-zinc-400 font-mono">
              待处理 {{ pendingTicketsCount }}
            </span>
          </div>

          <button
            @click="$emit('switchTab', 'tickets')"
            class="text-[11px] text-zinc-400 hover:text-zinc-200 flex items-center space-x-1 transition-colors"
          >
            <span>全部工单</span>
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- 工单快照列表 -->
        <div class="py-2 space-y-2 flex-1 overflow-y-auto max-h-52">
          <div v-if="recentTickets.length === 0" class="py-8 text-center text-zinc-500 text-xs">
            暂无历史工单流转记录
          </div>
          <div
            v-for="ticket in recentTickets"
            :key="ticket.id"
            @click="handleTicketClick(ticket.ticket_no)"
            :class="[
              'p-2.5 rounded-lg border transition-all cursor-pointer flex items-center justify-between text-xs',
              ticket.ticket_no === highlightedTicketNo
                ? 'bg-amber-950/30 border-amber-500/40 ring-1 ring-amber-500/30 animate-pulse-ticket font-medium text-amber-200'
                : 'glass-card-sub hover:bg-white/[0.08] border-white/[0.06] hover:border-white/[0.14]'
            ]"
          >
            <div class="space-y-1 min-w-0 pr-2">
              <div class="flex items-center space-x-2">
                <span class="font-mono text-zinc-300 font-medium text-[11px]">{{ ticket.ticket_no }}</span>
                <span :class="['px-1.5 py-0.5 rounded text-[9px] font-mono', priorityClass(ticket.priority)]">
                  {{ ticket.priority }}
                </span>
                <span :class="['px-1.5 py-0.5 rounded text-[9px] font-mono', statusClass(ticket.status)]">
                  {{ ticket.status }}
                </span>
              </div>
              <p class="text-zinc-300 text-xs truncate max-w-sm font-sans">{{ ticket.title }}</p>
            </div>

            <div class="text-right shrink-0">
              <span class="text-[10px] text-zinc-500 font-mono block">{{ ticket.device_id || '通用事件' }}</span>
              <span class="text-[10px] text-emerald-400/80 hover:text-emerald-300 underline cursor-pointer">
                去处理 →
              </span>
            </div>
          </div>
        </div>

        <div class="pt-2 border-t border-white/[0.04] flex items-center justify-between text-[11px] text-zinc-500">
          <span>点击任意事件卡片可直接在对话流中发起排查</span>
          <span class="font-mono">Total: {{ tickets.length }}</span>
        </div>
      </div>
    </div>

    <!-- 3. 下层 Bento: 重点感知节点硬件探针 (8 Cols) + 高频运维快捷通道 (4 Cols) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5">
      <!-- 硬件探针节点 (8 Cols) -->
      <div class="lg:col-span-8 rounded-xl glass-card border p-4 space-y-3 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-cyan-400">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
            </span>
            <span class="text-xs font-medium text-zinc-200 glass-text">核心算力与通信节点探针</span>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div
            v-for="node in nodes"
            :key="node.device_id"
            @click="$emit('inspectDevice', node.device_id)"
            class="p-3 rounded-lg glass-card-sub hover:bg-white/[0.08] border border-white/[0.06] hover:border-cyan-500/30 cursor-pointer transition-all space-y-2 group shadow-sm"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-1.5">
                <span class="font-mono text-xs font-medium text-zinc-200 group-hover:text-cyan-400 transition-colors">
                  {{ node.device_id }}
                </span>
                <span :class="['px-1.5 py-0.5 rounded text-[9px] font-mono', statusBadgeClass(node.health_status)]">
                  {{ node.health_status }}
                </span>
              </div>
              <span class="text-[10px] text-zinc-500 truncate max-w-[120px] font-mono">{{ node.location }}</span>
            </div>

            <div class="flex items-center justify-between text-[11px] font-mono text-zinc-400">
              <span>
                温度:
                <strong :class="node.temperature > 40 ? 'text-rose-400 font-medium' : node.temperature > 35 ? 'text-amber-400 font-medium' : 'text-emerald-400 font-medium'">
                  {{ node.temperature }}℃
                </strong>
              </span>
              <span>CPU: {{ node.cpu_usage }}%</span>
              <span>风扇: {{ node.fan_speed_rpm }} RPM</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷运维通道 (4 Cols) -->
      <div class="lg:col-span-4 rounded-xl glass-card border p-4 flex flex-col justify-between space-y-3 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-indigo-400">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </span>
            <span class="text-xs font-medium text-zinc-200 glass-text">快捷运维入口</span>
          </div>
        </div>

        <div class="space-y-2 flex-1 flex flex-col justify-center">
          <button
            @click="$emit('quickAction', '一键巡检当前机房全部资产设备，若存在超温或警告请自动提单')"
            class="w-full text-left p-2.5 rounded-lg glass-card-sub hover:bg-emerald-500/10 border border-white/[0.06] hover:border-emerald-500/30 transition-all text-xs text-zinc-300 hover:text-white flex items-center justify-between group active:scale-95 shadow-sm"
          >
            <div class="flex items-center space-x-2">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span class="font-medium">一键全盘健康巡检</span>
            </div>
            <svg class="w-3.5 h-3.5 text-zinc-500 group-hover:text-emerald-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>

          <button
            @click="$emit('quickAction', '查询当前处于 WARNING 或 OVERHEAT 异常状态的硬件，并根据机房规范输出处置建议')"
            class="w-full text-left p-2.5 rounded-lg glass-card-sub hover:bg-amber-500/10 border border-white/[0.06] hover:border-amber-500/30 transition-all text-xs text-zinc-300 hover:text-white flex items-center justify-between group active:scale-95 shadow-sm"
          >
            <div class="flex items-center space-x-2">
              <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
              <span class="font-medium">排查告警与超温节点</span>
            </div>
            <svg class="w-3.5 h-3.5 text-zinc-500 group-hover:text-amber-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>

          <button
            @click="$emit('quickAction', '检索机房用电安全和机柜额定功耗限制规范，说明红线阈值')"
            class="w-full text-left p-2.5 rounded-lg glass-card-sub hover:bg-indigo-500/10 border border-white/[0.06] hover:border-indigo-500/30 transition-all text-xs text-zinc-300 hover:text-white flex items-center justify-between group active:scale-95 shadow-sm"
          >
            <div class="flex items-center space-x-2">
              <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
              <span class="font-medium">溯源检索用电与功耗规章</span>
            </div>
            <svg class="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        </div>

        <div class="pt-2 border-t border-white/[0.04] text-[10px] text-zinc-500 flex items-center justify-between">
          <span>点击即可直接由智能管家执行</span>
          <span class="text-emerald-400">Ready</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  metrics: {
    type: Object,
    default: () => ({}),
  },
  tickets: {
    type: Array,
    default: () => [],
  },
  assets: {
    type: Array,
    default: () => [],
  },
  highlightedTicketNo: {
    type: String,
    default: '',
  },
  highlightedAssetNo: {
    type: String,
    default: '',
  },
})

const emit = defineEmits([
  'refresh',
  'switchTab',
  'inspectDevice',
  'inspectTicket',
  'inspectAsset',
  'quickAction',
])

// 1. 指标计算
const overview = computed(() => props.metrics?.overview || {})
const avgTemp = computed(() => overview.value.avg_temperature || 24.5)
const avgCpu = computed(() => overview.value.avg_cpu_load || 35.0)
const totalPower = computed(() => overview.value.total_power_watts || 1200)
const healthRate = computed(() => overview.value.system_health_rate || 100)
const alertsCount = computed(() => overview.value.active_alerts_count || 0)
const nodes = computed(() => props.metrics?.nodes || [])

// 2. 资产统计与 Donut Chart
const totalAssetsCount = computed(() => props.assets.length)
const healthyCount = computed(() => props.assets.filter((a) => a.health_status === 'HEALTHY').length)
const warningCount = computed(() => props.assets.filter((a) => a.health_status === 'WARNING').length)
const overheatCount = computed(() => props.assets.filter((a) => a.health_status === 'OVERHEAT').length)
const offlineCount = computed(() => props.assets.filter((a) => a.health_status === 'OFFLINE').length)
const inUseCount = computed(() => props.assets.filter((a) => a.borrow_status === 'IN_USE').length)

const chartData = computed(() => {
  const total = props.assets.length
  const r = 38
  const circumference = 2 * Math.PI * r // ~238.76

  if (total === 0) {
    return {
      circumference,
      healthyLength: 0,
      warningLength: 0,
      overheatLength: 0,
      offlineLength: 0,
      healthyOffset: 0,
      warningOffset: 0,
      overheatOffset: 0,
      offlineOffset: 0,
      healthyPct: 0,
      warningPct: 0,
      overheatPct: 0,
      offlinePct: 0,
    }
  }

  const hRatio = healthyCount.value / total
  const wRatio = warningCount.value / total
  const oRatio = overheatCount.value / total
  const fRatio = offlineCount.value / total

  const healthyLength = hRatio * circumference
  const warningLength = wRatio * circumference
  const overheatLength = oRatio * circumference
  const offlineLength = fRatio * circumference

  // 累积偏移量（圆周负方向）
  const healthyOffset = 0
  const warningOffset = -healthyLength
  const overheatOffset = -(healthyLength + warningLength)
  const offlineOffset = -(healthyLength + warningLength + overheatLength)

  return {
    circumference,
    healthyLength,
    warningLength,
    overheatLength,
    offlineLength,
    healthyOffset,
    warningOffset,
    overheatOffset,
    offlineOffset,
    healthyPct: Math.round(hRatio * 100),
    warningPct: Math.round(wRatio * 100),
    overheatPct: Math.round(oRatio * 100),
    offlinePct: Math.round(fRatio * 100),
  }
})

// 3. 最新工单快照
const recentTickets = computed(() => props.tickets.slice(0, 4))
const pendingTicketsCount = computed(() => props.tickets.filter((t) => t.status === 'PENDING').length)

function handleTicketClick(ticketNo) {
  emit('switchTab', 'tickets')
  emit('inspectTicket', ticketNo)
}

function priorityClass(priority) {
  switch (priority) {
    case 'CRITICAL':
      return 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
    case 'HIGH':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'MEDIUM':
      return 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
    case 'LOW':
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}

function statusClass(status) {
  switch (status) {
    case 'PENDING':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'PROCESSING':
      return 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
    case 'RESOLVED':
      return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
    case 'CLOSED':
      return 'bg-zinc-800 text-zinc-500 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}

function statusBadgeClass(status) {
  switch (status) {
    case 'HEALTHY':
      return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
    case 'WARNING':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'OVERHEAT':
      return 'bg-rose-500/10 text-rose-400 border border-rose-500/20 animate-pulse font-medium'
    case 'OFFLINE':
      return 'bg-zinc-800 text-zinc-500 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}
</script>
