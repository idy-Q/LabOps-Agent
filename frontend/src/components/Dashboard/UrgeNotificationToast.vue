<template>
  <Transition
    enter-active-class="transform transition ease-out duration-300"
    enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-4"
    enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="opacity-100 sm:translate-x-0"
    leave-to-class="opacity-0 sm:translate-x-4"
  >
    <div
      v-if="modelValue && notification"
      class="fixed top-16 right-3 sm:right-6 z-50 max-w-sm sm:max-w-md w-[calc(100vw-1.5rem)] rounded-2xl border p-4 shadow-2xl transition-all"
      :class="[
        theme === 'light'
          ? 'bg-white/95 backdrop-blur-xl border-rose-300/80 shadow-rose-200/50 text-slate-800'
          : 'bg-zinc-950/90 backdrop-blur-xl border-rose-500/35 shadow-rose-950/40 text-zinc-100'
      ]"
      role="alert"
    >
      <!-- 头部：警示状态与关闭按钮 -->
      <div class="flex items-start justify-between gap-3 pb-2.5 border-b" :class="theme === 'light' ? 'border-slate-200/80' : 'border-white/[0.08]'">
        <div class="flex items-center space-x-2">
          <!-- 动态呼吸微光警示微标 -->
          <span class="relative flex h-3 w-3 shrink-0">
            <span
              class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
              :class="notification.is_read ? 'bg-emerald-400' : 'bg-rose-400'"
            ></span>
            <span
              class="relative inline-flex rounded-full h-3 w-3"
              :class="notification.is_read ? 'bg-emerald-500' : 'bg-rose-500'"
            ></span>
          </span>
          <span
            class="font-semibold text-xs tracking-wide flex items-center gap-1.5"
            :class="notification.is_read ? 'text-emerald-500' : 'text-rose-500'"
          >
            <span>{{ notification.notice_type === 'SYSTEM' ? '系统运行状态' : '超期催收站内待办' }}</span>
            <span
              v-if="notification.is_read"
              class="px-1.5 py-0.2 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
            >
              {{ notification.id === 0 ? '运转正常' : '已查阅' }}
            </span>
            <span
              v-else
              class="px-1.5 py-0.2 rounded text-[10px] font-mono bg-rose-500/10 text-rose-500 border border-rose-500/20"
            >
              紧急督促
            </span>
          </span>
        </div>

        <button
          @click="close"
          class="p-1 rounded-lg transition-colors text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.08]"
          :class="theme === 'light' ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-100' : 'text-zinc-400 hover:text-zinc-200'"
          title="关闭提示"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 中间内容区 -->
      <div class="py-3 space-y-2">
        <h4 class="text-xs font-bold leading-snug" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'">
          {{ notification.title }}
        </h4>
        <p class="text-[11px] leading-relaxed line-clamp-3" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">
          {{ notification.content }}
        </p>

        <!-- 关联资产信息小标签 -->
        <div v-if="notification.asset_no" class="flex items-center justify-between text-[10px] pt-1" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">
          <span class="flex items-center gap-1 font-mono">
            <svg class="w-3 h-3 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
            设备编号: {{ notification.asset_no }}
          </span>
          <span class="font-mono">{{ notification.created_at }}</span>
        </div>
      </div>

      <!-- 底部动作按钮 -->
      <div class="flex items-center justify-end space-x-2 pt-1 border-t" :class="theme === 'light' ? 'border-slate-200/80' : 'border-white/[0.08]'">
        <!-- 查看催告公单 (仅针对设备催促公文开放) -->
        <button
          v-if="notification.asset_no"
          @click="handleViewNotice"
          class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1 transition-all active:scale-95 shadow-sm"
          :class="[
            theme === 'light'
              ? 'bg-rose-50 hover:bg-rose-100 text-rose-700 border-rose-300'
              : 'bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border-rose-500/30'
          ]"
        >
          <svg class="w-3.5 h-3.5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>查看催告公单</span>
        </button>

        <!-- 未读状态：我知道了 / 标为已读 -->
        <button
          v-if="!notification.is_read && notification.id"
          @click="handleMarkRead"
          :disabled="marking"
          class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1 transition-all active:scale-95 disabled:opacity-50"
          :class="[
            theme === 'light'
              ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300'
              : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/[0.1]'
          ]"
        >
          <svg v-if="marking" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ marking ? '处理中...' : '我知道了 / 标为已读' }}</span>
        </button>

        <!-- 已读或系统状态：已处理 / 关闭 -->
        <button
          v-else
          @click="close"
          class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1 transition-all active:scale-95"
          :class="[
            theme === 'light'
              ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300'
              : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/[0.1]'
          ]"
        >
          <span>{{ notification.id === 0 ? '好的 / 关闭' : '已处理 / 关闭' }}</span>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  notification: {
    type: Object,
    default: null,
  },
  theme: {
    type: String,
    default: 'dark',
  },
})

const emit = defineEmits(['update:modelValue', 'viewNotice', 'markRead'])

const marking = ref(false)

function close() {
  emit('update:modelValue', false)
}

function handleViewNotice() {
  const assetNo = props.notification?.asset_no || 'DEV-SRV-201'
  emit('viewNotice', assetNo)
}

async function handleMarkRead() {
  if (!props.notification || !props.notification.id) {
    close()
    return
  }
  marking.value = true
  try {
    await api.markNotificationRead(props.notification.id)
    emit('markRead', props.notification.id)
    close()
  } catch (err) {
    console.error('标记通知已读失败:', err)
  } finally {
    marking.value = false
  }
}
</script>
