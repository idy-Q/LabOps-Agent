<template>
  <div class="my-2.5 rounded-xl border border-amber-500/20 bg-amber-950/10 backdrop-blur-sm overflow-hidden text-xs transition-all duration-200">
    <!-- 头部栏 -->
    <div
      @click="isExpanded = !isExpanded"
      class="px-3 py-2 flex items-center justify-between cursor-pointer select-none bg-amber-900/15 hover:bg-amber-900/25 border-b border-amber-500/10 text-amber-200"
    >
      <div class="flex items-center space-x-2">
        <!-- 执行中或已完成图标 -->
        <span v-if="!toolCall.result" class="flex items-center text-amber-400">
          <svg class="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
        </span>
        <span v-else class="text-emerald-400">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
        </span>

        <span class="font-semibold text-amber-100 flex items-center gap-1.5">
          <span class="px-1.5 py-0.5 rounded bg-amber-500/20 border border-amber-500/30 text-[10px] text-amber-300 font-mono">
            @tool
          </span>
          {{ toolFriendlyName(toolCall.name) }}
        </span>

        <span class="text-slate-400 font-mono text-[11px]">({{ toolCall.name }})</span>

        <span
          v-if="toolCall.step"
          class="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400"
        >
          Step {{ toolCall.step }}
        </span>
      </div>

      <div class="flex items-center space-x-2 text-slate-400 text-[11px]">
        <span :class="toolCall.result ? 'text-emerald-400' : 'text-amber-400'">
          {{ toolCall.result ? '调用完毕' : '调度中...' }}
        </span>
        <svg
          :class="['w-3.5 h-3.5 transition-transform duration-200', isExpanded ? 'rotate-180' : '']"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- 展开详情 (入参与返回结果) -->
    <div v-show="isExpanded" class="p-3 space-y-2 bg-slate-950/60 font-mono text-[11px]">
      <!-- 调用入参 -->
      <div>
        <div class="flex items-center justify-between text-[10px] text-slate-400 uppercase tracking-wider mb-1">
          <span>调用参数 (Arguments)</span>
          <button
            @click.stop="copyText(JSON.stringify(toolCall.args, null, 2))"
            class="text-amber-400 hover:text-amber-300 text-[10px]"
          >
            {{ copied ? '已复制' : '复制' }}
          </button>
        </div>
        <pre class="p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-amber-200/90 overflow-x-auto">{{ formatJson(toolCall.args) }}</pre>
      </div>

      <!-- 执行返回结果 -->
      <div v-if="toolCall.result">
        <div class="text-[10px] text-slate-400 uppercase tracking-wider mb-1">
          <span>执行响应 (Return Result)</span>
        </div>
        <pre class="p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-emerald-300/90 overflow-x-auto max-h-48">{{ formatJson(toolCall.result) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  toolCall: {
    type: Object,
    required: true,
  },
})

const isExpanded = ref(false)
const copied = ref(false)

const toolNameMap = {
  get_server_metrics: '服务器指标感知',
  create_ticket: '自动创建运维工单',
  update_ticket_status: '更新工单处置状态',
  query_tickets: '检索工单库',
  borrow_asset: '办理设备借出登记',
  return_asset: '办理设备归还入库',
  query_assets: '检索资产台账',
  update_asset_health: '更新资产健康等级',
  query_regulations: '检索机房安全规程',
}

function toolFriendlyName(name) {
  return toolNameMap[name] || name
}

function formatJson(val) {
  if (typeof val === 'string') {
    try {
      return JSON.stringify(JSON.parse(val), null, 2)
    } catch {
      return val
    }
  }
  return JSON.stringify(val, null, 2)
}

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 1500)
  })
}
</script>
