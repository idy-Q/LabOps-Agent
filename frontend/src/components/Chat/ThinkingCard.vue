<template>
  <div
    v-if="thought || isThinking"
    class="my-2.5 rounded-xl border border-indigo-500/20 bg-indigo-950/20 backdrop-blur-sm overflow-hidden text-xs transition-all duration-300"
  >
    <!-- 头部栏 (点击切换展开/折叠) -->
    <div
      @click="toggleCollapse"
      class="px-3.5 py-2 flex items-center justify-between cursor-pointer select-none bg-indigo-900/20 hover:bg-indigo-900/30 text-indigo-300 border-b border-indigo-500/10"
    >
      <div class="flex items-center space-x-2">
        <!-- 思考动效指示器 (仿 DeepSeek-R1) -->
        <span
          v-if="isThinking"
          class="relative flex h-2 w-2"
        >
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
        </span>
        <span
          v-else
          class="inline-block w-1.5 h-1.5 rounded-full bg-indigo-400"
        ></span>

        <span class="font-medium tracking-wide flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          {{ isThinking ? 'DeepSeek-R1 推理思考中...' : '深度思考链 (已完成推理)' }}
        </span>

        <span
          v-if="step"
          class="px-1.5 py-0.5 rounded bg-indigo-800/50 text-[10px] text-indigo-200"
        >
          第 {{ step }} 轮决策
        </span>
      </div>

      <div class="flex items-center space-x-1.5 text-indigo-400/80 hover:text-indigo-200 text-[11px]">
        <span>{{ isCollapsed ? '展开' : '折叠' }}</span>
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
      class="px-3.5 py-2.5 text-slate-300 font-mono leading-relaxed whitespace-pre-wrap text-[11px] max-h-60 overflow-y-auto bg-slate-900/40 border-t border-indigo-500/5"
    >
      <div v-if="thought">{{ thought }}</div>
      <div
        v-else-if="isThinking"
        class="flex items-center space-x-1.5 text-indigo-400/70"
      >
        <span class="inline-block animate-pulse">正在梳理设备告警信号与安全规约...</span>
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

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}
</script>
