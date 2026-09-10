<template>
  <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-4 space-y-3 shadow-sm flex flex-col">
    <!-- 头部栏与过滤控制 -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
      <div class="flex items-center space-x-2">
        <span class="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-semibold text-slate-100">机房运维工单看板</h3>
        <span class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 text-[11px] font-mono">
          {{ filteredTickets.length }} 条
        </span>
      </div>

      <!-- 状态过滤胶囊 -->
      <div class="flex items-center space-x-1 text-xs">
        <button
          v-for="s in statusOptions"
          :key="s.value"
          @click="selectedStatus = s.value"
          :class="[
            'px-2 py-1 rounded-lg text-[11px] transition-all',
            selectedStatus === s.value
              ? 'bg-amber-500/20 text-amber-300 font-medium border border-amber-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          ]"
        >
          {{ s.label }}
        </button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="relative">
      <input
        v-model="keyword"
        type="text"
        placeholder="搜索工单号、标题、关联设备..."
        class="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/60 transition-colors"
      />
      <span v-if="keyword" @click="keyword = ''" class="absolute right-2.5 top-2 text-slate-500 hover:text-slate-300 text-xs cursor-pointer">
        ✕
      </span>
    </div>

    <!-- 表格区域 -->
    <div ref="tableContainerRef" class="overflow-x-auto rounded-xl border border-slate-800/80 max-h-72 overflow-y-auto">
      <table class="w-full text-left text-xs text-slate-300 border-collapse">
        <thead class="bg-slate-950/80 text-[11px] text-slate-400 sticky top-0 uppercase tracking-wider border-b border-slate-800">
          <tr>
            <th class="py-2.5 px-3">工单编号</th>
            <th class="py-2.5 px-3">工单标题与排查内容</th>
            <th class="py-2.5 px-2 text-center">优先级</th>
            <th class="py-2.5 px-2 text-center">状态</th>
            <th class="py-2.5 px-3">关联设备</th>
            <th class="py-2.5 px-3 text-right">流转操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60 font-sans">
          <tr v-if="filteredTickets.length === 0">
            <td colspan="6" class="py-6 text-center text-slate-500 text-xs">
              暂无匹配工单记录
            </td>
          </tr>
          <tr
            v-for="t in filteredTickets"
            :key="t.id"
            :class="[
              'transition-colors hover:bg-slate-800/40 text-xs',
              t.ticket_no === highlightedTicketNo
                ? 'bg-amber-500/25 ring-2 ring-amber-400 animate-pulse font-semibold'
                : ''
            ]"
          >
            <!-- 工单编号 -->
            <td class="py-2.5 px-3 font-mono text-[11px] text-amber-300 whitespace-nowrap">
              <span
                @click="$emit('inspectTicket', t.ticket_no)"
                class="hover:underline cursor-pointer flex items-center gap-1"
                title="点击在对话中查询该工单详情"
              >
                {{ t.ticket_no }}
              </span>
            </td>

            <!-- 标题与排查要求 -->
            <td class="py-2.5 px-3 max-w-xs">
              <div class="font-medium text-slate-200 truncate">{{ t.title }}</div>
              <div class="text-[10px] text-slate-400 truncate">{{ t.description }}</div>
            </td>

            <!-- 优先级 -->
            <td class="py-2.5 px-2 text-center whitespace-nowrap">
              <span :class="['px-1.5 py-0.5 rounded text-[10px] font-medium font-mono', priorityClass(t.priority)]">
                {{ t.priority }}
              </span>
            </td>

            <!-- 状态 -->
            <td class="py-2.5 px-2 text-center whitespace-nowrap">
              <span :class="['px-1.5 py-0.5 rounded text-[10px] font-medium font-mono', statusClass(t.status)]">
                {{ t.status }}
              </span>
            </td>

            <!-- 关联设备 -->
            <td class="py-2.5 px-3 font-mono text-[11px] text-slate-300 whitespace-nowrap">
              {{ t.device_id || '-' }}
            </td>

            <!-- 快速推进操作 -->
            <td class="py-2.5 px-3 text-right whitespace-nowrap">
              <div class="flex items-center justify-end space-x-1">
                <button
                  v-if="t.status === 'PENDING'"
                  @click="$emit('updateStatus', t.id, 'PROCESSING')"
                  class="px-2 py-0.5 rounded bg-blue-900/60 hover:bg-blue-800 text-blue-200 border border-blue-500/30 text-[10px] transition-colors"
                >
                  受理
                </button>
                <button
                  v-if="t.status === 'PROCESSING'"
                  @click="$emit('updateStatus', t.id, 'RESOLVED')"
                  class="px-2 py-0.5 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 border border-emerald-500/30 text-[10px] transition-colors"
                >
                  办结
                </button>
                <button
                  v-if="t.status === 'RESOLVED'"
                  @click="$emit('updateStatus', t.id, 'CLOSED')"
                  class="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] transition-colors"
                >
                  归档
                </button>
                <span v-if="t.status === 'CLOSED'" class="text-[10px] text-slate-500">已闭环</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  tickets: {
    type: Array,
    default: () => [],
  },
  highlightedTicketNo: {
    type: String,
    default: '',
  },
})

defineEmits(['refresh', 'updateStatus', 'inspectTicket'])

const tableContainerRef = ref(null)
const selectedStatus = ref('ALL')
const keyword = ref('')

watch(
  () => props.highlightedTicketNo,
  (newVal) => {
    if (newVal) {
      selectedStatus.value = 'ALL'
      nextTick(() => {
        if (tableContainerRef.value) {
          tableContainerRef.value.scrollTop = 0
        }
      })
    }
  }
)

const statusOptions = [
  { label: '全部', value: 'ALL' },
  { label: '待处理', value: 'PENDING' },
  { label: '处理中', value: 'PROCESSING' },
  { label: '已解决', value: 'RESOLVED' },
  { label: '已关闭', value: 'CLOSED' },
]

const filteredTickets = computed(() => {
  return props.tickets.filter((t) => {
    if (selectedStatus.value !== 'ALL' && t.status !== selectedStatus.value) {
      return false
    }
    if (keyword.value.trim()) {
      const kw = keyword.value.trim().toLowerCase()
      const matchNo = (t.ticket_no || '').toLowerCase().includes(kw)
      const matchTitle = (t.title || '').toLowerCase().includes(kw)
      const matchDev = (t.device_id || '').toLowerCase().includes(kw)
      const matchDesc = (t.description || '').toLowerCase().includes(kw)
      return matchNo || matchTitle || matchDev || matchDesc
    }
    return true
  })
})

function priorityClass(priority) {
  switch (priority) {
    case 'CRITICAL':
      return 'bg-rose-950/80 text-rose-300 border border-rose-500/40'
    case 'HIGH':
      return 'bg-amber-950/80 text-amber-300 border border-amber-500/40'
    case 'MEDIUM':
      return 'bg-blue-950/80 text-blue-300 border border-blue-500/30'
    case 'LOW':
      return 'bg-slate-800 text-slate-400 border border-slate-700'
    default:
      return 'bg-slate-800 text-slate-300'
  }
}

function statusClass(status) {
  switch (status) {
    case 'PENDING':
      return 'bg-amber-950/80 text-amber-300 border border-amber-500/30'
    case 'PROCESSING':
      return 'bg-blue-950/80 text-blue-300 border border-blue-500/30'
    case 'RESOLVED':
      return 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/30'
    case 'CLOSED':
      return 'bg-slate-800 text-slate-400 border border-slate-700'
    default:
      return 'bg-slate-800 text-slate-300'
  }
}
</script>
