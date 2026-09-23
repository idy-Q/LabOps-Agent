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
        <!-- 语音输入按钮 (浏览器原生 Web Speech API STT) -->
        <button
          v-if="isSpeechSupported"
          @click="toggleSpeechRecognition"
          :disabled="isLoading"
          type="button"
          class="chat-mic-btn relative p-2 rounded-lg transition-all shadow-sm flex items-center justify-center active:scale-95 border disabled:opacity-40 disabled:cursor-not-allowed"
          :class="[
            isListening
              ? 'is-listening bg-rose-500/20 text-rose-400 border-rose-500/50 hover:bg-rose-500/30 ring-2 ring-rose-500/30'
              : 'text-zinc-400 hover:text-zinc-200 bg-zinc-900/60 hover:bg-zinc-800/80 border-white/[0.08]'
          ]"
          :title="isListening ? '录音识别中，点击停止' : '点击通过麦克风语音输入 (中文识别)'"
        >
          <!-- 录音呼吸光晕脉冲动效 -->
          <span
            v-if="isListening"
            class="animate-ping absolute inset-0 rounded-lg bg-rose-500/30 pointer-events-none"
          ></span>
          <!-- 麦克风图标 -->
          <svg class="w-4 h-4 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>

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
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
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

// 浏览器原生语音识别 (STT - Web Speech API) 能力探测与生命周期管控
const SpeechRecognition = typeof window !== 'undefined'
  ? (window.SpeechRecognition || window.webkitSpeechRecognition || null)
  : null
const isSpeechSupported = ref(!!SpeechRecognition)
const isListening = ref(false)
let recognition = null
let baseContentBeforeSpeech = ''

function startListening() {
  if (!isSpeechSupported.value || props.isLoading) return
  // 启动前先彻底停止清理可能存在的前序实例，杜绝并发竞争
  stopListening()

  try {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition
    const currentRec = new SpeechRec()
    recognition = currentRec
    currentRec.lang = 'zh-CN'
    currentRec.continuous = true
    currentRec.interimResults = true

    baseContentBeforeSpeech = inputContent.value ? inputContent.value.trim() + ' ' : ''

    currentRec.onstart = () => {
      if (recognition === currentRec) {
        isListening.value = true
      }
    }

    currentRec.onresult = (event) => {
      if (recognition !== currentRec) return
      let interimTranscript = ''
      let finalTranscript = ''
      for (let i = 0; i < event.results.length; ++i) {
        const item = event.results[i]
        const transcript = item[0]?.transcript || ''
        if (item.isFinal) {
          finalTranscript += transcript
        } else {
          interimTranscript += transcript
        }
      }
      inputContent.value = baseContentBeforeSpeech + finalTranscript + interimTranscript
    }

    currentRec.onerror = (event) => {
      console.warn('语音识别事件:', event.error)
      if (recognition === currentRec) {
        isListening.value = false
        recognition = null
      }
    }

    currentRec.onend = () => {
      if (recognition === currentRec) {
        isListening.value = false
        recognition = null
      }
    }

    currentRec.start()
  } catch (err) {
    console.error('启动语音识别失败:', err)
    isListening.value = false
    recognition = null
  }
}

function stopListening() {
  if (recognition) {
    const rec = recognition
    recognition = null
    rec.onresult = null
    rec.onerror = null
    rec.onend = null
    try {
      rec.stop()
    } catch {}
  }
  isListening.value = false
}

function toggleSpeechRecognition() {
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

// 若模型正在推理流式生成中，立即切断并中止语音输入
watch(
  () => props.isLoading,
  (loading) => {
    if (loading && isListening.value) {
      stopListening()
    }
  }
)

onBeforeUnmount(() => {
  stopListening()
})

function handleKeyDown(e) {
  if (e.isComposing) return
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleSend() {
  if (isListening.value) {
    stopListening()
  }
  const trimmed = inputContent.value.trim()
  if (!trimmed || props.isLoading) return
  emit('send', trimmed)
  inputContent.value = ''
  baseContentBeforeSpeech = ''
}

function setInput(text) {
  inputContent.value = text || ''
  baseContentBeforeSpeech = ''
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
  if (isListening.value) {
    stopListening()
  }
  inputContent.value = ''
  baseContentBeforeSpeech = ''
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
  isListening,
  toggleSpeechRecognition,
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
html.light .chat-mic-btn:not(.is-listening) {
  background: rgba(241, 245, 249, 0.9) !important;
  border-color: rgba(226, 232, 240, 0.9) !important;
  color: #64748b !important;
}
html.light .chat-mic-btn:not(.is-listening):hover {
  background: rgba(226, 232, 240, 0.9) !important;
  color: #0f172a !important;
}
html.light .chat-mic-btn.is-listening {
  background: rgba(254, 226, 226, 0.95) !important;
  border-color: rgba(244, 63, 94, 0.6) !important;
  color: #e11d48 !important;
}
</style>
