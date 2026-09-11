<template>
  <div ref="containerRef" class="flex-1 overflow-y-auto p-4 space-y-4 text-zinc-200">
    <!-- 欢迎状态卡片 (Linear Minimalist 风格) -->
    <div
      v-if="messages.length === 0"
      class="h-full flex flex-col items-center justify-center text-center p-6 space-y-4 max-w-md mx-auto my-auto"
    >
      <div class="w-14 h-14 rounded-2xl bg-zinc-900/90 border border-indigo-500/20 flex items-center justify-center shadow-lg group hover:border-indigo-500/40 transition-colors">
        <svg class="w-8 h-8 transition-transform duration-300 group-hover:scale-105" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="labops-stream-logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#818cf8" />
              <stop offset="50%" stop-color="#6366f1" />
              <stop offset="100%" stop-color="#38bdf8" />
            </linearGradient>
            <linearGradient id="labops-stream-tool-grad" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#38bdf8" />
              <stop offset="100%" stop-color="#818cf8" />
            </linearGradient>
            <mask id="labops-stream-wrench-cutout">
              <rect width="100" height="100" fill="white" />
              <path d="M 40.3,29.4 L 37.2,14.2 L 34.4,12.1 L 31.1,10.9 L 27.6,10.7 L 24.2,11.5 L 21.2,13.3 L 18.8,15.8 L 17.3,19.0 L 24.8,12.4 L 30.4,18.1 L 31.5,25.5 L 24.1,24.4 L 18.4,18.8 L 25.0,11.3 L 21.8,12.8 L 19.3,15.2 L 17.5,18.2 L 16.7,21.6 L 16.9,25.1 L 18.1,28.4 L 20.2,31.2 L 35.4,34.3 L 62.3,61.2 L 65.4,76.4 L 66.9,77.6 L 68.5,78.6 L 70.2,79.3 L 72.0,79.8 L 73.9,79.9 L 75.8,79.8 L 77.6,79.3 L 77.8,78.2 L 72.2,72.5 L 71.1,65.1 L 78.5,66.2 L 84.2,71.8 L 85.3,71.6 L 85.8,69.8 L 85.9,67.9 L 85.8,66.0 L 85.3,64.2 L 84.6,62.5 L 83.6,60.9 L 82.4,59.4 L 67.2,56.3 Z" fill="black" stroke="black" stroke-width="6" stroke-linejoin="round" />
            </mask>
          </defs>
          <g mask="url(#labops-stream-wrench-cutout)">
            <path fill-rule="evenodd" d="M 37.0,20.8 L 39.1,11.3 L 48.9,11.3 L 51.0,20.8 L 61.1,25.0 L 69.3,19.7 L 76.3,26.7 L 71.0,34.9 L 75.2,45.0 L 84.7,47.1 L 84.7,56.9 L 75.2,59.0 L 71.0,69.1 L 76.3,77.3 L 69.3,84.3 L 61.1,79.0 L 51.0,83.2 L 48.9,92.7 L 39.1,92.7 L 37.0,83.2 L 26.9,79.0 L 18.7,84.3 L 11.7,77.3 L 17.0,69.1 L 12.8,59.0 L 3.3,56.9 L 3.3,47.1 L 12.8,45.0 L 17.0,34.9 L 11.7,26.7 L 18.7,19.7 L 26.9,25.0 Z M 65.0,52.0 L 64.3,57.4 L 62.2,62.5 L 58.8,66.8 L 54.5,70.2 L 49.4,72.3 L 44.0,73.0 L 38.6,72.3 L 33.5,70.2 L 29.2,66.8 L 25.8,62.5 L 23.7,57.4 L 23.0,52.0 L 23.7,46.6 L 25.8,41.5 L 29.2,37.2 L 33.5,33.8 L 38.6,31.7 L 44.0,31.0 L 49.4,31.7 L 54.5,33.8 L 58.8,37.2 L 62.2,41.5 L 64.3,46.6 Z" fill="url(#labops-stream-logo-grad)" opacity="0.92" />
            <path d="M 78.9,20.7 L 75.3,17.1 L 69.7,19.9 L 68.3,24.2 L 42.1,50.4 L 40.0,48.2 L 28.0,60.3 L 26.7,62.3 L 26.4,64.8 L 27.2,67.1 L 28.9,68.8 L 31.2,69.6 L 33.7,69.3 L 35.7,68.0 L 47.8,56.0 L 45.6,53.9 L 71.8,27.7 L 76.1,26.3 Z" fill="url(#labops-stream-tool-grad)" />
          </g>
          <path d="M 40.3,29.4 L 37.2,14.2 L 34.4,12.1 L 31.1,10.9 L 27.6,10.7 L 24.2,11.5 L 21.2,13.3 L 18.8,15.8 L 17.3,19.0 L 24.8,12.4 L 30.4,18.1 L 31.5,25.5 L 24.1,24.4 L 18.4,18.8 L 25.0,11.3 L 21.8,12.8 L 19.3,15.2 L 17.5,18.2 L 16.7,21.6 L 16.9,25.1 L 18.1,28.4 L 20.2,31.2 L 35.4,34.3 L 62.3,61.2 L 65.4,76.4 L 66.9,77.6 L 68.5,78.6 L 70.2,79.3 L 72.0,79.8 L 73.9,79.9 L 75.8,79.8 L 77.6,79.3 L 77.8,78.2 L 72.2,72.5 L 71.1,65.1 L 78.5,66.2 L 84.2,71.8 L 85.3,71.6 L 85.8,69.8 L 85.9,67.9 L 85.8,66.0 L 85.3,64.2 L 84.6,62.5 L 83.6,60.9 L 82.4,59.4 L 67.2,56.3 Z" fill="url(#labops-stream-logo-grad)" stroke="rgba(255,255,255,0.2)" stroke-width="0.8" stroke-linejoin="round" />
        </svg>
      </div>
      <div>
        <h2 class="text-base font-semibold text-zinc-100 tracking-wide glass-text">LabOps-Agent</h2>
      </div>
      <div class="w-full pt-1 grid grid-cols-1 gap-2.5 text-left text-xs">
        <div class="p-3.5 rounded-xl glass-card-sub border border-white/[0.06] hover:border-white/[0.14] transition-colors flex items-start space-x-2.5 shadow-sm">
          <span class="p-1 rounded-md bg-emerald-500/10 text-emerald-400 shrink-0">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
          <div>
            <div class="font-medium text-zinc-200 glass-text">全白盒推理感知</div>
            <div class="text-[11px] text-zinc-500 mt-0.5">细粒度展现 ReAct 深度思考过程与函数工具入参返回值</div>
          </div>
        </div>
        <div class="p-3.5 rounded-xl glass-card-sub border border-white/[0.06] hover:border-white/[0.14] transition-colors flex items-start space-x-2.5 shadow-sm">
          <span class="p-1 rounded-md bg-cyan-500/10 text-cyan-400 shrink-0">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </span>
          <div>
            <div class="font-medium text-zinc-200 glass-text">左右看板双向联动</div>
            <div class="text-[11px] text-zinc-500 mt-0.5">智能提单与借还操作即时同步右侧 SQLite 真实业务大盘</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息对话流 -->
    <div
      v-for="msg in messages"
      :key="msg.id"
      class="flex flex-col space-y-2 animate-fade-in"
    >
      <!-- 用户提问气泡 (Codex 玻璃气泡) -->
      <div
        v-if="msg.role === 'user'"
        class="flex items-start justify-end space-x-2.5"
      >
        <div class="max-w-[85%] rounded-2xl rounded-tr-sm glass-card bg-indigo-950/35 border-indigo-500/25 px-4 py-2.5 text-zinc-100 text-xs sm:text-sm shadow-sm leading-relaxed whitespace-pre-wrap">
          {{ msg.content }}
        </div>
        <!-- 用户矢量头像 -->
        <div class="w-7 h-7 rounded-full bg-zinc-800/90 border border-white/[0.1] flex items-center justify-center shrink-0 text-zinc-300 shadow-sm">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      </div>

      <!-- Agent 助手回复复合体 (Linear 暗调磨砂卡片) -->
      <div
        v-else-if="msg.role === 'assistant'"
        class="flex items-start space-x-2.5"
      >
        <!-- AI 助手矢量头像 -->
        <div class="w-7 h-7 rounded-lg bg-zinc-900 border border-white/[0.1] flex items-center justify-center shrink-0 text-indigo-400 shadow-sm">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>

        <div class="flex-1 min-w-0 max-w-[92%] space-y-2">
          <!-- 1. 仿 DeepSeek-R1 思考折叠卡片 -->
          <ThinkingCard
            v-if="msg.thought || msg.isThinking"
            :thought="msg.thought"
            :isThinking="msg.isThinking"
            :step="msg.step"
          />

          <!-- 2. 工具调用过程卡片组 -->
          <div v-if="msg.toolCalls && msg.toolCalls.length > 0" class="space-y-1.5">
            <ToolCard
              v-for="(tc, idx) in msg.toolCalls"
              :key="idx"
              :toolCall="tc"
            />
          </div>

          <!-- 3. 机房条例溯源徽章组 -->
          <div v-if="msg.citations && msg.citations.length > 0" class="flex flex-wrap items-center">
            <CitationBadge
              v-for="(c, cIdx) in msg.citations"
              :key="cIdx"
              :citation="c"
            />
          </div>

          <!-- 4. 助手最终正文回答 (Codex Glass Card) -->
          <div
            v-if="msg.content"
            class="p-4 rounded-2xl rounded-tl-sm glass-card border text-xs sm:text-sm text-zinc-200 leading-relaxed shadow-sm space-y-2"
          >
            <div
              class="prose prose-xs max-w-none whitespace-pre-wrap break-words font-sans leading-relaxed text-zinc-200"
              v-html="renderMarkdown(msg.content)"
            ></div>
          </div>

          <!-- 流式打字与决策状态指示灯 -->
          <div
            v-if="msg.isStreaming && !msg.content"
            class="flex items-center space-x-1.5 text-xs text-zinc-400 py-1"
          >
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce"></span>
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.2s]"></span>
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.4s]"></span>
            <span class="text-[11px] text-zinc-400 font-mono ml-1">
              {{ msg.isThinking ? 'Agent 正在进行深度白盒推理研判...' : '正在组织回答...' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import ThinkingCard from './ThinkingCard.vue'
import ToolCard from './ToolCard.vue'
import CitationBadge from './CitationBadge.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
})

const containerRef = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.scrollTop = containerRef.value.scrollHeight
    }
  })
}

watch(
  () => props.messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)

defineExpose({ scrollToBottom })

function renderMarkdown(text) {
  if (!text) return ''
  // 1. 转义 HTML 实体防止 XSS
  let escaped = String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 2. 提取并保护多行代码块 ```lang \n code \n ```
  const codeBlocks = []
  escaped = escaped.replace(/```([a-zA-Z0-9_-]*)[^\S\r\n]*\r?\n([\s\S]*?)```/g, (match, lang, code) => {
    const langLabel = lang
      ? `<span class="px-2 py-0.5 rounded-md bg-zinc-800 text-zinc-300 text-[10px] font-mono border border-white/[0.08]">${lang}</span>`
      : ''
    const blockHtml = `<div class="my-2.5 rounded-xl border border-white/[0.08] bg-black/40 backdrop-blur-md text-zinc-200 overflow-hidden shadow-sm">
      <div class="px-3 py-1.5 bg-white/[0.04] border-b border-white/[0.06] flex items-center justify-between text-[11px] text-zinc-400">
        <span class="font-mono text-[10px] text-zinc-500">Code Snippet</span>
        ${langLabel}
      </div>
      <pre class="p-3 text-xs text-zinc-200 font-mono leading-relaxed overflow-x-auto"><code>${code.trim()}</code></pre>
    </div>`
    const placeholder = `__LABOPS_CODEBLOCK_${codeBlocks.length}__`
    codeBlocks.push(blockHtml)
    return placeholder
  })

  // 3. 标题语法 (#, ##, ###)
  escaped = escaped.replace(/^###[ \t]+(.*)$/gm, '<h4 class="font-medium text-zinc-100 text-xs sm:text-sm mt-2 mb-1">$1</h4>')
  escaped = escaped.replace(/^##[ \t]+(.*)$/gm, '<h3 class="font-medium text-zinc-100 text-sm sm:text-base mt-2.5 mb-1">$1</h3>')
  escaped = escaped.replace(/^#[ \t]+(.*)$/gm, '<h2 class="font-medium text-zinc-100 text-base sm:text-lg mt-3 mb-1.5">$1</h2>')

  // 4. 列表语法
  escaped = escaped.replace(/^[ \t]*[-*][ \t]+(.*)$/gm, '<div class="flex items-start space-x-1.5 my-0.5"><span class="text-zinc-500 font-bold">•</span><span>$1</span></div>')
  escaped = escaped.replace(/^[ \t]*(\d+)\.[ \t]+(.*)$/gm, '<div class="flex items-start space-x-1.5 my-0.5"><span class="font-mono text-zinc-400 text-xs">$1.</span><span>$2</span></div>')

  // 5. 加粗语法 **text**
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong class="font-medium text-zinc-100">$1</strong>')

  // 6. 行内代码 `code`
  escaped = escaped.replace(/`([^`\n]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-black/40 backdrop-blur-sm border border-white/[0.08] text-emerald-400 font-mono text-[11px]">$1</code>')

  // 7. 还原代码块
  codeBlocks.forEach((blockHtml, idx) => {
    escaped = escaped.replace(`__LABOPS_CODEBLOCK_${idx}__`, blockHtml)
  })

  return escaped
}
</script>
