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
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/70 backdrop-blur-md overflow-hidden"
        @click.self="close"
      >
        <div
          class="w-full max-w-2xl rounded-3xl bg-zinc-900/95 border border-white/[0.12] ring-1 ring-white/[0.05] p-5 sm:p-6 space-y-4 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] flex flex-col max-h-[90vh] overflow-hidden backdrop-blur-2xl transition-all"
        >
          <!-- 移动端顶部抓手装饰条 -->
          <div class="w-10 h-1 rounded-full bg-white/20 mx-auto -mt-1 sm:hidden"></div>

          <!-- 头部 -->
          <div class="flex items-center justify-between border-b border-white/[0.08] pb-3 shrink-0">
            <div class="flex items-center space-x-3">
              <span class="p-2.5 rounded-2xl bg-zinc-950/80 border border-white/[0.1] text-indigo-400 shadow-sm">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </span>
              <div>
                <h3 class="text-base sm:text-lg font-semibold text-zinc-100 tracking-tight">
                  {{ isEdit ? '编辑机房资产与硬件规格' : '录入新设备与硬件物理参数' }}
                </h3>
                <p class="text-[11px] text-zinc-400">
                  {{ isEdit ? '更新设备的基础流转状态或底座硬件物理参数' : '录入新设备到机房台账，系统将自动分配并持久化硬件档案' }}
                </p>
              </div>
            </div>

            <button
              @click="close"
              class="text-zinc-400 hover:text-zinc-100 p-2 rounded-full hover:bg-white/[0.08] transition-all shrink-0 active:scale-90"
              title="关闭 (Esc)"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

      <!-- 分段切换器 (Tabs) -->
      <div class="flex items-center space-x-1 text-xs bg-zinc-900/80 p-1 rounded-xl border border-white/[0.06] shrink-0">
        <button
          type="button"
          @click="activeTab = 'basic'"
          :class="[
            'flex-1 py-1.5 rounded-lg transition-all font-medium flex items-center justify-center space-x-1.5',
            activeTab === 'basic'
              ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-white/[0.08]'
              : 'text-zinc-400 hover:text-zinc-200'
          ]"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <span>1. 基础台账与位置</span>
        </button>
        <button
          type="button"
          @click="activeTab = 'hardware'"
          :class="[
            'flex-1 py-1.5 rounded-lg transition-all font-medium flex items-center justify-center space-x-1.5',
            activeTab === 'hardware'
              ? 'bg-zinc-800 text-cyan-300 shadow-sm border border-cyan-500/20'
              : 'text-zinc-400 hover:text-zinc-200'
          ]"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          <span>2. 硬件物理规格参数</span>
        </button>
      </div>

      <!-- 表单主体区 -->
      <form @submit.prevent="handleSubmit" class="flex-1 overflow-y-auto pr-1 space-y-4 custom-scrollbar text-xs">
        <!-- TAB 1: 基础台账与位置 -->
        <div v-show="activeTab === 'basic'" class="space-y-3.5">
          <!-- 资产编号与自动生成 -->
          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <label class="font-medium text-zinc-300">资产编号 <span class="text-rose-400">*</span></label>
              <button
                v-if="!isEdit"
                type="button"
                @click="autoGenerateNo"
                class="text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline flex items-center space-x-1"
              >
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>自动生成规整编号</span>
              </button>
            </div>
            <input
              v-model="form.asset_no"
              type="text"
              :disabled="isEdit"
              placeholder="例如: DEV-SRV-206"
              required
              class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            />
          </div>

          <!-- 设备名称与分类 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">设备名称 <span class="text-rose-400">*</span></label>
              <input
                v-model="form.name"
                type="text"
                placeholder="例如: 2号机房-GPU计算节点06"
                required
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">设备类别 <span class="text-rose-400">*</span></label>
              <select
                v-model="form.category"
                required
                class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none transition-colors"
              >
                <option value="服务器">服务器</option>
                <option value="网络设备">网络设备</option>
                <option value="配电温控">配电温控</option>
                <option value="实验教学">实验教学</option>
              </select>
            </div>
          </div>

          <!-- 机房位置与责任人/借调人 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">机房/物理机柜位置 <span class="text-rose-400">*</span></label>
              <input
                v-model="form.location"
                type="text"
                placeholder="例如: 实训楼201-机柜A06"
                required
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">借用人 / 使用团队</label>
              <input
                v-model="form.borrower"
                type="text"
                placeholder="留空表示库房空闲在册"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <!-- 健康状态与借还状态 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">初始健康状态</label>
              <select
                v-model="form.health_status"
                class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
              >
                <option value="HEALTHY">HEALTHY (良好)</option>
                <option value="WARNING">WARNING (预警)</option>
                <option value="OVERHEAT">OVERHEAT (高温超温)</option>
                <option value="OFFLINE">OFFLINE (离线脱网)</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">借还流转状态</label>
              <select
                v-model="form.borrow_status"
                class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
              >
                <option value="AVAILABLE">AVAILABLE (空闲可借)</option>
                <option value="IN_USE">IN_USE (借调占用)</option>
                <option value="MAINTENANCE">MAINTENANCE (故障维护)</option>
              </select>
            </div>
          </div>

          <!-- 简要硬件规格说明 -->
          <div class="space-y-1">
            <label class="font-medium text-zinc-300">硬件概要标签</label>
            <input
              v-model="form.specs"
              type="text"
              placeholder="例如: 2x Xeon Gold 6330, 256GB RAM, 4x RTX 4090"
              class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors font-mono"
            />
          </div>
        </div>

        <!-- TAB 2: 硬件物理规格详细参数 -->
        <div v-show="activeTab === 'hardware'" class="space-y-3.5">
          <!-- 品牌型号与SN序列号 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">出厂 SN 序列号</label>
              <input
                v-model="detailForm.serial_number"
                type="text"
                placeholder="例如: SN-DELL-2024-998"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">厂商品牌</label>
              <input
                v-model="detailForm.brand"
                type="text"
                placeholder="例如: Dell / Huawei / Inspur"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">具体设备型号</label>
              <input
                v-model="detailForm.model_name"
                type="text"
                placeholder="例如: PowerEdge R750xa"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors font-mono"
              />
            </div>
          </div>

          <!-- 管理IP与MAC地址与固件 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">带外/管理 IP</label>
              <input
                v-model="detailForm.management_ip"
                type="text"
                placeholder="例如: 192.168.10.206"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-cyan-300 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">物理 MAC 地址</label>
              <input
                v-model="detailForm.mac_address"
                type="text"
                placeholder="例如: 00:1A:2B:3C:4D:5E"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">系统 / 固件版本</label>
              <input
                v-model="detailForm.os_firmware"
                type="text"
                placeholder="例如: Ubuntu 22.04 LTS"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
          </div>

          <!-- CPU与内存 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">核心处理器 (CPU) 规格</label>
              <input
                v-model="detailForm.cpu_info"
                type="text"
                placeholder="例如: 2x Intel Xeon Gold 6330 (56核/112线程)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">运行内存 (RAM) 规格</label>
              <input
                v-model="detailForm.memory_info"
                type="text"
                placeholder="例如: 256GB (8x 32GB DDR4 3200MHz ECC)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
          </div>

          <!-- 磁盘存储与GPU -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">磁盘存储配置与阵列</label>
              <input
                v-model="detailForm.storage_info"
                type="text"
                placeholder="例如: 2x 960G NVMe RAID1 + 4x 3.84T U.2 RAID5"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">算力加速卡 (GPU)</label>
              <input
                v-model="detailForm.gpu_info"
                type="text"
                placeholder="例如: 4x NVIDIA RTX 4090 24GB GDDR6X"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
          </div>

          <!-- 网络端口与供电规格 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">网络物理接口与速率</label>
              <input
                v-model="detailForm.network_interfaces"
                type="text"
                placeholder="例如: 2x 25GE SFP28 双光口 + 2x 10GE 电口"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">动力供电与功耗规格</label>
              <input
                v-model="detailForm.power_supply"
                type="text"
                placeholder="例如: 双路冗余 2400W 80Plus 钛金电源 (1+1)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
          </div>

          <!-- 维保信息与供应商 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">投产/采购日期</label>
              <input
                v-model="detailForm.purchase_date"
                type="text"
                placeholder="例如: 2024-03-15"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">维保期限与到期日</label>
              <input
                v-model="detailForm.warranty_period"
                type="text"
                placeholder="例如: 2027-03-14 (3年金牌维保)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">供应商及技术支持</label>
              <input
                v-model="detailForm.supplier"
                type="text"
                placeholder="例如: 戴尔企业服务 (400-881-1852)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <!-- 自定义扩展 JSON 参数 -->
          <div class="space-y-1">
            <label class="font-medium text-zinc-300">扩展定制参数 (JSON 键值对格式)</label>
            <textarea
              v-model="detailForm.extra_params"
              rows="2"
              placeholder='例如: {"rack_units": "4U", "cooling": "风冷进气加压"}'
              class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
            ></textarea>
          </div>
        </div>

        <div v-if="errorMsg" class="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
          {{ errorMsg }}
        </div>

        <!-- 底部提交与取消 -->
        <div class="pt-3 border-t border-white/[0.08] flex items-center justify-end space-x-2.5 shrink-0">
          <button
            type="button"
            @click="close"
            class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition-all"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-medium text-xs shadow-md active:scale-95 disabled:opacity-50 transition-all flex items-center space-x-1.5"
          >
            <span v-if="isSubmitting" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>{{ isEdit ? '确认更新设备' : '确认录入入库' }}</span>
          </button>
        </div>
      </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  mode: {
    type: String,
    default: 'create', // 'create' | 'edit'
  },
  asset: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const isEdit = computed(() => props.mode === 'edit')
const activeTab = ref('basic')
const isSubmitting = ref(false)
const errorMsg = ref('')

const form = reactive({
  asset_no: '',
  name: '',
  category: '服务器',
  location: '',
  health_status: 'HEALTHY',
  borrow_status: 'AVAILABLE',
  borrower: '',
  specs: '',
})

const detailForm = reactive({
  serial_number: '',
  brand: '',
  model_name: '',
  os_firmware: '',
  mac_address: '',
  management_ip: '',
  cpu_info: '',
  memory_info: '',
  storage_info: '',
  gpu_info: '',
  network_interfaces: '',
  power_supply: '',
  purchase_date: '',
  warranty_period: '',
  supplier: '',
  extra_params: '',
})

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      errorMsg.value = ''
      activeTab.value = 'basic'
      if (isEdit.value && props.asset) {
        form.asset_no = props.asset.asset_no || ''
        form.name = props.asset.name || ''
        form.category = props.asset.category || '服务器'
        form.location = props.asset.location || ''
        form.health_status = props.asset.health_status || 'HEALTHY'
        form.borrow_status = props.asset.borrow_status || 'AVAILABLE'
        form.borrower = props.asset.borrower || ''
        form.specs = props.asset.specs || ''

        const d = props.asset.detail || {}
        detailForm.serial_number = d.serial_number || ''
        detailForm.brand = d.brand || ''
        detailForm.model_name = d.model_name || ''
        detailForm.os_firmware = d.os_firmware || ''
        detailForm.mac_address = d.mac_address || ''
        detailForm.management_ip = d.management_ip || ''
        detailForm.cpu_info = d.cpu_info || ''
        detailForm.memory_info = d.memory_info || ''
        detailForm.storage_info = d.storage_info || ''
        detailForm.gpu_info = d.gpu_info || ''
        detailForm.network_interfaces = d.network_interfaces || ''
        detailForm.power_supply = d.power_supply || ''
        detailForm.purchase_date = d.purchase_date || ''
        detailForm.warranty_period = d.warranty_period || ''
        detailForm.supplier = d.supplier || ''
        detailForm.extra_params = d.extra_params || ''
      } else {
        resetForm()
        autoGenerateNo()
      }
    }
  }
)

function resetForm() {
  form.asset_no = ''
  form.name = ''
  form.category = '服务器'
  form.location = '实训楼201-'
  form.health_status = 'HEALTHY'
  form.borrow_status = 'AVAILABLE'
  form.borrower = ''
  form.specs = ''

  Object.keys(detailForm).forEach((k) => {
    detailForm[k] = ''
  })
}

function autoGenerateNo() {
  const prefixMap = {
    '服务器': 'DEV-SRV',
    '网络设备': 'DEV-NET',
    '配电温控': 'DEV-PWR',
    '实验教学': 'DEV-LAB',
  }
  const prefix = prefixMap[form.category] || 'DEV-AST'
  const randNum = Math.floor(100 + Math.random() * 900)
  form.asset_no = `${prefix}-${randNum}`
}

function close() {
  emit('update:modelValue', false)
}

async function handleSubmit() {
  if (!form.asset_no.trim() || !form.name.trim() || !form.location.trim()) {
    errorMsg.value = '请完整填写资产编号、名称与机房物理位置'
    return
  }

  isSubmitting.value = true
  errorMsg.value = ''

  try {
    const payload = {
      name: form.name.trim(),
      category: form.category,
      location: form.location.trim(),
      health_status: form.health_status,
      borrow_status: form.borrow_status,
      borrower: form.borrower.trim() || null,
      specs: form.specs.trim() || null,
      detail: {
        serial_number: detailForm.serial_number.trim() || null,
        brand: detailForm.brand.trim() || null,
        model_name: detailForm.model_name.trim() || null,
        os_firmware: detailForm.os_firmware.trim() || null,
        mac_address: detailForm.mac_address.trim() || null,
        management_ip: detailForm.management_ip.trim() || null,
        cpu_info: detailForm.cpu_info.trim() || null,
        memory_info: detailForm.memory_info.trim() || null,
        storage_info: detailForm.storage_info.trim() || null,
        gpu_info: detailForm.gpu_info.trim() || null,
        network_interfaces: detailForm.network_interfaces.trim() || null,
        power_supply: detailForm.power_supply.trim() || null,
        purchase_date: detailForm.purchase_date.trim() || null,
        warranty_period: detailForm.warranty_period.trim() || null,
        supplier: detailForm.supplier.trim() || null,
        extra_params: detailForm.extra_params.trim() || null,
      },
    }

    let savedAsset
    if (isEdit.value) {
      savedAsset = await api.updateAsset(props.asset.id, payload)
    } else {
      payload.asset_no = form.asset_no.trim().toUpperCase()
      savedAsset = await api.createAsset(payload)
    }

    emit('saved', savedAsset)
    close()
  } catch (err) {
    errorMsg.value = err.message || '提交失败，请检查网络或后端连接'
  } finally {
    isSubmitting.value = false
  }
}
</script>
