<template>
  <div ref="containerRef" class="flex-1 overflow-y-auto p-4 space-y-4 text-slate-200">
    <!-- 欢迎状态卡片 -->
    <div
      v-if="messages.length === 0"
      class="h-full flex flex-col items-center justify-center text-center p-6 space-y-4 max-w-md mx-auto my-auto"
    >
      <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-2xl">
        🤖
      </div>
      <div class="space-y-1.5">
        <h2 class="text-base font-bold text-slate-100">高校机房智能运维管家 (LabOps-Agent)</h2>
        <p class="text-xs text-slate-400 leading-relaxed">
          基于原生 ReAct 架构与大模型推理驱动。具备机房硬件实时探针感知、温度超标（>40℃）自动工单闭环、资产设备借还台账与安全规章检索能力。
        </p>
      </div>
      <div class="w-full pt-2 grid grid-cols-1 gap-2 text-left text-xs">
        <div class="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 flex items-start space-x-2.5">
          <span class="text-base">⚡</span>
          <div>
            <div class="font-medium text-slate-200">全白盒推理感知</div>
            <div class="text-[11px] text-slate-400">细粒度展开思考过程与函数工具入参返回值</div>
          </div>
        </div>
        <div class="p-3 rounded-xl bg-slate-800/40 border border-slate-700/50 flex items-start space-x-2.5">
          <span class="text-base">🔄</span>
          <div>
            <div class="font-medium text-slate-200">左右看板双向联动</div>
            <div class="text-[11px] text-slate-400">智能提单与借还操作即时同步右侧 SQLite 真实业务数据</div>
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
      <!-- 用户提问气泡 -->
      <div
        v-if="msg.role === 'user'"
        class="flex items-start justify-end space-x-2"
      >
        <div class="max-w-[85%] rounded-2xl rounded-tr-sm bg-emerald-600 px-4 py-2.5 text-white text-xs sm:text-sm shadow-md leading-relaxed whitespace-pre-wrap">
          {{ msg.content }}
        </div>
        <div class="w-7 h-7 rounded-full bg-emerald-700 flex items-center justify-center text-xs font-bold shrink-0 text-emerald-100 shadow">
          师
        </div>
      </div>

      <!-- Agent 助手回复复合体 -->
      <div
        v-else-if="msg.role === 'assistant'"
        class="flex items-start space-x-2.5"
      >
        <div class="w-7 h-7 rounded-xl bg-gradient-to-br from-indigo-500 to-emerald-500 flex items-center justify-center text-xs font-bold shrink-0 text-white shadow-md">
          AI
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

          <!-- 4. 助手最终正文回答 -->
          <div
            v-if="msg.content"
            class="p-4 rounded-2xl rounded-tl-sm bg-slate-800/80 border border-slate-700/60 text-xs sm:text-sm text-slate-100 leading-relaxed shadow-md space-y-2"
          >
            <div
              class="prose prose-invert prose-xs max-w-none whitespace-pre-wrap break-words font-sans leading-relaxed"
              v-html="renderMarkdown(msg.content)"
            ></div>
          </div>

          <!-- 流式打字与决策状态指示灯 -->
          <div
            v-if="msg.isStreaming && !msg.content"
            class="flex items-center space-x-1.5 text-xs text-slate-400 py-1"
          >
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce"></span>
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.2s]"></span>
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.4s]"></span>
            <span class="text-[11px] text-slate-400 ml-1">
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

  // 2. 加粗语法 **text**
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-emerald-300">$1</strong>')

  // 3. 行内代码 `code`
  escaped = escaped.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700/60 text-amber-300 font-mono text-[11px]">$1</code>')

  return escaped
}
</script>
