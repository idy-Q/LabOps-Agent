<template>
  <div class="inline-block my-1 mr-2">
    <!-- 徽章触发按钮 -->
    <button
      @click="showModal = true"
      class="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-900/60 hover:border-emerald-500/50 hover:text-emerald-200 transition-all duration-200 shadow-sm group"
    >
      <svg class="w-3.5 h-3.5 text-emerald-400 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
      <span>依据:《{{ citation.source }}》</span>
      <span v-if="citation.section" class="text-emerald-400/70 font-normal">· {{ citation.section }}</span>
    </button>

    <!-- 溯源详情弹窗 -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in"
      @click.self="showModal = false"
    >
      <div class="relative w-full max-w-lg rounded-2xl bg-slate-900 border border-emerald-500/30 p-5 shadow-2xl space-y-4">
        <!-- 弹窗标题 -->
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center space-x-2">
            <span class="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
            <div>
              <h3 class="font-semibold text-slate-100 text-sm">机房管理规范溯源依据</h3>
              <p class="text-[11px] text-slate-400">知识库 RAG 向量召回条目</p>
            </div>
          </div>
          <button
            @click="showModal = false"
            class="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 规程文献来源与条款 -->
        <div class="rounded-xl bg-slate-800/60 p-3 border border-slate-700/50 space-y-1 text-xs">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">规范文献：</span>
            <span class="font-medium text-emerald-400 font-mono">《{{ citation.source }}》</span>
          </div>
          <div v-if="citation.section" class="flex items-center justify-between">
            <span class="text-slate-400">章节条款：</span>
            <span class="text-slate-200">{{ citation.section }}</span>
          </div>
        </div>

        <!-- 条款原文 -->
        <div class="space-y-1">
          <span class="text-xs font-medium text-slate-300">召回条款原文：</span>
          <div class="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-300 text-xs leading-relaxed max-h-56 overflow-y-auto whitespace-pre-wrap font-sans">
            {{ citation.content }}
          </div>
        </div>

        <!-- 底部说明 -->
        <div class="flex items-center justify-between pt-2 border-t border-slate-800 text-[11px] text-slate-400">
          <span>防幻觉溯源机制保障决策准确性</span>
          <button
            @click="showModal = false"
            class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs transition-colors"
          >
            关闭
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
