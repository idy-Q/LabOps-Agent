<template>
  <div class="border-t border-slate-800 bg-slate-900/90 backdrop-blur p-3.5 space-y-2.5">
    <!-- 快捷指令胶囊 (Prompt Capsules) -->
    <div class="flex items-center space-x-2 overflow-x-auto pb-1 text-xs no-scrollbar">
      <span class="text-slate-500 shrink-0 text-[11px] font-medium flex items-center gap-1">
        <svg class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        推荐场景:
      </span>
      <button
        v-for="capsule in promptCapsules"
        :key="capsule.label"
        @click="selectCapsule(capsule.prompt)"
        :disabled="isLoading"
        class="shrink-0 px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 hover:text-white transition-all text-[11px] disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
      >
        <span>{{ capsule.icon }}</span>
        <span>{{ capsule.label }}</span>
      </button>
    </div>

    <!-- 输入主区域 -->
    <div class="relative flex items-end space-x-2 bg-slate-950/80 border border-slate-700/80 rounded-2xl p-1.5 focus-within:border-emerald-500/80 focus-within:ring-1 focus-within:ring-emerald-500/50 transition-all">
      <textarea
        ref="inputRef"
        v-model="inputContent"
        @keydown="handleKeyDown"
        :disabled="isLoading"
        rows="2"
        placeholder="向 LabOps-Agent 提问，如：'DEV-SRV-201 温度过高，查一下并提单' (Enter 发送, Shift+Enter 换行)"
        class="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-xs sm:text-sm px-3 py-1.5 focus:outline-none resize-none disabled:opacity-50"
      ></textarea>

      <div class="flex items-center space-x-1.5 pb-1 pr-1">
        <!-- 停止生成按钮 -->
        <button
          v-if="isLoading"
          @click="$emit('abort')"
          type="button"
          class="p-2 rounded-xl bg-rose-600/80 hover:bg-rose-500 text-white transition-colors shadow-sm flex items-center justify-center"
          title="中止生成"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <rect x="5" y="5" width="10" height="10" rx="1.5" />
          </svg>
        </button>

        <!-- 发送按钮 -->
        <button
          v-else
          @click="handleSend"
          :disabled="!inputContent.trim()"
          type="button"
          class="p-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-sm flex items-center justify-center group"
          title="发送指令"
        >
          <svg class="w-4 h-4 transform group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['send', 'abort'])

const inputContent = ref('')
const inputRef = ref(null)

const promptCapsules = [
  {
    icon: '🔥',
    label: '超温提单排查',
    prompt: '查询DEV-SRV-201监控指标，若异常请自动提单',
  },
  {
    icon: '📦',
    label: '资产借出登记',
    prompt: '帮李老师办理设备 DEV-SRV-202 的借用登记',
  },
  {
    icon: '📜',
    label: '机房规程检索',
    prompt: '机房用电安全和机架功耗限制是怎样的？',
  },
  {
    icon: '📋',
    label: '待办工单查询',
    prompt: '查询当前机房全部待办工单',
  },
  {
    icon: '⚠️',
    label: '告警设备台账',
    prompt: '查询当前健康状态为 OVERHEAT 的设备资产',
  },
]

function selectCapsule(prompt) {
  inputContent.value = prompt
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus()
    }
  })
}

function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleSend() {
  const trimmed = inputContent.value.trim()
  if (!trimmed || props.isLoading) return
  emit('send', trimmed)
  inputContent.value = ''
}
</script>
