<template>
  <div class="my-2.5 rounded-xl border glass-card overflow-hidden text-xs transition-all duration-200 shadow-sm">
    <!-- 头部栏 -->
    <div
      @click="isExpanded = !isExpanded"
      class="px-3 py-2 flex items-center justify-between cursor-pointer select-none bg-white/[0.03] hover:bg-white/[0.07] border-b border-white/[0.06] text-zinc-300 transition-colors"
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

        <!-- 标准化工具矢量 SVG 徽章 (替代 @tool) -->
        <div class="flex items-center space-x-1.5 font-medium text-zinc-100">
          <span class="px-1.5 py-0.5 rounded-md bg-zinc-800 border border-white/[0.08] text-[10px] text-indigo-300 flex items-center gap-1 font-mono">
            <svg class="w-3 h-3 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            TOOL
          </span>
          <span class="glass-text">{{ toolFriendlyName(toolCall.name) }}</span>
        </div>

        <span class="text-zinc-500 font-mono text-[11px]">({{ toolCall.name }})</span>

        <span
          v-if="toolCall.step"
          class="px-2 py-0.5 rounded-md bg-zinc-900 border border-white/[0.06] text-[10px] text-zinc-400 font-mono"
        >
          Step {{ toolCall.step }}
        </span>
      </div>

      <div class="flex items-center space-x-2 text-zinc-400 text-[11px]">
        <span :class="toolCall.result ? 'text-emerald-400 font-mono' : 'text-amber-400 font-mono'">
          {{ toolCall.result ? '调用完毕' : '正在调度...' }}
        </span>
        <svg
          :class="['w-3.5 h-3.5 transition-transform duration-200 text-zinc-500', isExpanded ? 'rotate-180' : '']"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- 展开详情 (入参与返回结果) -->
    <div v-show="isExpanded" class="p-3 space-y-2.5 bg-black/30 backdrop-blur-sm font-mono text-[11px] border-t border-white/[0.04]">
      <!-- 调用入参 -->
      <div>
        <div class="flex items-center justify-between text-[10px] text-zinc-400 uppercase tracking-wider mb-1">
          <span class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            调用入参 (Arguments)
          </span>
          <button
            @click.stop="copyText(JSON.stringify(toolCall.args, null, 2), 'args')"
            class="text-zinc-400 hover:text-zinc-200 text-[10px] transition-colors flex items-center space-x-1"
          >
            <svg v-if="copiedField !== 'args'" class="w-3 h-3 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <svg v-else class="w-3 h-3 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span :class="copiedField === 'args' ? 'text-emerald-400' : ''">{{ copiedField === 'args' ? '已复制' : '复制 JSON' }}</span>
          </button>
        </div>
        <pre class="p-2.5 rounded-lg bg-black/40 backdrop-blur-sm border border-white/[0.08] text-zinc-300 overflow-x-auto leading-relaxed">{{ formatJson(toolCall.args) }}</pre>
      </div>

      <!-- 执行返回结果 -->
      <div v-if="toolCall.result">
        <div class="flex items-center justify-between text-[10px] text-zinc-400 uppercase tracking-wider mb-1">
          <span class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            执行响应结果 (Execution Result)
          </span>
          <button
            @click.stop="copyText(JSON.stringify(toolCall.result, null, 2), 'result')"
            class="text-zinc-400 hover:text-zinc-200 text-[10px] transition-colors flex items-center space-x-1"
          >
            <svg v-if="copiedField !== 'result'" class="w-3 h-3 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <svg v-else class="w-3 h-3 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span :class="copiedField === 'result' ? 'text-emerald-400' : ''">{{ copiedField === 'result' ? '已复制' : '复制 JSON' }}</span>
          </button>
        </div>
        <pre class="p-2.5 rounded-lg bg-black/40 backdrop-blur-sm border border-emerald-500/20 text-emerald-300 overflow-x-auto max-h-48 leading-relaxed">{{ formatJson(toolCall.result) }}</pre>
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
const copiedField = ref('')

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

function fallbackCopyText(text) {
  try {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    const success = document.execCommand('copy')
    document.body.removeChild(ta)
    return success
  } catch {
    return false
  }
}

function copyText(text, field) {
  if (!text) return
  const onDone = () => {
    copiedField.value = field
    setTimeout(() => {
      if (copiedField.value === field) {
        copiedField.value = ''
      }
    }, 1500)
  }
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(text)
      .then(onDone)
      .catch(() => {
        if (fallbackCopyText(text)) onDone()
      })
  } else if (fallbackCopyText(text)) {
    onDone()
  }
}
</script>
