<template>
  <div class="border-t glass-panel p-3.5 space-y-2.5">
    <!-- 快捷场景胶囊 (Prompt Capsules - Linear 药丸风格) -->
    <div class="flex items-center space-x-2 overflow-x-auto pb-1 text-xs no-scrollbar">
      <span class="text-zinc-400 shrink-0 text-[11px] font-medium flex items-center gap-1.5 glass-text">
        <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        运维高频场景:
      </span>

      <button
        v-for="capsule in promptCapsules"
        :key="capsule.label"
        @click="triggerCapsule(capsule.prompt)"
        :disabled="isLoading"
        class="shrink-0 px-2.5 py-1 rounded-lg glass-card-sub hover:bg-white/[0.08] text-zinc-300 hover:text-white border border-white/[0.06] hover:border-indigo-500/30 transition-all text-[11px] disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1.5 shadow-sm active:scale-95 group"
        :title="`一键提问: ${capsule.prompt}`"
      >
        <!-- 矢量 SVG 图标 -->
        <!-- 超温告警图标 -->
        <svg v-if="capsule.type === 'overheat'" class="w-3 h-3 text-rose-400 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343a7.975 7.975 0 012.343 5.657c0 2.12-.835 4.16-2.342 5.657z" />
        </svg>
        <!-- 资产借用图标 -->
        <svg v-else-if="capsule.type === 'borrow'" class="w-3 h-3 text-cyan-400 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
        <!-- 规程检索图标 -->
        <svg v-else-if="capsule.type === 'regulation'" class="w-3 h-3 text-emerald-400 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <!-- 待办工单图标 -->
        <svg v-else-if="capsule.type === 'ticket'" class="w-3 h-3 text-amber-400 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
        <!-- 异常设备排查图标 -->
        <svg v-else class="w-3 h-3 text-violet-400 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>

        <span>{{ capsule.label }}</span>
      </button>
    </div>

    <!-- 输入主区域 (Linear Minimalist Input) -->
    <div class="relative flex items-end space-x-2 bg-black/30 backdrop-blur-sm border border-white/[0.08] focus-within:border-indigo-500/60 rounded-xl p-1.5 transition-all shadow-sm">
      <textarea
        ref="inputRef"
        v-model="inputContent"
        @keydown="handleKeyDown"
        :disabled="isLoading"
        rows="2"
        placeholder="向智能运维管家提问，如：'DEV-SRV-201 告警超温，查一下并按规章自动提单' (Enter 发送, Shift+Enter 换行)"
        class="flex-1 bg-transparent text-zinc-100 placeholder-zinc-500 text-xs sm:text-sm px-3 py-1.5 focus:outline-none resize-none disabled:opacity-50"
      ></textarea>

      <div class="flex items-center space-x-1.5 pb-1 pr-1">
        <!-- 停止生成按钮 -->
        <button
          v-if="isLoading"
          @click="$emit('abort')"
          type="button"
          class="p-2 rounded-lg bg-rose-500 hover:bg-rose-400 text-white transition-all shadow-sm flex items-center justify-center active:scale-95"
          title="中止推理与生成"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <rect x="5" y="5" width="10" height="10" rx="1.5" />
          </svg>
        </button>

        <!-- 发送按钮 (Linear Button) -->
        <button
          v-else
          @click="handleSend"
          :disabled="!inputContent.trim()"
          type="button"
          class="p-2 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 transition-all disabled:opacity-30 disabled:cursor-not-allowed shadow-sm flex items-center justify-center group active:scale-95 border border-zinc-100"
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
    type: 'overheat',
    label: '超温提单排查',
    prompt: '查询 DEV-SRV-201 监控指标，若发现温度超标请按规章自动提单',
  },
  {
    type: 'borrow',
    label: '算力节点借用',
    prompt: '帮李老师办理设备 DEV-SRV-202 的借用登记',
  },
  {
    type: 'regulation',
    label: '机房用电防火规范',
    prompt: '检索机房用电安全和机柜额定功耗限制规范，说明阈值要求',
  },
  {
    type: 'ticket',
    label: '待办工单汇总',
    prompt: '查询机房当前全部未结案的待办运维工单',
  },
  {
    type: 'alert',
    label: '离线异常巡检',
    prompt: '巡检当前健康状态为 OVERHEAT 或 WARNING 的资产设备',
  },
]

function triggerCapsule(prompt) {
  if (props.isLoading) return
  inputContent.value = prompt
  handleSend()
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
