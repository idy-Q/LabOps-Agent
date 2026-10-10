<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="modelValue"
        @keydown.esc.window="close"
        class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-5 backdrop-blur-md overflow-hidden transition-colors"
        :class="theme === 'light' ? 'bg-slate-900/40' : 'bg-black/75'"
        @mousedown="handleBackdropMouseDown"
        @mouseup="handleBackdropMouseUp"
      >
        <!-- 弹窗核心卡片容器 -->
        <div
          class="w-full max-w-2xl rounded-3xl border p-5 sm:p-6 space-y-4 flex flex-col max-h-[92vh] overflow-hidden backdrop-blur-2xl transition-all"
          :class="[
            theme === 'light'
              ? 'bg-white/95 border-slate-200/90 text-slate-800 shadow-[0_25px_80px_-15px_rgba(15,23,42,0.18)] ring-1 ring-slate-900/[0.05]'
              : 'bg-zinc-900/95 border-white/[0.12] text-zinc-100 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] ring-1 ring-white/[0.05]'
          ]"
        >
          <!-- 移动端顶部抓手装饰条 -->
          <div
            class="w-10 h-1 rounded-full mx-auto -mt-1 sm:hidden shrink-0"
            :class="theme === 'light' ? 'bg-slate-300' : 'bg-white/20'"
          ></div>

          <!-- 弹窗顶栏 Header -->
          <div
            class="flex items-center justify-between border-b pb-3 shrink-0"
            :class="theme === 'light' ? 'border-slate-200/80' : 'border-white/[0.08]'"
          >
            <div class="flex items-center space-x-3 min-w-0">
              <span
                class="p-2.5 rounded-2xl border flex items-center justify-center shrink-0 shadow-sm"
                :class="[
                  theme === 'light'
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-600 shadow-emerald-50'
                    : 'bg-zinc-950/80 border-white/[0.1] text-emerald-400'
                ]"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
              </span>
              <div class="min-w-0">
                <div class="flex items-center space-x-2 flex-wrap gap-y-1">
                  <h3
                    class="text-base sm:text-lg font-semibold tracking-tight truncate"
                    :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'"
                  >
                    {{ isEditMode ? '编辑机房规章规程' : '录入新增机房规章规程' }}
                  </h3>
                  <span
                    class="text-[10px] px-2 py-0.5 rounded-full font-mono font-medium border"
                    :class="[
                      theme === 'light'
                        ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                        : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
                    ]"
                  >
                    {{ isEditMode ? '修改并同步安全规约库' : '规约细则自动解析入库' }}
                  </span>
                </div>
                <p
                  class="text-[11px] truncate mt-0.5"
                  :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                >
                  {{ isEditMode ? '修改正文条款或元数据后，系统将自动重新拆解细则并同步至安全规约库' : '支持标准 Markdown 语法，保存后系统将自动按章节与条款拆解规约细则并同步入库' }}
                </p>
              </div>
            </div>

            <button
              @click="close"
              class="p-2 rounded-full transition-all shrink-0 active:scale-90"
              :class="[
                theme === 'light'
                  ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
                  : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.08]'
              ]"
              title="关闭 (Esc)"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- 错误与成功提示条 -->
          <div
            v-if="errorMsg"
            class="p-2.5 rounded-xl border text-xs flex items-center space-x-2 animate-fade-in shrink-0"
            :class="[
              theme === 'light'
                ? 'bg-rose-50 border-rose-200 text-rose-700'
                : 'bg-rose-500/15 border-rose-500/30 text-rose-300'
            ]"
          >
            <svg class="w-4 h-4 shrink-0 text-rose-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ errorMsg }}</span>
          </div>

          <div
            v-if="successMsg"
            class="p-2.5 rounded-xl border text-xs flex items-center space-x-2 animate-fade-in shrink-0"
            :class="[
              theme === 'light'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
            ]"
          >
            <svg class="w-4 h-4 shrink-0 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>{{ successMsg }}</span>
          </div>

          <!-- 表单主体区 (支持纵向平滑滚动) -->
          <form @submit.prevent="handleSubmit" class="flex-1 overflow-y-auto pr-1 space-y-3.5 custom-scrollbar text-xs">
            <!-- 规程标题 -->
            <div class="space-y-1">
              <label
                class="font-medium flex items-center gap-1"
                :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
              >
                规程标题 <span class="text-rose-400">*</span>
              </label>
              <input
                v-model="form.title"
                type="text"
                placeholder="例如: 机房精密空调温湿度联动调控操作规范"
                required
                minlength="2"
                class="w-full rounded-xl px-3.5 py-2 text-xs border outline-none transition-all shadow-inner"
                :class="[
                  theme === 'light'
                    ? 'bg-slate-50 border-slate-200/90 text-slate-800 placeholder-slate-400 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15'
                    : 'bg-zinc-950/60 border-white/[0.08] text-zinc-100 placeholder-zinc-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30'
                ]"
              />
            </div>

            <!-- 业务分类 与 版本号 -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="space-y-1">
                <label
                  class="font-medium flex items-center gap-1"
                  :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                >
                  规程业务分类 <span class="text-rose-400">*</span>
                </label>
                <select
                  v-model="form.category"
                  required
                  class="w-full rounded-xl px-3.5 py-2 text-xs border outline-none transition-all"
                  :class="[
                    theme === 'light'
                      ? 'bg-slate-50 border-slate-200/90 text-slate-800 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15'
                      : 'bg-zinc-950 border-white/[0.08] text-zinc-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30'
                  ]"
                >
                  <option value="用电规范">用电规范</option>
                  <option value="应急条例">应急条例</option>
                  <option value="维保规程">维保规程</option>
                  <option value="安全制度">安全制度</option>
                </select>
              </div>

              <div class="space-y-1">
                <label
                  class="font-medium"
                  :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                >
                  规程版本号
                </label>
                <input
                  v-model="form.version"
                  type="text"
                  placeholder="例如: 2026版"
                  class="w-full rounded-xl px-3.5 py-2 text-xs border outline-none transition-all shadow-inner font-mono"
                  :class="[
                    theme === 'light'
                      ? 'bg-slate-50 border-slate-200/90 text-slate-800 placeholder-slate-400 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15'
                      : 'bg-zinc-950/60 border-white/[0.08] text-zinc-100 placeholder-zinc-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30'
                  ]"
                />
              </div>
            </div>

            <!-- 颁布实施日期 与 自定义规程编号 -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="space-y-1">
                <label
                  class="font-medium flex items-center gap-1"
                  :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                >
                  颁布实施日期 <span class="text-rose-400">*</span>
                </label>
                <input
                  v-model="form.effective_date"
                  type="date"
                  required
                  class="w-full rounded-xl px-3.5 py-2 text-xs border outline-none transition-all font-mono"
                  :class="[
                    theme === 'light'
                      ? 'bg-slate-50 border-slate-200/90 text-slate-800 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15'
                      : 'bg-zinc-950 border-white/[0.08] text-zinc-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30'
                  ]"
                />
              </div>

              <div class="space-y-1">
                <label
                  class="font-medium"
                  :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                >
                  {{ isEditMode ? '规程唯一编号 (已固化不可修改)' : '自定义规程编号 (可选)' }}
                </label>
                <input
                  v-model="form.doc_id"
                  type="text"
                  :disabled="isEditMode"
                  :placeholder="isEditMode ? '编号已固化不可修改' : '留空自动按 DOC-RAG-XXX 递增'"
                  class="w-full rounded-xl px-3.5 py-2 text-xs border outline-none transition-all shadow-inner font-mono"
                  :class="[
                    isEditMode ? 'opacity-60 cursor-not-allowed bg-zinc-800/40' : '',
                    theme === 'light'
                      ? 'bg-slate-50 border-slate-200/90 text-slate-800 placeholder-slate-400 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15'
                      : 'bg-zinc-950/60 border-white/[0.08] text-zinc-100 placeholder-zinc-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30'
                  ]"
                />
              </div>
            </div>

            <!-- 正文 Markdown 内容 -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <label
                  class="font-medium flex items-center gap-1"
                  :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                >
                  规程正文 Markdown 内容 <span class="text-rose-400">*</span>
                </label>
                <button
                  type="button"
                  @click="fillExampleContent"
                  class="text-[11px] font-medium flex items-center space-x-1 transition-colors hover:underline"
                  :class="theme === 'light' ? 'text-emerald-700 hover:text-emerald-800' : 'text-emerald-400 hover:text-emerald-300'"
                >
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>填入标准 Markdown 模板</span>
                </button>
              </div>

              <textarea
                v-model="form.content"
                rows="7"
                placeholder="推荐格式：&#10;## 第一条 章节标题&#10;1. 具体条款内容&#10;&#10;## 第二条 核心指标与红线要求&#10;1. 规定数值与操作要求"
                required
                minlength="10"
                class="w-full rounded-xl px-3.5 py-2.5 text-xs font-mono border outline-none transition-all resize-y shadow-inner leading-relaxed"
                :class="[
                  theme === 'light'
                    ? 'bg-slate-50 border-slate-200/90 text-slate-800 placeholder-slate-400 focus:bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/15'
                    : 'bg-zinc-950/60 border-white/[0.08] text-zinc-100 placeholder-zinc-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/30'
                ]"
              ></textarea>

              <div
                class="p-2.5 rounded-xl border text-[11px] flex items-center space-x-2"
                :class="[
                  theme === 'light'
                    ? 'bg-slate-50 border-slate-200 text-slate-600'
                    : 'bg-zinc-950/40 border-white/[0.06] text-zinc-400'
                ]"
              >
                <span>💡</span>
                <span>语义解析器将按 <code class="px-1.5 py-0.5 rounded font-mono font-medium border" :class="theme === 'light' ? 'bg-white border-slate-200 text-emerald-700' : 'bg-black/40 border-white/[0.08] text-emerald-400'">##</code> 章节和数字条款自动分块并向量化存储。</span>
              </div>
            </div>

            <!-- 底部提交与取消 -->
            <div
              class="pt-3 border-t flex items-center justify-end space-x-2.5 shrink-0"
              :class="theme === 'light' ? 'border-slate-200/80' : 'border-white/[0.08]'"
            >
              <button
                type="button"
                @click="close"
                class="px-4 py-2 rounded-xl text-xs font-medium border transition-all active:scale-95"
                :class="[
                  theme === 'light'
                    ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
                    : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/[0.06]'
                ]"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="isSubmitting"
                class="px-5 py-2 rounded-xl text-white font-medium text-xs shadow-md active:scale-95 disabled:opacity-50 transition-all flex items-center space-x-1.5"
                :class="[
                  theme === 'light'
                    ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/20'
                    : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-950/40'
                ]"
              >
                <span v-if="isSubmitting" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>{{ isSubmitting ? (isEditMode ? '保存修改并更新向量中...' : '解析切块与存库中...') : (isEditMode ? '保存修改并重新切块' : '保存规程并生成切块') }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  theme: {
    type: String,
    default: 'dark', // 'light' | 'dark'
  },
  editDoc: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const isEditMode = computed(() => !!props.editDoc)
const isSubmitting = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const form = reactive({
  doc_id: '',
  title: '',
  category: '用电规范',
  version: '2026版',
  effective_date: new Date().toISOString().slice(0, 10),
  content: '',
})

// 防误触判定：mousedown + mouseup 双重校验
let isMouseDownOnBackdrop = false

function handleBackdropMouseDown(e) {
  isMouseDownOnBackdrop = (e.target === e.currentTarget)
}

function handleBackdropMouseUp(e) {
  if (isMouseDownOnBackdrop && e.target === e.currentTarget) {
    close()
  }
  isMouseDownOnBackdrop = false
}

function close() {
  emit('update:modelValue', false)
}

function resetForm() {
  form.doc_id = ''
  form.title = ''
  form.category = '用电规范'
  form.version = '2026版'
  form.effective_date = new Date().toISOString().slice(0, 10)
  form.content = ''
  errorMsg.value = ''
  successMsg.value = ''
}

function fillExampleContent() {
  form.content = `## 第一条 设备接入与供电负荷前置核算
1. 任何新增或调动服务器设备接入机架前，必须严格核算其实测最大功率，严禁导致单机架总负荷超过 4.5kW 设计阈值。

## 第二条 巡检监测与异常处置要求
1. 运维人员在日常巡检中必须密切监测机架 PDU 输出电流与环境温度，遇有接近红线情况立即启动负载分流与降级预案。`
}

function reconstructMarkdownFromChunks(chunks) {
  if (!chunks || chunks.length === 0) return ''
  const sections = []
  let currentSec = null
  let secContent = []

  for (const ck of chunks) {
    const rawTitle = (ck.section_title || '').trim()
    // 匹配章节名，剥离附带在 section_title 后面的条款序号与内容（如 "第二条 功耗上限 1. 单机架..." -> "第二条 功耗上限"）
    const match = rawTitle.match(/^(.*?)\s+\d+\..*$/)
    const cleanSec = match ? match[1].trim() : rawTitle

    if (cleanSec !== currentSec) {
      if (currentSec !== null) {
        sections.push({ section: currentSec, text: secContent.join('\n') })
      }
      currentSec = cleanSec
      secContent = []
    }
    const content = (ck.chunk_content || '').trim()
    if (content) {
      secContent.push(content)
    }
  }

  if (currentSec !== null) {
    sections.push({ section: currentSec, text: secContent.join('\n') })
  }

  return sections
    .map(({ section, text }) => {
      if (section) {
        return `## ${section}\n${text}`
      }
      return text
    })
    .join('\n\n')
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      if (props.editDoc) {
        form.doc_id = props.editDoc.doc_id || ''
        form.title = props.editDoc.title || ''
        form.category = props.editDoc.category || '用电规范'
        form.version = props.editDoc.version || '2026版'
        form.effective_date = props.editDoc.effective_date || new Date().toISOString().slice(0, 10)
        if (props.editDoc.content) {
          form.content = props.editDoc.content
        } else if (props.editDoc.chunks && props.editDoc.chunks.length > 0) {
          form.content = reconstructMarkdownFromChunks(props.editDoc.chunks)
        } else {
          form.content = ''
        }
        errorMsg.value = ''
        successMsg.value = ''
      } else {
        resetForm()
      }
    }
  }
)

async function handleSubmit() {
  if (!form.title.trim() || !form.content.trim()) {
    errorMsg.value = '请完整填写规程标题与条款内容'
    return
  }

  isSubmitting.value = true
  errorMsg.value = ''
  successMsg.value = ''

  const payload = {
    title: form.title.trim(),
    category: form.category,
    version: form.version?.trim() || '2026版',
    effective_date: form.effective_date,
    content: form.content.trim(),
  }

  try {
    if (isEditMode.value && props.editDoc?.doc_id) {
      const updated = await api.updateRegulation(props.editDoc.doc_id, payload)
      successMsg.value = `规程《${updated.title}》修改保存成功！已同步更新 ${updated.chunk_count} 个语义切块至向量知识库。`
      emit('saved', updated)
    } else {
      if (form.doc_id?.trim()) {
        payload.doc_id = form.doc_id.trim()
      }
      const created = await api.createRegulation(payload)
      successMsg.value = `规程《${created.title}》录入成功！已自动完成 ${created.chunk_count} 个语义切块并同步至向量知识库。`
      emit('saved', created)
    }

    setTimeout(() => {
      close()
    }, 1000)
  } catch (err) {
    errorMsg.value = err.message || (isEditMode.value ? '修改规程失败，请重试' : '录入新规程失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}
</script>
