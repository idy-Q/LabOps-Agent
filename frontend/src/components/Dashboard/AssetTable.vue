<template>
  <div class="rounded-xl glass-panel border p-4 space-y-3.5 shadow-sm transition-colors flex flex-col">
    <!-- 头部与多维分类过滤 -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 pb-2 border-b border-white/[0.06]">
      <div class="flex items-center space-x-2">
        <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-cyan-400">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-medium text-zinc-100 glass-text">机房硬件资产与设备台账</h3>
        <span class="px-2 py-0.5 rounded-md bg-zinc-900/80 border border-white/[0.08] text-zinc-400 text-[10px] font-mono">
          共 {{ filteredAssets.length }} 台设备
        </span>
      </div>

      <!-- 分类胶囊 (Linear Segmented Pills) -->
      <div class="flex items-center space-x-1 text-xs bg-zinc-900/60 p-0.5 rounded-lg border border-white/[0.06]">
        <button
          v-for="c in categoryOptions"
          :key="c.value"
          @click="selectedCategory = c.value"
          :class="[
            'px-2.5 py-1 rounded-md text-[11px] transition-all',
            selectedCategory === c.value
              ? 'bg-zinc-800 text-zinc-100 font-medium shadow-sm border border-white/[0.08]'
              : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50 border border-transparent'
          ]"
        >
          {{ c.label }}
        </button>
      </div>
    </div>

    <!-- 搜索与健康筛选条 -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
      <div class="relative flex-1">
        <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索资产编号 (DEV-*)、设备名称、机架位置..."
          class="w-full bg-black/25 backdrop-blur-sm border border-white/[0.08] focus:border-cyan-500/60 rounded-lg pl-8 pr-8 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
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

      <!-- 健康状态快捷过滤 -->
      <div class="flex items-center space-x-1 shrink-0 text-xs">
        <button
          v-for="h in healthFilterOptions"
          :key="h.value"
          @click="selectedHealth = h.value"
          :class="[
            'px-2 py-1 rounded-md text-[10px] font-mono transition-all border',
            selectedHealth === h.value
              ? 'bg-zinc-800 text-zinc-100 font-medium border-white/[0.15] shadow-sm'
              : 'text-zinc-500 hover:text-zinc-300 border-white/[0.04] hover:bg-zinc-900'
          ]"
        >
          {{ h.label }}
        </button>

        <button
          @click="$emit('refresh')"
          class="px-2.5 py-1.5 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-white/[0.08] hover:border-white/[0.15] text-xs flex items-center space-x-1 transition-all active:scale-95 shadow-sm ml-1"
          title="刷新资产列表"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="hidden sm:inline">刷新</span>
        </button>
      </div>
    </div>

    <!-- 资产表格区域 (Linear Dark Table) -->
    <div ref="tableContainerRef" class="overflow-x-auto rounded-xl border border-white/[0.08] min-h-[300px] max-h-[580px] overflow-y-auto bg-black/25 backdrop-blur-sm shadow-sm">
      <table class="w-full text-left text-xs text-zinc-300 border-separate border-spacing-0">
        <thead class="bg-black/50 text-[11px] text-zinc-300 sticky top-0 uppercase tracking-wider border-b border-white/[0.06] backdrop-blur-md z-10">
          <tr>
            <th class="py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text">资产编号</th>
            <th class="py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text">设备名称 / 分类</th>
            <th class="py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text">机柜/物理位置</th>
            <th class="py-2.5 px-2 text-center border-b border-white/[0.06] font-medium glass-text">健康度调节</th>
            <th class="py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text">借用状态 / 借调人</th>
            <th class="py-2.5 px-3 text-right border-b border-white/[0.06] font-medium glass-text">资产操作</th>
          </tr>
        </thead>
        <tbody class="font-sans">
          <tr v-if="filteredAssets.length === 0">
            <td colspan="6" class="py-12 text-center text-zinc-500 text-xs">
              未检索到符合条件的资产设备
            </td>
          </tr>
          <tr
            v-for="a in filteredAssets"
            :key="a.id"
            :class="[
              'transition-all duration-300 hover:bg-white/[0.06] text-xs border-b border-white/[0.04]',
              a.asset_no === highlightedAssetNo
                ? 'animate-pulse-asset font-medium text-cyan-200'
                : ''
            ]"
          >
            <!-- 编号 -->
            <td class="py-2.5 px-3 font-mono text-[11px] text-zinc-300 whitespace-nowrap">
              <span
                @click="$emit('inspectAsset', a.asset_no)"
                class="hover:underline hover:text-cyan-400 cursor-pointer flex items-center gap-1.5 transition-colors"
                title="点击在左侧对话中发起设备巡检"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="a.health_status === 'HEALTHY' ? 'bg-emerald-400' : a.health_status === 'OVERHEAT' ? 'bg-rose-400 animate-ping' : 'bg-amber-400'"></span>
                {{ a.asset_no }}
              </span>
            </td>

            <!-- 名称分类 -->
            <td class="py-2.5 px-3">
              <div class="font-medium text-zinc-200 truncate">{{ a.name }}</div>
              <div class="text-[10px] text-zinc-500 font-mono truncate">{{ a.category }}</div>
            </td>

            <!-- 位置 -->
            <td class="py-2.5 px-3 text-zinc-400 text-[11px] font-mono whitespace-nowrap">
              {{ a.location }}
            </td>

            <!-- 健康状态快速模拟调节 -->
            <td class="py-2.5 px-2 text-center whitespace-nowrap">
              <select
                :value="a.health_status"
                @change="$emit('updateHealth', a.id, $event.target.value)"
                :class="[
                  'px-2 py-0.5 rounded text-[10px] font-medium font-mono border cursor-pointer focus:outline-none transition-colors shadow-sm',
                  healthClass(a.health_status)
                ]"
                title="可切换状态联动触发大盘突变与推理"
              >
                <option class="bg-zinc-900 text-zinc-300" value="HEALTHY">HEALTHY (良好)</option>
                <option class="bg-zinc-900 text-zinc-300" value="WARNING">WARNING (预警)</option>
                <option class="bg-zinc-900 text-zinc-300" value="OVERHEAT">OVERHEAT (超温)</option>
                <option class="bg-zinc-900 text-zinc-300" value="OFFLINE">OFFLINE (离线)</option>
              </select>
            </td>

            <!-- 借用状态与借用人 -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              <div class="flex items-center space-x-1.5">
                <span :class="['px-2 py-0.5 rounded text-[10px] font-mono', borrowClass(a.borrow_status)]">
                  {{ a.borrow_status }}
                </span>
                <span v-if="a.borrower" class="text-[11px] text-amber-300 font-medium font-mono">
                  ({{ a.borrower }})
                </span>
              </div>
            </td>

            <!-- 借还操作 (Linear Buttons) -->
            <td class="py-2.5 px-3 text-right whitespace-nowrap">
              <div class="flex items-center justify-end space-x-1.5">
                <button
                  v-if="a.borrow_status === 'AVAILABLE'"
                  @click="openBorrowModal(a)"
                  class="px-2.5 py-0.5 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-white/[0.08] text-[10px] transition-all active:scale-95 shadow-sm font-mono"
                >
                  借用
                </button>
                <button
                  v-if="a.borrow_status === 'IN_USE'"
                  @click="$emit('returnAsset', a.asset_no)"
                  class="px-2.5 py-0.5 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 text-[10px] transition-all active:scale-95 shadow-sm font-mono"
                >
                  归还
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 借用登记快速弹窗 (Linear Modal) -->
    <div
      v-if="showBorrowModal"
      @keydown.esc.window="showBorrowModal = false"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in"
      @click.self="showBorrowModal = false"
    >
      <div class="w-full max-w-sm rounded-xl glass-card border border-white/[0.12] p-5 space-y-4 shadow-2xl backdrop-blur-xl">
        <div class="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
          <div class="flex items-center space-x-2">
            <span class="p-1.5 rounded-lg bg-zinc-900/90 border border-white/[0.08] text-cyan-400">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </span>
            <h4 class="text-sm font-medium text-zinc-100 glass-text">办理设备借出登记</h4>
          </div>
          <button
            @click="showBorrowModal = false"
            class="text-zinc-500 hover:text-zinc-300 p-1 rounded transition-colors"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="text-xs text-zinc-400 bg-zinc-950/60 p-2.5 rounded-lg border border-white/[0.04] space-y-1">
          <div>目标设备：<span class="font-mono text-cyan-400 font-medium">{{ targetAsset?.asset_no }}</span></div>
          <div class="text-zinc-500">{{ targetAsset?.name }} ({{ targetAsset?.location }})</div>
        </div>

        <div>
          <label class="block text-[11px] text-zinc-400 mb-1">借用人姓名 / 课题组</label>
          <input
            v-model="borrowerInput"
            type="text"
            placeholder="例如：李老师 / 人工智能实验室"
            class="w-full bg-black/30 backdrop-blur-sm border border-white/[0.08] rounded-lg px-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        <div class="flex justify-end space-x-2 pt-2">
          <button
            @click="showBorrowModal = false"
            class="px-3 py-1.5 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors border border-white/[0.08]"
          >
            取消
          </button>
          <button
            @click="confirmBorrow"
            :disabled="!borrowerInput.trim()"
            class="px-3.5 py-1.5 rounded-md bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs disabled:opacity-40 transition-all shadow-sm active:scale-95"
          >
            确认登记借出
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  assets: {
    type: Array,
    default: () => [],
  },
  highlightedAssetNo: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['refresh', 'borrowAsset', 'returnAsset', 'updateHealth', 'inspectAsset'])

const tableContainerRef = ref(null)
const selectedCategory = ref('ALL')
const selectedHealth = ref('ALL')
const keyword = ref('')
const showBorrowModal = ref(false)
const targetAsset = ref(null)
const borrowerInput = ref('')

watch(
  () => props.highlightedAssetNo,
  (newVal) => {
    if (newVal) {
      selectedCategory.value = 'ALL'
      selectedHealth.value = 'ALL'
      keyword.value = ''
      nextTick(() => {
        if (tableContainerRef.value) {
          tableContainerRef.value.scrollTop = 0
        }
      })
    }
  }
)

const categoryOptions = [
  { label: '全部', value: 'ALL' },
  { label: '服务器', value: '服务器' },
  { label: '网络设备', value: '网络设备' },
  { label: '配电温控', value: '配电温控' },
  { label: '实验教学', value: '实验教学' },
]

const healthFilterOptions = [
  { label: '全部健康度', value: 'ALL' },
  { label: '良好', value: 'HEALTHY' },
  { label: '预警', value: 'WARNING' },
  { label: '超温', value: 'OVERHEAT' },
  { label: '离线', value: 'OFFLINE' },
]

const filteredAssets = computed(() => {
  return props.assets.filter((a) => {
    if (selectedCategory.value !== 'ALL' && a.category !== selectedCategory.value) {
      return false
    }
    if (selectedHealth.value !== 'ALL' && a.health_status !== selectedHealth.value) {
      return false
    }
    if (keyword.value.trim()) {
      const kw = keyword.value.trim().toLowerCase()
      const matchNo = (a.asset_no || '').toLowerCase().includes(kw)
      const matchName = (a.name || '').toLowerCase().includes(kw)
      const matchLoc = (a.location || '').toLowerCase().includes(kw)
      return matchNo || matchName || matchLoc
    }
    return true
  })
})

function openBorrowModal(asset) {
  targetAsset.value = asset
  borrowerInput.value = '李老师'
  showBorrowModal.value = true
}

function confirmBorrow() {
  if (!targetAsset.value || !borrowerInput.value.trim()) return
  emit('borrowAsset', targetAsset.value.asset_no, borrowerInput.value.trim())
  showBorrowModal.value = false
}

function healthClass(status) {
  switch (status) {
    case 'HEALTHY':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'WARNING':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'OVERHEAT':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20 font-semibold'
    case 'OFFLINE':
      return 'bg-zinc-800 text-zinc-500 border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border-white/[0.06]'
  }
}

function borrowClass(status) {
  switch (status) {
    case 'AVAILABLE':
      return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
    case 'IN_USE':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'MAINTENANCE':
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}
</script>
