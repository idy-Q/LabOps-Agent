<template>
  <div
    v-if="thought || isThinking"
    class="my-2.5 rounded-xl border glass-card overflow-hidden text-xs transition-all duration-300 shadow-sm"
  >
    <!-- 头部栏 (点击切换展开/折叠) -->
    <div
      @click="toggleCollapse"
      class="px-3.5 py-2 flex items-center justify-between cursor-pointer select-none bg-white/[0.03] hover:bg-white/[0.07] text-zinc-300 border-b border-white/[0.06] transition-colors"
    >
      <div class="flex items-center space-x-2">
        <!-- 思考动效指示器 -->
        <span
          v-if="isThinking"
          class="relative flex h-2 w-2"
        >
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-400"></span>
        </span>
        <span
          v-else
          class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"
        ></span>

        <span class="font-medium tracking-wide flex items-center gap-1.5 text-zinc-200 glass-text">
          <!-- AI 芯片算力 SVG 图标 -->
          <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          {{ isThinking ? 'DeepSeek-R1 状态机深度推理中...' : 'ReAct 深度推理链 (已完成研判)' }}
        </span>

        <span
          v-if="step"
          class="px-2 py-0.5 rounded-md bg-zinc-800/80 border border-white/[0.08] text-[10px] text-zinc-400 font-mono"
        >
          Round {{ step }}
        </span>
      </div>

      <div class="flex items-center space-x-2 text-zinc-500 text-[11px]">
        <!-- 复制思考过程按钮 -->
        <button
          v-if="thought"
          @click.stop="copyThinking"
          class="hover:text-zinc-200 px-1.5 py-0.5 rounded hover:bg-zinc-800 transition-colors flex items-center space-x-1"
          title="复制思考链内容"
        >
          <svg v-if="!copied" class="w-3 h-3 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <svg v-else class="w-3 h-3 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span :class="copied ? 'text-emerald-400' : ''">{{ copied ? '已复制' : '复制' }}</span>
        </button>

        <span class="text-zinc-600">|</span>

        <span class="hover:text-zinc-300 transition-colors">{{ isCollapsed ? '展开' : '折叠' }}</span>
        <svg
          :class="['w-3.5 h-3.5 transition-transform duration-200', isCollapsed ? '' : 'rotate-180']"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- 思考内容正文 -->
    <div
      v-show="!isCollapsed"
      class="px-3.5 py-2.5 text-zinc-300 font-mono leading-relaxed whitespace-pre-wrap text-[11px] max-h-60 overflow-y-auto bg-black/30 backdrop-blur-sm border-t border-white/[0.04] transition-all"
    >
      <div v-if="thought">{{ thought }}</div>
      <div
        v-else-if="isThinking"
        class="flex items-center space-x-2 text-zinc-400"
      >
        <span class="inline-block w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
        <span class="animate-pulse">正在梳理设备告警信号与高校机房安全规约...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  thought: {
    type: String,
    default: '',
  },
  isThinking: {
    type: Boolean,
    default: false,
  },
  step: {
    type: Number,
    default: null,
  },
})

const isCollapsed = ref(false)
const copied = ref(false)

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
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

function copyThinking() {
  if (!props.thought) return
  const onDone = () => {
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 1500)
  }
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(props.thought)
      .then(onDone)
      .catch(() => {
        if (fallbackCopyText(props.thought)) onDone()
      })
  } else if (fallbackCopyText(props.thought)) {
    onDone()
  }
}
</script>
