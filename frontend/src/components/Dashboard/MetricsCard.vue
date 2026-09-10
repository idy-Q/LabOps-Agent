<template>
  <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-4 space-y-4 shadow-sm">
    <!-- 头部栏 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-semibold text-slate-100">机房实时运行健康态势</h3>
        <span class="flex h-2 w-2 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
      </div>

      <button
        @click="$emit('refresh')"
        class="text-slate-400 hover:text-emerald-400 text-xs flex items-center space-x-1 transition-colors p-1 rounded-lg hover:bg-slate-800"
        title="刷新大盘指标"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>刷新</span>
      </button>
    </div>

    <!-- 四大核心 KPI 指标卡片 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
      <!-- 1. 机房均温 -->
      <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50 flex flex-col justify-between">
        <span class="text-[11px] text-slate-400">平均核心温度</span>
        <div class="flex items-baseline space-x-1 mt-1">
          <span
            :class="[
              'text-lg font-bold font-mono',
              avgTemp > 40 ? 'text-rose-400' : avgTemp > 35 ? 'text-amber-400' : 'text-emerald-400'
            ]"
          >
            {{ avgTemp }}
          </span>
          <span class="text-xs text-slate-400">℃</span>
        </div>
        <span class="text-[10px] text-slate-500 mt-1">阈值红线: 40℃</span>
      </div>

      <!-- 2. CPU 平均负载 -->
      <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50 flex flex-col justify-between">
        <span class="text-[11px] text-slate-400">算力节点均载</span>
        <div class="flex items-baseline space-x-1 mt-1">
          <span class="text-lg font-bold font-mono text-cyan-400">{{ avgCpu }}</span>
          <span class="text-xs text-slate-400">%</span>
        </div>
        <span class="text-[10px] text-slate-500 mt-1">运算集群负载</span>
      </div>

      <!-- 3. 总功耗负荷 -->
      <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50 flex flex-col justify-between">
        <span class="text-[11px] text-slate-400">实时动力功耗</span>
        <div class="flex items-baseline space-x-1 mt-1">
          <span class="text-lg font-bold font-mono text-amber-300">{{ totalPower }}</span>
          <span class="text-xs text-slate-400">W</span>
        </div>
        <span class="text-[10px] text-slate-500 mt-1">单柜上限: 4.5kW</span>
      </div>

      <!-- 4. 系统健康率 -->
      <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/50 flex flex-col justify-between">
        <span class="text-[11px] text-slate-400">设备健康率</span>
        <div class="flex items-baseline space-x-1 mt-1">
          <span class="text-lg font-bold font-mono text-emerald-400">{{ healthRate }}</span>
          <span class="text-xs text-slate-400">%</span>
        </div>
        <span class="text-[10px] text-slate-500 mt-1">
          待办告警: {{ alertsCount }} 项
        </span>
      </div>
    </div>

    <!-- 关键计算与供电节点硬件探针卡片 -->
    <div class="space-y-2">
      <div class="flex items-center justify-between text-xs text-slate-400 font-medium">
        <span>重点监控节点 (实时探针)</span>
        <span class="text-[11px] text-slate-500">点击设备可直接在左侧发起诊断</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div
          v-for="node in nodes"
          :key="node.device_id"
          @click="$emit('inspectDevice', node.device_id)"
          class="p-2.5 rounded-xl bg-slate-800/40 hover:bg-slate-800/70 border border-slate-700/50 hover:border-emerald-500/40 cursor-pointer transition-all space-y-1.5 group"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-1.5">
              <span class="font-mono text-xs font-semibold text-slate-200 group-hover:text-emerald-300 transition-colors">
                {{ node.device_id }}
              </span>
              <span
                :class="[
                  'px-1.5 py-0.2 rounded text-[10px] font-medium',
                  statusBadgeClass(node.health_status)
                ]"
              >
                {{ node.health_status }}
              </span>
            </div>
            <span class="text-[10px] text-slate-500 truncate max-w-[120px]">{{ node.location }}</span>
          </div>

          <div class="flex items-center justify-between text-[11px] font-mono text-slate-300">
            <span>
              温度:
              <strong :class="node.temperature > 40 ? 'text-rose-400' : node.temperature > 35 ? 'text-amber-400' : 'text-emerald-400'">
                {{ node.temperature }}℃
              </strong>
            </span>
            <span>CPU: {{ node.cpu_usage }}%</span>
            <span>风扇: {{ node.fan_speed_rpm }} RPM</span>
          </div>
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
})

defineEmits(['refresh', 'inspectDevice'])

const overview = computed(() => props.metrics?.overview || {})
const avgTemp = computed(() => overview.value.avg_temperature || 24.5)
const avgCpu = computed(() => overview.value.avg_cpu_load || 35.0)
const totalPower = computed(() => overview.value.total_power_watts || 1200)
const healthRate = computed(() => overview.value.system_health_rate || 100)
const alertsCount = computed(() => overview.value.active_alerts_count || 0)
const nodes = computed(() => props.metrics?.nodes || [])

function statusBadgeClass(status) {
  switch (status) {
    case 'HEALTHY':
      return 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/30'
    case 'WARNING':
      return 'bg-amber-950/80 text-amber-300 border border-amber-500/30'
    case 'OVERHEAT':
      return 'bg-rose-950/80 text-rose-300 border border-rose-500/30 animate-pulse'
    case 'OFFLINE':
      return 'bg-slate-800 text-slate-400 border border-slate-700'
    default:
      return 'bg-slate-800 text-slate-300'
  }
}
</script>
