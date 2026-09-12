<template>
  <div class="border-t glass-panel p-3">
    <!-- 输入主区域 (Linear Minimalist Input) -->
    <div class="relative flex items-end space-x-2 bg-black/30 backdrop-blur-sm border border-white/[0.08] focus-within:border-indigo-500/60 rounded-xl p-1.5 transition-all shadow-sm">
      <textarea
        ref="inputRef"
        v-model="inputContent"
        @keydown="handleKeyDown"
        :disabled="isLoading"
        rows="2"
        placeholder="输入运维指令或提问... (Enter 发送，Shift+Enter 换行)"
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

defineExpose({
  setInput,
  sendInput,
  focus,
  clear,
  inputContent,
})
</script>
