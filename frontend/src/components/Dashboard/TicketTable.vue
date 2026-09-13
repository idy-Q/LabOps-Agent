<template>
  <div class="rounded-xl glass-panel border p-4 space-y-3.5 shadow-sm transition-colors flex flex-col">
    <!-- 头部栏与过滤控制 -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 pb-2 border-b border-white/[0.06]">
      <div class="flex items-center space-x-2">
        <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-amber-400">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-medium text-zinc-100 glass-text">机房运维工单流转库</h3>
        <span class="px-2 py-0.5 rounded-md bg-zinc-900/80 border border-white/[0.08] text-zinc-400 text-[10px] font-mono">
          共 {{ filteredTickets.length }} 条记录
        </span>
      </div>

      <!-- 状态过滤胶囊 (Linear Segmented Pills) -->
      <div class="flex items-center space-x-1 text-xs bg-zinc-900/60 p-0.5 rounded-lg border border-white/[0.06]">
        <button
          v-for="s in statusOptions"
          :key="s.value"
          @click="selectedStatus = s.value"
          :class="[
            'px-2.5 py-1 rounded-md text-[11px] transition-all',
            selectedStatus === s.value
              ? 'bg-zinc-800 text-zinc-100 font-medium shadow-sm border border-white/[0.08]'
              : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50 border border-transparent'
          ]"
        >
          {{ s.label }}
        </button>
      </div>
    </div>

    <!-- 搜索栏与刷新栏 -->
    <div class="flex items-center space-x-2">
      <div class="relative flex-1">
        <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索工单编号、故障描述、关联设备或报修内容..."
          class="w-full bg-black/25 backdrop-blur-sm border border-white/[0.08] focus:border-indigo-500/60 rounded-lg pl-8 pr-8 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
        />
        <button
          v-if="keyword"
          @click="keyword = ''"
          class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-zinc-500 hover:text-zinc-300 transition-colors"
          title="清空搜索"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <button
        @click="$emit('refresh')"
        class="px-2.5 py-1.5 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-white/[0.08] hover:border-white/[0.15] text-xs flex items-center space-x-1 transition-all shrink-0 active:scale-95 shadow-sm"
        title="刷新工单列表"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span class="hidden sm:inline">刷新</span>
      </button>
    </div>

    <!-- 表格区域 (Linear Dark Table) -->
    <div ref="tableContainerRef" class="overflow-x-hidden rounded-xl border border-white/[0.08] min-h-[300px] max-h-[580px] overflow-y-auto bg-black/25 backdrop-blur-sm shadow-sm">
      <table class="w-full table-fixed text-left text-xs text-zinc-300 border-separate border-spacing-0">
        <thead class="bg-black/50 text-[11px] text-zinc-300 sticky top-0 uppercase tracking-wider border-b border-white/[0.06] backdrop-blur-md z-10">
          <tr>
            <th class="w-[124px] py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">工单编号</th>
            <th class="w-auto py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text">工单标题与处置内容</th>
            <th class="w-[70px] py-2.5 px-1 text-center border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">等级</th>
            <th class="w-[76px] py-2.5 px-1 text-center border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">流转状态</th>
            <th class="w-[102px] py-2.5 px-2 border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">关联设备</th>
            <th class="w-[84px] py-2.5 px-3 text-right border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">处置操作</th>
          </tr>
        </thead>
        <tbody class="font-sans">
          <tr v-if="filteredTickets.length === 0">
            <td colspan="6" class="py-12 text-center text-zinc-500 text-xs">
              未检索到符合条件的运维工单
            </td>
          </tr>
          <tr
            v-for="t in filteredTickets"
            :key="t.id"
            :class="[
              'transition-all duration-300 hover:bg-white/[0.06] text-xs border-b border-white/[0.04]',
              t.ticket_no === highlightedTicketNo
                ? 'animate-pulse-ticket font-medium text-amber-200'
                : ''
            ]"
          >
            <!-- 工单编号 -->
            <td class="py-2.5 px-3 font-mono text-[11px] text-zinc-300 whitespace-nowrap truncate">
              <span
                @click="$emit('inspectTicket', t.ticket_no)"
                class="hover:underline hover:text-amber-400 cursor-pointer inline-flex items-center gap-1.5 transition-colors"
                title="点击在左侧对话中查询此工单进展"
              >
                <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="t.status === 'RESOLVED' || t.status === 'CLOSED' ? 'bg-zinc-600' : 'bg-amber-400'"></span>
                <span class="truncate">{{ t.ticket_no }}</span>
              </span>
            </td>

            <!-- 标题与排查要求 -->
            <td class="py-2.5 px-3 overflow-hidden">
              <div class="font-medium text-zinc-200 truncate" :title="t.title">{{ t.title }}</div>
              <div class="text-[11px] text-zinc-500 truncate" :title="t.description">{{ t.description }}</div>
            </td>

            <!-- 优先级 (Linear Badge) -->
            <td class="py-2.5 px-1 text-center whitespace-nowrap">
              <span :class="['px-1.5 py-0.5 rounded text-[10px] font-mono inline-block', priorityClass(t.priority)]">
                {{ t.priority }}
              </span>
            </td>

            <!-- 状态 (Linear Badge) -->
            <td class="py-2.5 px-1 text-center whitespace-nowrap">
              <span :class="['px-1.5 py-0.5 rounded text-[10px] font-mono inline-block', statusClass(t.status)]">
                {{ statusLabel(t.status) }}
              </span>
            </td>

            <!-- 关联设备 -->
            <td class="py-2.5 px-2 font-mono text-[11px] text-zinc-400 whitespace-nowrap truncate" :title="t.device_id || '-'">
              {{ t.device_id || '-' }}
            </td>

            <!-- 快速流转推进 (Linear Buttons) -->
            <td class="py-2.5 px-3 text-right whitespace-nowrap">
              <!-- 学生角色：隐藏操作列流转按钮，显示中性灰微标「学生只读」 -->
              <span
                v-if="isStudent"
                class="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-800/80 text-zinc-400 border border-white/[0.08] inline-block shadow-sm"
                title="学生角色对机房运维工单仅有只读权限"
              >
                学生只读
              </span>

              <!-- 教师与管理员角色操作列 -->
              <div v-else class="flex items-center justify-end space-x-1.5">
                <!-- 待处理工单：教师与管理员均可点击【受理】 -->
                <button
                  v-if="t.status === 'PENDING'"
                  @click="$emit('updateStatus', t.id, 'PROCESSING')"
                  class="px-2.5 py-0.5 rounded-md bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 text-[11px] transition-all active:scale-95 shadow-sm font-mono"
                  title="认领并开始处理工单"
                >
                  受理
                </button>

                <!-- 处理中工单：管理员可办结，教师置灰禁用并提示“需主管核验闭环” -->
                <button
                  v-if="t.status === 'PROCESSING'"
                  :disabled="isTeacher"
                  @click="!isTeacher && $emit('updateStatus', t.id, 'RESOLVED')"
                  :class="[
                    'px-2.5 py-0.5 rounded-md text-[11px] transition-all font-mono border',
                    isTeacher
                      ? 'bg-zinc-800/50 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-60'
                      : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border-emerald-500/20 active:scale-95 shadow-sm'
                  ]"
                  :title="isTeacher ? '需主管核验闭环' : '办结此工单'"
                >
                  办结
                </button>

                <!-- 已解决工单：管理员可归档，教师置灰禁用并提示“需主管核验闭环” -->
                <button
                  v-if="t.status === 'RESOLVED'"
                  :disabled="isTeacher"
                  @click="!isTeacher && $emit('updateStatus', t.id, 'CLOSED')"
                  :class="[
                    'px-2.5 py-0.5 rounded-md text-[11px] transition-all font-mono border',
                    isTeacher
                      ? 'bg-zinc-800/50 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-60'
                      : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/[0.08] active:scale-95 shadow-sm'
                  ]"
                  :title="isTeacher ? '需主管核验闭环' : '归档此工单'"
                >
                  归档
                </button>

                <span v-if="t.status === 'CLOSED'" class="text-[11px] text-zinc-500 font-mono">已闭环</span>
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
  currentUser: {
    type: Object,
    default: null,
  },
  highlightedTicketNo: {
    type: String,
    default: '',
  },
})

const userRole = computed(() => (props.currentUser?.role || 'STUDENT').toUpperCase())
const isStudent = computed(() => userRole.value === 'STUDENT')
const isTeacher = computed(() => userRole.value === 'TEACHER')
const isAdmin = computed(() => userRole.value === 'ADMIN')

defineEmits(['refresh', 'updateStatus', 'inspectTicket'])

const tableContainerRef = ref(null)
const selectedStatus = ref('ALL')
const keyword = ref('')

watch(
  () => props.highlightedTicketNo,
  (newVal) => {
    if (newVal) {
      selectedStatus.value = 'ALL'
      keyword.value = ''
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

function statusLabel(status) {
  switch (status) {
    case 'PENDING':
      return '待处理'
    case 'PROCESSING':
      return '处理中'
    case 'RESOLVED':
      return '已解决'
    case 'CLOSED':
      return '已关闭'
    default:
      return status
  }
}

function priorityClass(priority) {
  switch (priority) {
    case 'CRITICAL':
      return 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
    case 'HIGH':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'MEDIUM':
      return 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
    case 'LOW':
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}

function statusClass(status) {
  switch (status) {
    case 'PENDING':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'PROCESSING':
      return 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
    case 'RESOLVED':
      return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
    case 'CLOSED':
      return 'bg-zinc-800 text-zinc-500 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}
</script>
