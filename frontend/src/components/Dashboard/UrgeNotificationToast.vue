<template>
  <div>
    <!-- 1. 收敛状态 (Collapsed Compact Pill: 关联设备已在系统中归还，默认呈现轻巧收敛胶囊条) -->
    <Transition
      enter-active-class="transform transition ease-out duration-300"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-4"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 sm:translate-x-0"
      leave-to-class="opacity-0 sm:translate-x-4"
    >
      <div
        v-if="modelValue && notification && isResolvedReturned && !isExpanded"
        @click="toggleExpand"
        class="fixed top-16 right-3 sm:right-6 z-50 flex items-center space-x-2.5 px-3.5 py-2 rounded-full border shadow-xl backdrop-blur-xl transition-all cursor-pointer select-none group"
        :class="[
          theme === 'light'
            ? 'bg-white/95 border-emerald-300 text-slate-800 hover:bg-emerald-50/80 shadow-emerald-200/40 ring-1 ring-emerald-400/20'
            : 'bg-zinc-950/90 border-emerald-500/40 text-zinc-100 hover:bg-zinc-900/90 shadow-emerald-950/50 ring-1 ring-emerald-500/20'
        ]"
        role="alert"
        title="点击展开查看历史逾期催收与归还记录"
      >
        <!-- 翡翠绿已解决徽标 (精致对勾图标) -->
        <span class="w-5 h-5 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shrink-0 text-emerald-400">
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </span>

        <div class="flex items-center space-x-1.5 text-xs font-sans">
          <span class="font-mono text-cyan-400 font-semibold">{{ notification.asset_no || '资产' }}</span>
          <span class="text-emerald-400 font-medium">逾期催收已解决</span>
          <span class="text-zinc-500 text-[11px] font-sans">(已归还入库)</span>
        </div>

        <span class="text-[10px] text-zinc-400 bg-white/[0.06] px-1.5 py-0.5 rounded border border-white/[0.08] group-hover:text-cyan-300 transition-colors">
          点击查看
        </span>

        <!-- 展开下箭头图标 -->
        <svg class="w-3.5 h-3.5 text-zinc-400 group-hover:text-zinc-200 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>

        <!-- 关闭按钮 -->
        <button
          @click.stop="close"
          class="p-0.5 rounded-full text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.1] transition-colors ml-1"
          title="关闭提示"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </Transition>

    <!-- 2. 展开大卡片状态 (Expanded Card: 未归还时保持展开，或归还后点击收敛条再次查看) -->
    <Transition
      enter-active-class="transform transition ease-out duration-300"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-4"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 sm:translate-x-0"
      leave-to-class="opacity-0 sm:translate-x-4"
    >
      <div
        v-if="modelValue && notification && (!isResolvedReturned || isExpanded)"
        class="fixed top-16 right-3 sm:right-6 z-50 max-w-sm sm:max-w-md w-[calc(100vw-1.5rem)] rounded-2xl border p-4 shadow-2xl transition-all"
        :class="[
          isResolvedReturned
            ? (theme === 'light'
                ? 'bg-white/95 backdrop-blur-xl border-emerald-300/80 shadow-emerald-200/50 text-slate-800'
                : 'bg-zinc-950/90 backdrop-blur-xl border-emerald-500/35 shadow-emerald-950/40 text-zinc-100')
            : (theme === 'light'
                ? 'bg-white/95 backdrop-blur-xl border-rose-300/80 shadow-rose-200/50 text-slate-800'
                : 'bg-zinc-950/90 backdrop-blur-xl border-rose-500/35 shadow-rose-950/40 text-zinc-100')
        ]"
        role="alert"
      >
        <!-- 头部：警示/解决状态、折叠与关闭按钮 -->
        <div class="flex items-start justify-between gap-3 pb-2.5 border-b" :class="theme === 'light' ? 'border-slate-200/80' : 'border-white/[0.08]'">
          <div class="flex items-center space-x-2">
            <!-- 动态呼吸微光微标 (已归还为常亮绿标，未归还已读为呼吸绿标，未归还未读为呼吸红标) -->
            <span class="relative flex h-3 w-3 shrink-0">
              <span
                v-if="!isResolvedReturned"
                class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
                :class="notification.is_read ? 'bg-emerald-400' : 'bg-rose-400'"
              ></span>
              <span
                class="relative inline-flex rounded-full h-3 w-3"
                :class="isResolvedReturned || notification.is_read ? 'bg-emerald-500' : 'bg-rose-500'"
              ></span>
            </span>

            <span
              class="font-semibold text-xs tracking-wide flex items-center gap-1.5"
              :class="isResolvedReturned || notification.is_read ? 'text-emerald-500' : 'text-rose-500'"
            >
              <span>{{ notification.notice_type === 'SYSTEM' ? '系统运行状态' : '超期催收站内待办' }}</span>

              <!-- 状态胶囊药丸 -->
              <span
                v-if="isResolvedReturned"
                class="px-1.5 py-0.2 rounded text-[10px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1"
              >
                <span>✓ 已解决归还</span>
              </span>
              <span
                v-else-if="notification.is_read"
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

          <!-- 右上角控制按钮：收起与关闭 -->
          <div class="flex items-center space-x-1">
            <!-- 仅在归还解决后可折叠为收敛状态 -->
            <button
              v-if="isResolvedReturned"
              @click="toggleExpand"
              class="p-1 rounded-lg transition-colors text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.08]"
              :class="theme === 'light' ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-100' : 'text-zinc-400 hover:text-zinc-200'"
              title="收起为收敛状态"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
            </button>

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
        </div>

        <!-- 中间内容区 -->
        <div class="py-3 space-y-2">
          <!-- 已归还闭环提示横幅 -->
          <div
            v-if="isResolvedReturned"
            class="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center space-x-2"
          >
            <svg class="w-4 h-4 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="leading-relaxed">关联设备已于系统中验收入库归还，原逾期催收状态已解除闭环。</span>
          </div>

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
          <!-- 查看催告公单 (针对设备催促公文开放，即使已归还仍可查看历史公单) -->
          <button
            v-if="notification.asset_no"
            @click="handleViewNotice"
            class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1 transition-all active:scale-95 shadow-sm"
            :class="[
              isResolvedReturned
                ? (theme === 'light' ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300' : 'bg-zinc-850 hover:bg-zinc-800 text-zinc-300 border-white/[0.1]')
                : (theme === 'light' ? 'bg-rose-50 hover:bg-rose-100 text-rose-700 border-rose-300' : 'bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border-rose-500/30')
            ]"
          >
            <svg class="w-3.5 h-3.5" :class="isResolvedReturned ? 'text-cyan-400' : 'text-rose-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>查看催告公单</span>
          </button>

          <!-- 1. 若已归还解决：提供快捷“收起”按钮与“关闭”按钮 -->
          <template v-if="isResolvedReturned">
            <button
              @click="toggleExpand"
              class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1 transition-all active:scale-95 text-zinc-400 hover:text-zinc-200 border-white/[0.08] hover:bg-white/[0.06]"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
              <span>收起状态条</span>
            </button>
            <button
              @click="close"
              class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1 transition-all active:scale-95 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/[0.1]"
            >
              <span>好的 / 关闭</span>
            </button>
          </template>

          <!-- 2. 未归还且未读状态：我知道了 / 标为已读 (标为已读后保持当前卡片展开呈现，不主动关闭，直至系统中办理归还) -->
          <button
            v-else-if="!notification.is_read && notification.id"
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

          <!-- 3. 未归还但已读：已处理 / 关闭 -->
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
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
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
  assets: {
    type: Array,
    default: () => [],
  },
  overdueMap: {
    type: Object,
    default: () => ({}),
  },
  theme: {
    type: String,
    default: 'dark',
  },
})

const emit = defineEmits(['update:modelValue', 'viewNotice', 'markRead'])

const marking = ref(false)

// 关联设备计算
const relatedAsset = computed(() => {
  if (!props.notification?.asset_no) return null
  return (props.assets || []).find((a) => a.asset_no === props.notification.asset_no)
})

// 判定关联设备是否在系统中已处于归还状态 (已解决逾期)
const isResolvedReturned = computed(() => {
  if (!props.notification?.asset_no) return false
  // 1. 若在当前 assets 列表中存在，且借用状态已为 AVAILABLE，则已成功归还
  if (relatedAsset.value && relatedAsset.value.borrow_status === 'AVAILABLE') {
    return true
  }
  // 2. 若不在 overdueMap 中，且借用人为空，也表明已归还
  if (props.overdueMap && !props.overdueMap[props.notification.asset_no]) {
    if (relatedAsset.value && !relatedAsset.value.borrower) {
      return true
    }
  }
  return false
})

// 控制展开卡片状态
// 核心状态机：
// - 若已归还解决：默认直接呈现收敛状态 (isExpanded = false)，点击一下即可展开再次查看
// - 若尚未归还：默认保持展开卡片状态 (isExpanded = true)
const isExpanded = ref(false)

watch(
  [isResolvedReturned, () => props.notification?.id],
  ([resolved]) => {
    if (resolved) {
      isExpanded.value = false
    } else {
      isExpanded.value = true
    }
  },
  { immediate: true }
)

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

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
    // 标记已读后，在本地将 notification.is_read 更新为 true，保持当前展开卡片状态呈现 (不强制 close)
    if (props.notification) {
      props.notification.is_read = true
    }
    emit('markRead', props.notification.id)
  } catch (err) {
    console.error('标记通知已读失败:', err)
  } finally {
    marking.value = false
  }
}
</script>
