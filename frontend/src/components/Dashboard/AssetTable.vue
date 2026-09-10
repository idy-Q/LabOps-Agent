<template>
  <div class="rounded-2xl bg-slate-900/80 border border-slate-800 p-4 space-y-3 shadow-sm flex flex-col">
    <!-- 头部与分类过滤 -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
      <div class="flex items-center space-x-2">
        <span class="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-semibold text-slate-100">机房资产设备台账</h3>
        <span class="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 text-[11px] font-mono">
          {{ filteredAssets.length }} 台
        </span>
      </div>

      <!-- 分类过滤 -->
      <div class="flex items-center space-x-1 text-xs">
        <button
          v-for="c in categoryOptions"
          :key="c.value"
          @click="selectedCategory = c.value"
          :class="[
            'px-2 py-1 rounded-lg text-[11px] transition-all',
            selectedCategory === c.value
              ? 'bg-cyan-500/20 text-cyan-300 font-medium border border-cyan-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          ]"
        >
          {{ c.label }}
        </button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="relative">
      <input
        v-model="keyword"
        type="text"
        placeholder="搜索资产编号、设备名称、机房位置..."
        class="w-full bg-slate-950/60 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 transition-colors"
      />
      <span v-if="keyword" @click="keyword = ''" class="absolute right-2.5 top-2 text-slate-500 hover:text-slate-300 text-xs cursor-pointer">
        ✕
      </span>
    </div>

    <!-- 资产表格区域 -->
    <div class="overflow-x-auto rounded-xl border border-slate-800/80 max-h-72 overflow-y-auto">
      <table class="w-full text-left text-xs text-slate-300 border-collapse">
        <thead class="bg-slate-950/80 text-[11px] text-slate-400 sticky top-0 uppercase tracking-wider border-b border-slate-800">
          <tr>
            <th class="py-2.5 px-3">设备编号</th>
            <th class="py-2.5 px-3">设备名称 / 分类</th>
            <th class="py-2.5 px-3">物理位置</th>
            <th class="py-2.5 px-2 text-center">健康状态</th>
            <th class="py-2.5 px-3">借还状态 / 借用人</th>
            <th class="py-2.5 px-3 text-right">资产操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60">
          <tr v-if="filteredAssets.length === 0">
            <td colspan="6" class="py-6 text-center text-slate-500 text-xs">
              未检索到符合条件的资产设备
            </td>
          </tr>
          <tr
            v-for="a in filteredAssets"
            :key="a.id"
            :class="[
              'transition-colors hover:bg-slate-800/40 text-xs',
              a.asset_no === highlightedAssetNo
                ? 'bg-cyan-500/25 ring-2 ring-cyan-400 animate-pulse font-semibold'
                : ''
            ]"
          >
            <!-- 编号 -->
            <td class="py-2.5 px-3 font-mono text-[11px] text-cyan-300 whitespace-nowrap">
              <span
                @click="$emit('inspectAsset', a.asset_no)"
                class="hover:underline cursor-pointer"
                title="点击在对话中发起巡检排查"
              >
                {{ a.asset_no }}
              </span>
            </td>

            <!-- 名称分类 -->
            <td class="py-2.5 px-3">
              <div class="font-medium text-slate-200">{{ a.name }}</div>
              <div class="text-[10px] text-slate-400 font-mono">{{ a.category }}</div>
            </td>

            <!-- 位置 -->
            <td class="py-2.5 px-3 text-slate-300 text-[11px] whitespace-nowrap">
              {{ a.location }}
            </td>

            <!-- 健康状态 (可直接快速切换模拟) -->
            <td class="py-2.5 px-2 text-center whitespace-nowrap">
              <select
                :value="a.health_status"
                @change="$emit('updateHealth', a.id, $event.target.value)"
                :class="[
                  'px-1.5 py-0.5 rounded text-[10px] font-medium font-mono bg-slate-900 border cursor-pointer focus:outline-none',
                  healthClass(a.health_status)
                ]"
              >
                <option value="HEALTHY">HEALTHY (良好)</option>
                <option value="WARNING">WARNING (预警)</option>
                <option value="OVERHEAT">OVERHEAT (超温)</option>
                <option value="OFFLINE">OFFLINE (离线)</option>
              </select>
            </td>

            <!-- 借用状态与借用人 -->
            <td class="py-2.5 px-3 whitespace-nowrap">
              <div class="flex items-center space-x-1.5">
                <span :class="['px-1.5 py-0.5 rounded text-[10px] font-mono', borrowClass(a.borrow_status)]">
                  {{ a.borrow_status }}
                </span>
                <span v-if="a.borrower" class="text-[11px] text-amber-300">
                  ({{ a.borrower }})
                </span>
              </div>
            </td>

            <!-- 借还操作 -->
            <td class="py-2.5 px-3 text-right whitespace-nowrap">
              <div class="flex items-center justify-end space-x-1">
                <button
                  v-if="a.borrow_status === 'AVAILABLE'"
                  @click="openBorrowModal(a)"
                  class="px-2 py-0.5 rounded bg-cyan-900/60 hover:bg-cyan-800 text-cyan-200 border border-cyan-500/30 text-[10px] transition-colors"
                >
                  借用
                </button>
                <button
                  v-if="a.borrow_status === 'IN_USE'"
                  @click="$emit('returnAsset', a.asset_no)"
                  class="px-2 py-0.5 rounded bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 border border-emerald-500/30 text-[10px] transition-colors"
                >
                  归还
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 借用登记快速弹窗 -->
    <div
      v-if="showBorrowModal"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      @click.self="showBorrowModal = false"
    >
      <div class="w-full max-w-sm rounded-2xl bg-slate-900 border border-cyan-500/30 p-5 space-y-3 shadow-2xl">
        <h4 class="text-sm font-semibold text-slate-100">办理设备借出登记</h4>
        <div class="text-xs text-slate-400">
          目标设备：<span class="font-mono text-cyan-300 font-bold">{{ targetAsset?.asset_no }}</span> ({{ targetAsset?.name }})
        </div>
        <div>
          <label class="block text-[11px] text-slate-400 mb-1">借用人姓名 / 课题组</label>
          <input
            v-model="borrowerInput"
            type="text"
            placeholder="例如：张老师 / 智能感知实验室"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
          />
        </div>
        <div class="flex justify-end space-x-2 pt-2">
          <button
            @click="showBorrowModal = false"
            class="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
          >
            取消
          </button>
          <button
            @click="confirmBorrow"
            :disabled="!borrowerInput.trim()"
            class="px-3 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs disabled:opacity-40"
          >
            确认借出
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

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

const selectedCategory = ref('ALL')
const keyword = ref('')
const showBorrowModal = ref(false)
const targetAsset = ref(null)
const borrowerInput = ref('')

watch(
  () => props.highlightedAssetNo,
  (newVal) => {
    if (newVal) {
      selectedCategory.value = 'ALL'
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

const filteredAssets = computed(() => {
  return props.assets.filter((a) => {
    if (selectedCategory.value !== 'ALL' && a.category !== selectedCategory.value) {
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
  borrowerInput.value = '科研教师'
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
      return 'text-emerald-300 border-emerald-500/30'
    case 'WARNING':
      return 'text-amber-300 border-amber-500/30'
    case 'OVERHEAT':
      return 'text-rose-300 border-rose-500/40'
    case 'OFFLINE':
      return 'text-slate-400 border-slate-700'
    default:
      return 'text-slate-300 border-slate-700'
  }
}

function borrowClass(status) {
  switch (status) {
    case 'AVAILABLE':
      return 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/30'
    case 'IN_USE':
      return 'bg-amber-950/80 text-amber-300 border border-amber-500/30'
    case 'MAINTENANCE':
      return 'bg-slate-800 text-slate-400 border border-slate-700'
    default:
      return 'bg-slate-800 text-slate-300'
  }
}
</script>
