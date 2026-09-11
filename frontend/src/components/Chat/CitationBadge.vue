<template>
  <div class="inline-block my-1 mr-2">
    <!-- 徽章触发按钮 (Linear Pill 风格) -->
    <button
      @click="showModal = true"
      class="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium bg-zinc-900/90 hover:bg-zinc-800 border border-white/[0.08] hover:border-emerald-500/30 text-zinc-300 hover:text-white transition-all duration-150 shadow-sm group active:scale-95"
      :title="`点击查看溯源详情: ${citation.source}`"
    >
      <!-- 规范法典/卷轴 SVG 矢量图标 -->
      <svg class="w-3.5 h-3.5 text-emerald-400 group-hover:scale-110 transition-transform shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
      <span class="truncate max-w-[200px] text-zinc-200">依据:《{{ citation.source }}》</span>
      <span v-if="citation.section" class="text-zinc-500 font-normal truncate max-w-[120px]">· {{ citation.section }}</span>
    </button>

    <!-- 溯源详情弹窗 (Linear Modal) -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in"
      @click.self="showModal = false"
      @keydown.esc.window="showModal = false"
    >
      <div class="relative w-full max-w-lg rounded-2xl glass-card border border-white/[0.12] p-5 shadow-2xl space-y-4 backdrop-blur-xl">
        <!-- 弹窗标题 -->
        <div class="flex items-center justify-between border-b border-white/[0.08] pb-3">
          <div class="flex items-center space-x-2">
            <span class="p-1.5 rounded-lg bg-zinc-900/90 border border-white/[0.08] text-emerald-400">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <div>
              <h3 class="font-medium text-zinc-100 text-sm glass-text">机房安全运维规程溯源依据</h3>
              <p class="text-[11px] text-zinc-500">知识库 RAG 向量防幻觉召回证据链</p>
            </div>
          </div>
          <button
            @click="showModal = false"
            class="text-zinc-500 hover:text-zinc-300 p-1.5 rounded-lg hover:bg-zinc-800 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 规程文献来源与条款 -->
        <div class="rounded-xl bg-zinc-950/60 p-3.5 border border-white/[0.06] space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="text-zinc-400">规范文献：</span>
            <span class="font-medium text-emerald-300 font-mono">《{{ citation.source }}》</span>
          </div>
          <div v-if="citation.section" class="flex items-center justify-between">
            <span class="text-zinc-400">章节条款：</span>
            <span class="text-zinc-300">{{ citation.section }}</span>
          </div>
          <div v-if="citation.step" class="flex items-center justify-between">
            <span class="text-zinc-400">研判轮次：</span>
            <span class="font-mono text-zinc-400">Round {{ citation.step }}</span>
          </div>
        </div>

        <!-- 条款原文 -->
        <div class="space-y-1.5">
          <span class="text-xs font-medium text-zinc-300 flex items-center gap-1.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            召回条款完整原文：
          </span>
          <div class="p-3.5 rounded-xl bg-black/40 backdrop-blur-sm border border-white/[0.08] text-zinc-300 text-xs leading-relaxed max-h-56 overflow-y-auto whitespace-pre-wrap font-sans">
            {{ citation.content }}
          </div>
        </div>

        <!-- 底部说明与操作 -->
        <div class="flex items-center justify-between pt-2 border-t border-white/[0.08] text-[11px] text-zinc-500">
          <span>防幻觉溯源机制保障决策学术准确性</span>
          <button
            @click="showModal = false"
            class="px-4 py-1.5 rounded-lg bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs transition-all shadow-sm active:scale-95"
          >
            完成查看
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  citation: {
    type: Object,
    required: true,
  },
})

const showModal = ref(false)
</script>
