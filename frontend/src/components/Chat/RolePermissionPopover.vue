<template>
  <div class="relative inline-block select-none" ref="popoverContainerRef">
    <!-- 身份触发药丸胶囊 (Role Trigger Pill) -->
    <div
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
      @click="togglePopover"
      role="button"
      tabindex="0"
      class="role-trigger-badge flex items-center space-x-1.5 px-2.5 py-1 rounded-lg border text-[11px] font-medium transition-all duration-200 cursor-pointer shadow-xs active:scale-95 group focus:outline-none"
      :class="triggerClass"
      :title="`当前身份：${roleConfig.title}。点击查看权限指引`"
    >
      <!-- 角色矢量图标 -->
      <span class="shrink-0 flex items-center justify-center">
        <!-- 学生 (帽子) -->
        <svg v-if="roleKey === 'STUDENT'" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
        </svg>
        <!-- 教师 (讲台/书本) -->
        <svg v-else-if="roleKey === 'TEACHER'" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <!-- 管理员 (盾牌) -->
        <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </span>

      <!-- 角色名称与用户姓名 -->
      <span class="tracking-wide">{{ roleConfig.title }}</span>
      <span class="text-[10px] opacity-75 font-mono">({{ currentUser?.real_name || '用户' }})</span>

      <!-- 圆圈问号帮助图标 (Help Icon) -->
      <span
        class="w-3.5 h-3.5 rounded-full flex items-center justify-center text-[10px] font-bold border transition-transform duration-200 group-hover:scale-110 ml-0.5"
        :class="helpIconClass"
        title="点击展开角色权限说明"
      >
        ?
      </span>
    </div>

    <!-- 悬浮弹窗 (Popover 浮层) -->
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-1 scale-95"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 translate-y-1 scale-95"
    >
      <div
        v-if="isOpen"
        @mouseenter="handleMouseEnter"
        @mouseleave="handleMouseLeave"
        class="role-permission-popover-card absolute bottom-full mb-2 left-0 w-80 sm:w-96 rounded-xl border p-4 shadow-xl z-50 backdrop-blur-md transition-all text-xs"
        :class="popoverCardClass"
      >
        <!-- 弹窗顶部：身份与归属说明 -->
        <div class="flex items-center justify-between pb-2.5 mb-2.5 border-b border-inherit/20">
          <div class="flex items-center space-x-2">
            <span class="p-1.5 rounded-lg border flex items-center justify-center shrink-0" :class="triggerClass">
              <!-- 顶部角标图标 -->
              <svg v-if="roleKey === 'STUDENT'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
              </svg>
              <svg v-else-if="roleKey === 'TEACHER'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </span>
            <div>
              <div class="font-semibold text-zinc-100 flex items-center space-x-1.5 popover-text-title">
                <span>{{ roleConfig.title }}权限指引</span>
                <span class="text-[10px] px-1 py-0.2 rounded font-mono border" :class="triggerClass">{{ roleKey }}</span>
              </div>
              <div class="text-[11px] text-zinc-400 popover-text-muted">
                {{ currentUser?.department || '公共机房中心' }} · {{ currentUser?.real_name || '用户' }}
              </div>
            </div>
          </div>
          <button
            @click.stop="isOpen = false"
            type="button"
            class="p-1 rounded hover:bg-white/10 text-zinc-400 hover:text-zinc-200 transition-colors"
            title="关闭提示"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 权限说明区：允许 vs 受限 -->
        <div class="space-y-3">
          <!-- 允许操作 -->
          <div>
            <div class="flex items-center space-x-1.5 font-medium text-emerald-400 text-[11px] mb-1.5">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span>允许执行的操作</span>
            </div>
            <ul class="space-y-1.5 pl-5 text-[11px] text-zinc-300 popover-list-item">
              <li v-for="(item, idx) in roleConfig.allowed" :key="idx" class="list-disc leading-relaxed">
                {{ item }}
              </li>
            </ul>
          </div>

          <!-- 受限边界 / 拦截禁区 -->
          <div v-if="roleConfig.restricted && roleConfig.restricted.length > 0">
            <div class="flex items-center space-x-1.5 font-medium text-amber-400 text-[11px] mb-1.5">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>受限操作边界 (系统将自动拦截)</span>
            </div>
            <ul class="space-y-1.5 pl-5 text-[11px] text-zinc-400 popover-list-restricted">
              <li v-for="(item, idx) in roleConfig.restricted" :key="idx" class="list-disc leading-relaxed">
                {{ item }}
              </li>
            </ul>
          </div>
          <div
            v-else
            class="p-2.5 rounded-lg border bg-emerald-500/10 border-emerald-500/20 text-emerald-400 text-[11px] flex items-center space-x-2"
          >
            <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>系统超级管理员拥有全栈最高管辖权，无任何操作受限边界</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
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

const isOpen = ref(false)
const popoverContainerRef = ref(null)
let closeTimer = null

const roleKey = computed(() => (props.currentUser?.role || 'STUDENT').toUpperCase())

const ROLE_PERMISSIONS = {
  STUDENT: {
    title: '学生身份',
    allowed: [
      '实时查看机房环境大盘、机柜拓扑及各服务器温度与负载监控',
      '在设备发生超温或离线告警时，向 AI 运维管家发起故障报修工单',
      '查阅机房用电安全条例、应急处置预案与日常巡检规程',
      '只读追踪工单流转进展、处理说明与故障排查记录',
    ],
    restricted: [
      '无法直接借调或归还机房服务器（须由指导教师代办）',
      '无法受理、推进或办结归档任何运维工单',
      '无权新增/编辑设备资产，无权新增/修改/废止安全规章规程',
    ],
  },
  TEACHER: {
    title: '教师身份',
    allowed: [
      '登记办理教学科研算力节点的借用出库与设备归还入库',
      '提报运维工单，受理工单并推进至“处理中”，追加处置进展',
      '在机房拓扑图谱中可视化拖拽调整机架设备的空间布局',
      '全文检索机房安全规约，向 AI 咨询规程细则与合规要求',
    ],
    restricted: [
      '无法最终办结或归档工单（须由管理员现场实测验收闭环）',
      '无法录入新规程、编辑或废止规程（安全规约库由管理员维护）',
      '无法删除核心硬件设备台账或变更机房物理空间规划',
    ],
  },
  ADMIN: {
    title: '管理员身份',
    allowed: [
      '全生命周期工单闭环：创建、受理、指派、实测温度验收与终审办结',
      '机房空间与资产全景运维：机房/机柜增删改、设备拖拽调度与健康标定',
      '安全规约库全生命周期：录入新规、智能语义切块、编辑修订与废止下线',
      '全局自主自治巡检调度，调优大模型参数与系统级运维策略',
    ],
    restricted: [],
  },
}

const roleConfig = computed(() => ROLE_PERMISSIONS[roleKey.value] || ROLE_PERMISSIONS.STUDENT)

// 样式根据身份药丸胶囊计算
const triggerClass = computed(() => {
  if (roleKey.value === 'STUDENT') {
    return 'bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
  } else if (roleKey.value === 'TEACHER') {
    return 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border-indigo-500/30'
  } else {
    return 'bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border-amber-500/30'
  }
})

const helpIconClass = computed(() => {
  if (roleKey.value === 'STUDENT') {
    return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
  } else if (roleKey.value === 'TEACHER') {
    return 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
  } else {
    return 'bg-amber-500/20 text-amber-300 border-amber-500/40'
  }
})

const popoverCardClass = computed(() => {
  return 'role-popover-card-theme'
})

function handleMouseEnter() {
  if (closeTimer) {
    clearTimeout(closeTimer)
    closeTimer = null
  }
  isOpen.value = true
}

function handleMouseLeave() {
  closeTimer = setTimeout(() => {
    isOpen.value = false
  }, 250)
}

function togglePopover() {
  isOpen.value = !isOpen.value
}

function handleClickOutside(e) {
  if (popoverContainerRef.value && !popoverContainerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  if (closeTimer) clearTimeout(closeTimer)
})
</script>

<style>
/* 明亮与暗黑模式深度适配 (采用全局类自适应) */
.role-popover-card-theme {
  background: rgba(20, 20, 25, 0.96);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 12px 36px -6px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);
}

/* 明亮模式高透白底冰晶风格 */
html.light .role-popover-card-theme {
  background: rgba(255, 255, 255, 0.98);
  border-color: rgba(226, 232, 240, 0.95);
  box-shadow: 0 14px 40px -8px rgba(15, 23, 42, 0.15), 0 0 0 1px rgba(226, 232, 240, 0.8);
}
html.light .role-popover-card-theme .popover-text-title {
  color: #0f172a !important;
}
html.light .role-popover-card-theme .popover-text-muted {
  color: #64748b !important;
}
html.light .role-popover-card-theme .popover-list-item {
  color: #334155 !important;
}
html.light .role-popover-card-theme .popover-list-restricted {
  color: #475569 !important;
}
</style>
