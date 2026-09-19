<template>
  <div class="border-t glass-panel p-3">
    <!-- 顶部辅助工具条：身份状态标签与权限指引入口 -->
    <div class="flex items-center justify-between pb-2 px-0.5 text-xs">
      <!-- 身份权限气泡组件 -->
      <RolePermissionPopover
        :currentUser="currentUser"
        @fill-prompt="handleFillPrompt"
      />

      <div class="hidden sm:flex items-center space-x-2 text-[10.5px] text-zinc-400 font-mono select-none">
        <span>Enter 发送</span>
        <span class="text-zinc-600">·</span>
        <span>Shift+Enter 换行</span>
      </div>
    </div>

    <!-- 输入主区域 (Linear Minimalist Input) -->
    <div class="relative flex items-end space-x-2 chat-textarea-wrapper bg-black/30 backdrop-blur-sm border border-white/[0.08] focus-within:border-indigo-500/60 rounded-xl p-1.5 transition-all shadow-sm">
      <textarea
        ref="inputRef"
        v-model="inputContent"
        @keydown="handleKeyDown"
        :disabled="isLoading"
        rows="2"
        placeholder="输入运维指令或提问... (可点击上方身份标签查看权限与推荐提示词)"
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
import RolePermissionPopover from './RolePermissionPopover.vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false,
  },
  currentUser: {
    type: Object,
    default: () => ({
      username: 'student',
      real_name: '李同学',
      role: 'STUDENT',
      department: '计算机学院',
    }),
  },
})

const emit = defineEmits(['send', 'abort'])

const inputContent = ref('')
const inputRef = ref(null)

function handleKeyDown(e) {
  if (e.isComposing) return
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

function setInput(text) {
  inputContent.value = text || ''
  nextTick(() => {
    inputRef.value?.focus()
  })
}

function sendInput(text) {
  if (props.isLoading) return
  if (text !== undefined && text !== null) {
    inputContent.value = text
  }
  handleSend()
}

function focus() {
  inputRef.value?.focus()
}

function clear() {
  inputContent.value = ''
}

function handleFillPrompt(prompt) {
  setInput(prompt)
}

defineExpose({
  setInput,
  sendInput,
  focus,
  clear,
  inputContent,
})
</script>

<style>
/* 明亮模式适配 */
html.light .chat-textarea-wrapper {
  background: rgba(255, 255, 255, 0.85) !important;
  border-color: rgba(226, 232, 240, 0.95) !important;
}
html.light .chat-textarea-wrapper textarea {
  color: #0f172a !important;
}
html.light .chat-textarea-wrapper textarea::placeholder {
  color: #94a3b8 !important;
}
</style>
