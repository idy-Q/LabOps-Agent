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
      :title="`当前身份：${roleConfig.title}。点击或悬停查看权限说明与推荐提示词`"
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
        title="点击展开权限与提示词说明"
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
        <div class="space-y-2.5 mb-3">
          <!-- 允许操作 -->
          <div>
            <div class="flex items-center space-x-1.5 font-medium text-emerald-400 text-[11px] mb-1">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <span>允许执行的操作</span>
            </div>
            <ul class="space-y-1 pl-5 text-[11px] text-zinc-300 popover-list-item">
              <li v-for="(item, idx) in roleConfig.allowed" :key="idx" class="list-disc leading-relaxed">
                {{ item }}
              </li>
            </ul>
          </div>

          <!-- 受限边界 / 拦截禁区 -->
          <div v-if="roleConfig.restricted && roleConfig.restricted.length > 0">
            <div class="flex items-center space-x-1.5 font-medium text-amber-400 text-[11px] mb-1">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>权限受限边界 (触发将拦截提醒)</span>
            </div>
            <ul class="space-y-1 pl-5 text-[11px] text-zinc-400 popover-list-restricted">
              <li v-for="(item, idx) in roleConfig.restricted" :key="idx" class="list-disc leading-relaxed">
                {{ item }}
              </li>
            </ul>
          </div>
        </div>

        <!-- 快捷提示词指引 (点击直接填入输入框) -->
        <div class="pt-2.5 border-t border-inherit/20">
          <div class="text-[11px] font-medium text-zinc-300 popover-text-title mb-1.5 flex items-center justify-between">
            <span class="flex items-center gap-1">
              <span>💡 推荐常用提示词 (点击填入)</span>
            </span>
            <span class="text-[10px] text-zinc-500">点选即用</span>
          </div>
          <div class="space-y-1.5">
            <button
              v-for="(prompt, pIdx) in roleConfig.prompts"
              :key="pIdx"
              type="button"
              @click.stop="handleSelectPrompt(prompt)"
              class="w-full text-left px-2.5 py-1.5 rounded-lg border text-[11px] transition-all flex items-center justify-between group active:scale-[0.99]"
              :class="promptButtonClass"
              :title="`填入提示词: ${prompt}`"
            >
              <span class="truncate pr-2 font-mono text-[10.5px]">{{ prompt }}</span>
              <span class="text-[10px] opacity-60 group-hover:opacity-100 text-indigo-400 shrink-0 font-sans">填入 ↵</span>
            </button>
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

const emit = defineEmits(['fill-prompt'])

const isOpen = ref(false)
const popoverContainerRef = ref(null)
let closeTimer = null

const roleKey = computed(() => (props.currentUser?.role || 'STUDENT').toUpperCase())

const ROLE_PERMISSIONS = {
  STUDENT: {
    title: '学生身份',
    allowed: [
      '感知机房环境指标与各服务器温度、CPU实时负载',
      '超温（>40℃）告警或脱网故障自动触发报修工单',
      '检索机房用电防火管理规章、应急处置与借调规范',
      '只读查询全部工单进展、待办清单与排查日志',
    ],
    restricted: [
      '禁止直接借调机房服务器或固定设备（需指导教师代办）',
      '禁止修改运维工单流转状态（如认领或办结归档）',
      '禁止手动改写硬件健康等级台账或删除添加设备',
    ],
    prompts: [
      '查询 DEV-SRV-201 的实时监控指标，若异常请自动提单',
      '查一下机房用电安全和防火巡检的相关规定',
      '查询工单 TK-20260901-001 的处置进展',
    ],
  },
  TEACHER: {
    title: '教师身份',
    allowed: [
      '办理科研或教学实验算力节点的借调登记与归还出入库',
      '受理工单并流转推进至处理中（PROCESSING），追加维保备注',
      '查验机房服务器运行大盘、历史工单与应急规程条例',
    ],
    restricted: [
      '禁止直接办结或归档工单（须由机房专职主管现场实地验收闭环）',
      '禁止擅自修改硬件健康台账等级或变更物理供电配置',
    ],
    prompts: [
      '帮我办理 DEV-SRV-202 服务器的借用登记，用途为课程实验',
      '受理工单 TK-20260901-001 并标记为处理中',
      '办理设备 DEV-SRV-202 的归还登记',
    ],
  },
  ADMIN: {
    title: '管理员身份',
    allowed: [
      '全生命周期工单管理：创建、分派、受理、终审验收与关闭归档',
      '资产台账全量运维：设备增删改查、借调归还、硬件健康状态标定',
      '机房安全规程知识库检视与多智能体自主决策全局调度',
    ],
    restricted: [],
    prompts: [
      '排查全部机房指标异常设备并按规章自动提单闭环',
      '将设备 DEV-SRV-201 健康等级标记为正常',
      '办结工单 TK-20260901-001 并验收归档',
    ],
  },
}

const roleConfig = computed(() => ROLE_PERMISSIONS[roleKey.value] || ROLE_PERMISSIONS.STUDENT)

// 样式根据暗黑与明亮模式计算
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
  // class 结合 CSS 自定义样式保证高质感
  return 'role-popover-card-theme'
})

const promptButtonClass = computed(() => {
  return 'role-prompt-btn-theme'
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

function handleSelectPrompt(prompt) {
  emit('fill-prompt', prompt)
  isOpen.value = false
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
/* 明亮与暗黑模式适配 (采用全局类自适应，确保不会被 scoped 截断) */
.role-popover-card-theme {
  background: rgba(20, 20, 25, 0.96);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 12px 36px -6px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);
}

.role-prompt-btn-theme {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
  color: #d4d4d8;
}
.role-prompt-btn-theme:hover {
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.35);
  color: #ffffff;
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
html.light .role-prompt-btn-theme {
  background: rgba(248, 250, 252, 0.95);
  border-color: rgba(226, 232, 240, 0.9);
  color: #334155;
}
html.light .role-prompt-btn-theme:hover {
  background: rgba(238, 242, 255, 0.95);
  border-color: rgba(129, 140, 248, 0.6);
  color: #4338ca;
}
</style>
