<template>
  <div class="permission-alert-card rounded-2xl border p-4 sm:p-5 my-1.5 transition-all duration-200 shadow-md backdrop-blur-sm animate-fade-in">
    <!-- 卡片头部：盾牌图标与告警标题 -->
    <div class="flex items-start justify-between pb-3 border-b border-inherit/20 gap-2">
      <div class="flex items-center space-x-2.5">
        <!-- 矢量警示盾牌图标 -->
        <span class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border shadow-xs alert-shield-icon">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </span>
        <div>
          <div class="text-xs sm:text-sm font-semibold tracking-wide flex items-center gap-2 alert-title">
            <span>{{ parsedInfo.title || '权限拦截警报 / PERMISSION DENIED' }}</span>
            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded border alert-badge">
              403 越权拦截
            </span>
          </div>
          <div class="text-[11px] opacity-75 font-mono mt-0.5 alert-subtitle">
            机房分权安全管理策略已触发硬性拦截
          </div>
        </div>
      </div>

      <!-- 右侧尝试操作微标 -->
      <div v-if="parsedInfo.action" class="shrink-0 text-right">
        <span class="text-[10px] px-2 py-0.5 rounded font-medium border alert-action-badge">
          {{ parsedInfo.action }}
        </span>
      </div>
    </div>

    <!-- 中间：拦截信息分块结构化展示 -->
    <div class="pt-3 space-y-2.5 text-xs">
      <!-- 1. 当前操作人身份 -->
      <div v-if="parsedInfo.identity" class="flex items-start space-x-2">
        <span class="font-medium shrink-0 alert-label">当前身份：</span>
        <span class="font-mono alert-val">{{ parsedInfo.identity }}</span>
      </div>

      <!-- 2. 核心拦截原因 (警示高亮块) -->
      <div v-if="parsedInfo.reason" class="p-2.5 rounded-xl border alert-reason-box">
        <div class="font-medium text-[11px] mb-1 flex items-center gap-1.5 alert-reason-title">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          <span>拦截原因</span>
        </div>
        <p class="text-[11.5px] leading-relaxed alert-reason-desc">
          {{ parsedInfo.reason }}
        </p>
      </div>

      <!-- 3. 身份权限边界 (告知用户当前身份可做与不可做) -->
      <div v-if="parsedInfo.boundary" class="flex items-start space-x-2 text-[11.5px] leading-relaxed">
        <span class="font-medium shrink-0 alert-label">权限边界：</span>
        <span class="alert-boundary-text">{{ parsedInfo.boundary }}</span>
      </div>

      <!-- 4. 正确处置指引 (指引找导师或专管员) -->
      <div v-if="parsedInfo.guide" class="pt-2 border-t border-inherit/20 flex items-start space-x-2 text-[11.5px] leading-relaxed">
        <span class="font-medium shrink-0 alert-guide-label">💡 办理指引：</span>
        <span class="alert-guide-text">{{ parsedInfo.guide }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: String,
    required: true,
  },
})

const parsedInfo = computed(() => {
  const text = props.content || ''

  // 1. 标题提取 (如 "【权限拦截警报】借调申请已被系统拦截！")
  const titleMatch = text.match(/【权限拦截警报】(.*?)(?:\n|$)/)
  const title = titleMatch ? titleMatch[1].trim() : '权限拦截警报'

  // 2. 尝试操作提取
  const actionMatch = text.match(/- 尝试操作[：:\s]*(.*?)(?:\n|$)/)
  const action = actionMatch ? actionMatch[1].trim() : ''

  // 3. 当前身份提取
  const idMatch = text.match(/- 当前(?:操作用户|身份)[：:\s]*(.*?)(?:\n|$)/)
  const identity = idMatch ? idMatch[1].trim() : ''

  // 4. 拦截原因提取
  const reasonMatch = text.match(/- 拦截原因[：:\s]*(.*?)(?:\n-|\n\n|$)/s)
  const reason = reasonMatch ? reasonMatch[1].trim() : ''

  // 5. 权限边界提取
  const boundMatch = text.match(/- 权限边界[：:\s]*(.*?)(?:\n-|\n\n|$)/s)
  const boundary = boundMatch ? boundMatch[1].trim() : ''

  // 6. 处置指引提取
  const guideMatch = text.match(/- 处置指引[：:\s]*(.*?)(?:\n-|\n\n|$)/s)
  const guide = guideMatch ? guideMatch[1].trim() : ''

  return {
    title,
    action,
    identity,
    reason,
    boundary,
    guide,
  }
})
</script>

<style>
/* 默认暗黑风格样式 */
.permission-alert-card {
  background: rgba(41, 23, 15, 0.55);
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 4px 20px -4px rgba(245, 158, 11, 0.15);
}
.permission-alert-card .alert-shield-icon {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.35);
  color: #fbbf24;
}
.permission-alert-card .alert-title {
  color: #fef3c7;
}
.permission-alert-card .alert-badge {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}
.permission-alert-card .alert-subtitle {
  color: #d97706;
}
.permission-alert-card .alert-action-badge {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.25);
  color: #fde68a;
}
.permission-alert-card .alert-label {
  color: #fbbf24;
}
.permission-alert-card .alert-val {
  color: #f3f4f6;
}
.permission-alert-card .alert-reason-box {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(245, 158, 11, 0.2);
}
.permission-alert-card .alert-reason-title {
  color: #f59e0b;
}
.permission-alert-card .alert-reason-desc {
  color: #fef3c7;
}
.permission-alert-card .alert-boundary-text {
  color: #e5e7eb;
}
.permission-alert-card .alert-guide-label {
  color: #60a5fa;
}
.permission-alert-card .alert-guide-text {
  color: #93c5fd;
}

/* 明亮模式适配 */
html.light .permission-alert-card {
  background: rgba(255, 251, 235, 0.96);
  border-color: rgba(251, 191, 36, 0.6);
  box-shadow: 0 8px 24px -4px rgba(217, 119, 6, 0.12), 0 0 0 1px rgba(251, 191, 36, 0.3);
}
html.light .permission-alert-card .alert-shield-icon {
  background: rgba(254, 243, 199, 0.95);
  border-color: rgba(245, 158, 11, 0.5);
  color: #d97706;
}
html.light .permission-alert-card .alert-title {
  color: #78350f !important;
}
html.light .permission-alert-card .alert-badge {
  background: rgba(254, 226, 226, 0.95);
  border-color: rgba(239, 68, 68, 0.4);
  color: #b91c1c;
}
html.light .permission-alert-card .alert-subtitle {
  color: #b45309 !important;
}
html.light .permission-alert-card .alert-action-badge {
  background: rgba(254, 243, 199, 0.9);
  border-color: rgba(245, 158, 11, 0.4);
  color: #92400e;
}
html.light .permission-alert-card .alert-label {
  color: #b45309 !important;
}
html.light .permission-alert-card .alert-val {
  color: #1e293b !important;
}
html.light .permission-alert-card .alert-reason-box {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(251, 191, 36, 0.4);
}
html.light .permission-alert-card .alert-reason-title {
  color: #b45309 !important;
}
html.light .permission-alert-card .alert-reason-desc {
  color: #78350f !important;
}
html.light .permission-alert-card .alert-boundary-text {
  color: #334155 !important;
}
html.light .permission-alert-card .alert-guide-label {
  color: #2563eb !important;
}
html.light .permission-alert-card .alert-guide-text {
  color: #1d4ed8 !important;
}
</style>
