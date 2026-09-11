<template>
  <div class="relative" ref="controllerRef">
    <!-- 顶部导航栏玻璃微调胶囊按钮 -->
    <button
      @click="isOpen = !isOpen"
      class="px-2.5 py-1.5 rounded-lg border text-xs flex items-center space-x-1.5 transition-all shadow-sm active:scale-95 select-none"
      :class="[
        isOpen
          ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-200 shadow-indigo-500/10'
          : 'bg-zinc-900/80 hover:bg-zinc-800 text-zinc-300 hover:text-white border-white/[0.08] hover:border-white/[0.15]'
      ]"
      title="调节界面透明玻璃质感与背景动效"
    >
      <!-- 棱镜折射玻璃矢量 SVG 图标 -->
      <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
      </svg>
      <span class="font-medium hidden sm:inline">视效</span>
      <svg
        :class="['w-3 h-3 text-zinc-400 transition-transform duration-200', isOpen ? 'rotate-180' : '']"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- 玻璃视效控制浮层菜单 (100% 独立不透明遮光防穿透层级) -->
    <div
      v-if="isOpen"
      @keydown.esc.window="isOpen = false"
      class="fixed sm:absolute top-16 sm:top-full left-3 sm:left-auto right-3 sm:right-0 mt-0 sm:mt-2 w-auto sm:w-80 rounded-2xl bg-[#121218] border border-white/[0.14] p-4 shadow-[0_25px_60px_rgba(0,0,0,0.95)] text-xs space-y-4 text-zinc-200 z-50 animate-fade-in"
    >
      <!-- 浮层顶栏标题 -->
      <div class="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
        <div class="flex items-center space-x-2">
          <span class="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </span>
          <div>
            <h4 class="font-medium text-zinc-100 text-xs">全景玻璃视效调节</h4>
          </div>
        </div>

        <button
          @click="isOpen = false"
          class="text-zinc-500 hover:text-zinc-300 p-1 rounded hover:bg-white/[0.06] transition-colors"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 1. 三档经典预设快速切换 -->
      <div class="space-y-1.5">
        <span class="text-[10px] font-medium text-zinc-400 uppercase tracking-wider block">
          材质预设 (Presets)
        </span>
        <div class="grid grid-cols-3 gap-1.5">
          <button
            v-for="p in presets"
            :key="p.id"
            @click="applyPreset(p)"
            :class="[
              'p-2 rounded-xl border text-left transition-all flex flex-col justify-between group',
              activePreset === p.id
                ? 'bg-indigo-500/15 border-indigo-500/40 text-white shadow-sm ring-1 ring-indigo-500/20'
                : 'bg-white/[0.03] hover:bg-white/[0.06] border-white/[0.06] text-zinc-400 hover:text-zinc-200'
            ]"
          >
            <span class="font-medium text-[11px] block text-zinc-200 group-hover:text-white">{{ p.name }}</span>
            <span class="text-[9px] text-zinc-500 font-mono mt-1">{{ p.desc }}</span>
          </button>
        </div>
      </div>

      <!-- 2. 无级连续滑块精细微调 -->
      <div class="space-y-3 pt-1 border-t border-white/[0.06]">
        <!-- 不透明度滑块 -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-[11px]">
            <span class="text-zinc-400 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
              面板不透明度 (Opacity)
            </span>
            <span class="font-mono text-zinc-200 bg-white/[0.06] px-1.5 py-0.5 rounded text-[10px]">
              {{ opacityPercent }}%
            </span>
          </div>
          <input
            v-model.number="opacityPercent"
            type="range"
            min="10"
            max="90"
            step="1"
            class="w-full accent-indigo-500 h-1.5 bg-zinc-800 rounded-lg cursor-pointer transition-all"
            @input="handleCustomInput"
          />
          <div class="flex justify-between text-[9px] text-zinc-500 font-mono">
            <span>10% (极度通透)</span>
            <span>90% (扎实质感)</span>
          </div>
        </div>

        <!-- 模糊半径滑块 -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-[11px]">
            <span class="text-zinc-400 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
              毛玻璃模糊半径 (Blur)
            </span>
            <span class="font-mono text-zinc-200 bg-white/[0.06] px-1.5 py-0.5 rounded text-[10px]">
              {{ blurRadius }}px
            </span>
          </div>
          <input
            v-model.number="blurRadius"
            type="range"
            min="4"
            max="24"
            step="1"
            class="w-full accent-cyan-500 h-1.5 bg-zinc-800 rounded-lg cursor-pointer transition-all"
            @input="handleCustomInput"
          />
          <div class="flex justify-between text-[9px] text-zinc-500 font-mono">
            <span>4px (微弱虚化)</span>
            <span>24px (深度磨砂)</span>
          </div>
        </div>
      </div>

      <!-- 3. 背景效果开关 -->
      <div class="pt-2 border-t border-white/[0.06] flex items-center justify-between">
        <div class="font-medium text-[11px] text-zinc-200 flex items-center gap-1.5">
          <span
            class="w-1.5 h-1.5 rounded-full"
            :class="isBgAnimationActive ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-500'"
          ></span>
          背景效果
        </div>

        <!-- 启停滑动开关 Switch -->
        <button
          @click="toggleBgAnimation"
          type="button"
          class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
          :class="isBgAnimationActive ? 'bg-indigo-600' : 'bg-zinc-700'"
          title="启停背景动态效果"
        >
          <span
            class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out"
            :class="isBgAnimationActive ? 'translate-x-4' : 'translate-x-0'"
          />
        </button>
      </div>

      <!-- 4. 底部重置与状态提示 -->
      <div class="pt-2 border-t border-white/[0.06] flex items-center justify-between text-[10px] text-zinc-500">
        <button
          @click="resetToDefault"
          class="hover:text-zinc-300 underline transition-colors cursor-pointer"
        >
          恢复推荐默认
        </button>
        <span class="font-mono text-[9px]">已保存到本地存储</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  bgAnimation: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:bgAnimation'])

const isOpen = ref(false)
const controllerRef = ref(null)

// 经典预设配置
const presets = [
  {
    id: 'clear',
    name: '纯透清澈',
    desc: '15% · 6px',
    opacity: 15,
    blur: 6,
  },
  {
    id: 'frosted',
    name: '平衡毛玻璃',
    desc: '35% · 12px (荐)',
    opacity: 35,
    blur: 12,
  },
  {
    id: 'acrylic',
    name: '深邃亚克力',
    desc: '65% · 20px',
    opacity: 65,
    blur: 20,
  },
]

// 核心参数状态
const activePreset = ref('frosted')
const opacityPercent = ref(35)
const blurRadius = ref(12)
const isBgAnimationActive = ref(props.bgAnimation)

const STORAGE_KEY = 'labops_glass_config'

// 应用 CSS 变量到 :root
function applyGlassCSS() {
  const root = document.documentElement
  const op = opacityPercent.value / 100
  const blur = blurRadius.value

  root.style.setProperty('--glass-opacity', op.toFixed(2))
  root.style.setProperty('--glass-blur', `${blur}px`)

  // 面板与卡片背景半透色彩
  root.style.setProperty('--glass-bg', `rgba(12, 12, 16, ${op.toFixed(2)})`)
  root.style.setProperty('--glass-panel-bg', `rgba(12, 12, 16, ${op.toFixed(2)})`)
  
  // 卡片略增不透明度保障微反差层级
  const cardOp = Math.min(op + 0.12, 0.95).toFixed(2)
  const hoverOp = Math.min(op + 0.22, 0.98).toFixed(2)
  root.style.setProperty('--glass-card-bg', `rgba(18, 18, 24, ${cardOp})`)
  root.style.setProperty('--glass-card-hover-bg', `rgba(26, 26, 36, ${hoverOp})`)

  // 动态边框半透光
  const borderOp = Math.max(0.06, 0.15 - op * 0.08).toFixed(2)
  const borderHoverOp = Math.max(0.12, 0.24 - op * 0.08).toFixed(2)
  root.style.setProperty('--glass-border', `rgba(255, 255, 255, ${borderOp})`)
  root.style.setProperty('--glass-border-hover', `rgba(255, 255, 255, ${borderHoverOp})`)

  // 子卡片微背景
  const subOp = Math.max(0.02, 0.06 - op * 0.03).toFixed(2)
  root.style.setProperty('--glass-sub-bg', `rgba(255, 255, 255, ${subOp})`)

  // 动态高质感投影
  const shadowOp = (0.2 + op * 0.25).toFixed(2)
  root.style.setProperty('--glass-shadow', `0 8px 32px 0 rgba(0, 0, 0, ${shadowOp})`)
}

// 保存持久化配置
function saveConfig() {
  try {
    const config = {
      preset: activePreset.value,
      opacity: opacityPercent.value,
      blur: blurRadius.value,
      bgAnimation: isBgAnimationActive.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
  } catch {
    // 忽略 localStorage 限制
  }
}

// 从本地存储读取
function loadConfig() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const config = JSON.parse(saved)
      if (typeof config.opacity === 'number' && config.opacity >= 10 && config.opacity <= 90) {
        opacityPercent.value = config.opacity
      }
      if (typeof config.blur === 'number' && config.blur >= 4 && config.blur <= 24) {
        blurRadius.value = config.blur
      }
      if (typeof config.preset === 'string') activePreset.value = config.preset
      if (typeof config.bgAnimation === 'boolean') {
        isBgAnimationActive.value = config.bgAnimation
        emit('update:bgAnimation', config.bgAnimation)
      }
    }
  } catch {
    // 采用默认配置
  }
}

// 切换预设
function applyPreset(p) {
  activePreset.value = p.id
  opacityPercent.value = p.opacity
  blurRadius.value = p.blur
  applyGlassCSS()
  saveConfig()
}

// 自定义滑动输入
function handleCustomInput() {
  // 检查是否匹配任何预设
  const matched = presets.find((p) => p.opacity === opacityPercent.value && p.blur === blurRadius.value)
  activePreset.value = matched ? matched.id : 'custom'
  applyGlassCSS()
  saveConfig()
}

// 启停背景动画
function toggleBgAnimation() {
  isBgAnimationActive.value = !isBgAnimationActive.value
  emit('update:bgAnimation', isBgAnimationActive.value)
  saveConfig()
}

// 恢复默认配置
function resetToDefault() {
  applyPreset(presets[1]) // 平衡毛玻璃
  isBgAnimationActive.value = true
  emit('update:bgAnimation', true)
  saveConfig()
}

// 点击外部收起浮层
function handleClickOutside(e) {
  if (controllerRef.value && !controllerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

watch(
  () => props.bgAnimation,
  (val) => {
    isBgAnimationActive.value = val
  }
)

onMounted(() => {
  loadConfig()
  applyGlassCSS()
  document.addEventListener('pointerdown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('pointerdown', handleClickOutside)
})
</script>
