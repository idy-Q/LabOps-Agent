<template>
  <div ref="containerRef" class="flex-1 overflow-y-auto p-4 space-y-4 text-zinc-200">
    <!-- 欢迎状态卡片 (Linear Minimalist 风格) -->
    <div
      v-if="messages.length === 0"
      class="min-h-full flex flex-col items-center justify-center text-center px-4 py-6 sm:py-8 space-y-4 max-w-lg mx-auto w-full select-none"
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
      <div class="space-y-1">
        <h2 class="text-base font-semibold text-zinc-100 tracking-wide glass-text">LabOps-Agent</h2>
        <p class="text-xs text-zinc-400">数据中心智能自治运维系统 · 点击典型场景即刻体验</p>
      </div>

      <!-- 典型运维场景推荐卡片 (可点击/支持直接提问与填入编辑) -->
      <div class="w-full pt-1 grid grid-cols-1 gap-2.5 text-left text-xs">
        <div
          v-for="scenario in recommendedScenarios"
          :key="scenario.id"
          @click="triggerScenario(scenario.prompt)"
          role="button"
          tabindex="0"
          @keydown.enter.self.prevent="triggerScenario(scenario.prompt)"
          @keydown.space.self.prevent="triggerScenario(scenario.prompt)"
          class="p-3.5 rounded-xl glass-card-sub border border-white/[0.08] hover:border-indigo-500/40 hover:bg-white/[0.06] hover:-translate-y-0.5 hover:shadow-md hover:shadow-indigo-500/10 transition-all duration-200 flex items-center justify-between shadow-sm cursor-pointer active:scale-[0.99] group focus:outline-none focus:ring-1 focus:ring-indigo-500/40 select-none"
          :class="{ 'opacity-50 cursor-not-allowed': isStreaming }"
          :title="`一键提问: ${scenario.prompt}`"
        >
          <div class="flex items-start space-x-3 min-w-0 pr-2">
            <span
              class="p-2 rounded-lg border shrink-0 transition-transform duration-200 group-hover:scale-110 flex items-center justify-center shadow-sm"
              :class="[scenario.iconBg, scenario.iconColor]"
            >
              <!-- 矢量 SVG 图标 -->
              <!-- 超温告警图标 -->
              <svg v-if="scenario.iconType === 'overheat'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343a7.975 7.975 0 012.343 5.657c0 2.12-.835 4.16-2.342 5.657z" />
              </svg>
              <!-- 算力借用图标 -->
              <svg v-else-if="scenario.iconType === 'borrow'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <!-- 规程检索图标 -->
              <svg v-else-if="scenario.iconType === 'regulation'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </span>

            <div class="min-w-0 flex-1">
              <div class="flex items-center space-x-2">
                <span class="font-medium text-zinc-100 group-hover:text-indigo-400 transition-colors glass-text text-xs sm:text-sm truncate">
                  {{ scenario.title }}
                </span>
                <span
                  class="text-[10px] px-1.5 py-0.5 rounded font-mono shrink-0 border"
                  :class="scenario.badgeClass"
                >
                  {{ scenario.category }}
                </span>
              </div>
              <p class="text-[11px] text-zinc-400 group-hover:text-zinc-300 mt-1 line-clamp-2 leading-relaxed">
                {{ scenario.prompt }}
              </p>
            </div>
          </div>

          <!-- 右侧操作区：支持填入输入框与一键直接提问 -->
          <div class="flex items-center space-x-1 shrink-0 ml-1.5">
            <button
              type="button"
              @click.stop="handleFill(scenario.prompt)"
              @keydown.enter.stop.prevent="handleFill(scenario.prompt)"
              @keydown.space.stop.prevent="handleFill(scenario.prompt)"
              class="opacity-70 hover:opacity-100 sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100 focus:opacity-100 p-1.5 rounded-lg hover:bg-white/[0.1] text-zinc-400 hover:text-zinc-200 transition-all focus:outline-none focus:ring-1 focus:ring-indigo-500/40"
              title="填入输入框二次编辑"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <div
              class="p-1 text-zinc-500 group-hover:text-indigo-400 group-hover:translate-x-0.5 transition-all"
              title="一键直接提问"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </div>
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

const emit = defineEmits(['select', 'fill'])

const recommendedScenarios = [
  {
    id: 'overheat',
    iconType: 'overheat',
    title: '超温告警排查',
    category: '监控 · 闭环提单',
    prompt: 'DEV-SRV-201 告警超温，查一下并按规章自动提单',
    iconColor: 'text-rose-400',
    iconBg: 'bg-rose-500/10 border-rose-500/20',
    badgeClass: 'text-rose-400 border-rose-500/20 bg-rose-500/10',
  },
  {
    id: 'borrow',
    iconType: 'borrow',
    title: '算力节点借用',
    category: '资源 · 借还登记',
    prompt: '借用 DEV-SRV-202 服务器，用途为大模型微调实验，期限 3 天',
    iconColor: 'text-cyan-400',
    iconBg: 'bg-cyan-500/10 border-cyan-500/20',
    badgeClass: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/10',
  },
  {
    id: 'regulation',
    iconType: 'regulation',
    title: '用电防火规程',
    category: '合规 · 规程溯源',
    prompt: '查一下机房用电安全和防火巡检的相关规定',
    iconColor: 'text-emerald-400',
    iconBg: 'bg-emerald-500/10 border-emerald-500/20',
    badgeClass: 'text-emerald-400 border-emerald-500/20 bg-emerald-500/10',
  },
]

function triggerScenario(prompt) {
  if (props.isStreaming) return
  emit('select', prompt)
}

function handleFill(prompt) {
  if (props.isStreaming) return
  emit('fill', prompt)
}

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
