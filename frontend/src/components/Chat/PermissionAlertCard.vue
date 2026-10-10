<template>
  <div class="permission-alert-card rounded-2xl border p-4 sm:p-5 my-2 transition-all duration-200 shadow-lg backdrop-blur-md animate-fade-in">
    <!-- 卡片头部：加粗红色安全盾牌图标与醒目越权警示标题 -->
    <div class="flex items-start justify-between pb-3.5 border-b border-inherit/20 gap-3">
      <div class="flex items-center space-x-3 min-w-0">
        <!-- 核心视觉要素：加粗红色安全盾牌图标 (双层微光盾牌 + 感叹号安全锁) -->
        <span class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border shadow-xs alert-shield-icon">
          <svg class="w-5 h-5 alert-shield-svg" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
            <!-- 盾牌外形基底与轮廓 -->
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" class="shield-body" />
            <!-- 内嵌高亮安全感叹号 -->
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.6" d="M12 8v4m0 4h.01" class="shield-core" stroke="#fff" />
          </svg>
        </span>

        <div class="min-w-0">
          <div class="text-xs sm:text-sm font-bold tracking-wide flex items-center gap-2 alert-title">
            <span class="truncate" v-html="renderAlertMarkdown(parsedInfo.title || '越权敏感操作已被系统拦截')"></span>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold border shrink-0 alert-badge">
              403 RBAC 越权拦截
            </span>
          </div>
          <div class="text-[11px] font-mono mt-0.5 alert-subtitle truncate">
            机房分权安全管理策略已触发硬性安全联锁
          </div>
        </div>
      </div>

      <!-- 右侧尝试操作徽章 -->
      <div v-if="parsedInfo.action" class="shrink-0 text-right">
        <span class="text-[10px] px-2 py-0.5 rounded-md font-mono font-medium border alert-action-badge">
          {{ parsedInfo.action }}
        </span>
      </div>
    </div>

    <!-- 中间：拦截要素结构化呈现 (身份 -> 拦截原因 -> 权限边界 -> 办理指引) -->
    <div class="pt-3.5 space-y-3 text-xs">
      <!-- 1. 当前操作人身份 -->
      <div v-if="parsedInfo.identity" class="flex items-start space-x-2">
        <span class="font-bold shrink-0 alert-label">当前身份：</span>
        <span class="font-mono alert-val font-medium" v-html="renderAlertMarkdown(parsedInfo.identity)"></span>
      </div>

      <!-- 2. 核心拦截原因 (加粗红色警示高亮块) -->
      <div v-if="parsedInfo.reason" class="p-3 rounded-xl border alert-reason-box">
        <div class="font-bold text-[11px] mb-1 flex items-center gap-1.5 alert-reason-title">
          <svg class="w-3.5 h-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          <span>拦截原因</span>
        </div>
        <div class="text-[11.5px] leading-relaxed alert-reason-desc font-sans" v-html="renderAlertMarkdown(parsedInfo.reason)"></div>
      </div>

      <!-- 3. 身份权限边界 (明确受限角色可做与禁止做事项) -->
      <div v-if="parsedInfo.boundary" class="flex items-start space-x-2 text-[11.5px] leading-relaxed">
        <span class="font-bold shrink-0 alert-label">权限边界：</span>
        <span class="alert-boundary-text flex-1" v-html="renderAlertMarkdown(parsedInfo.boundary)"></span>
      </div>

      <!-- 4. 正确合规办理指引 (联系导师或专管员) -->
      <div v-if="parsedInfo.guide" class="pt-2.5 border-t border-inherit/20 flex items-start space-x-2 text-[11.5px] leading-relaxed">
        <span class="font-bold shrink-0 alert-guide-label mt-0.5">💡 办理指引：</span>
        <div class="alert-guide-text font-medium flex-1 space-y-1" v-html="renderAlertGuide(parsedInfo.guide)"></div>
      </div>

      <!-- 5. 附加细节说明 (若有大模型输出的多余正文或只读指引) -->
      <div v-if="parsedInfo.extraNotes" class="pt-2 text-[11px] opacity-80 alert-extra-notes border-t border-inherit/15" v-html="renderAlertMarkdown(parsedInfo.extraNotes)"></div>
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

// 轻量级安全行内 Markdown 渲染函数（彻底解析 **加粗**、`代码` 与 *斜体*，杜绝裸露星号）
function renderAlertMarkdown(str) {
  if (!str) return ''
  // 1. 转义 HTML 字符防止 XSS 攻击
  let s = String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 2. 提取并保护行内反引号代码 `code`
  const codes = []
  s = s.replace(/`([^`\n]+)`/g, (_, code) => {
    const ph = `__LABOPS_ALERT_CODE_${codes.length}__`
    codes.push(`<code class="alert-inline-code px-1.5 py-0.5 rounded font-mono text-[11px] font-semibold">${code}</code>`)
    return ph
  })

  // 3. 粗斜体与加粗语法解析
  s = s.replace(/\*\*\*(.+?)\*\*\*/g, '<strong class="font-bold text-inherit"><em>$1</em></strong>')
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong class="font-bold text-inherit">$1</strong>')
  s = s.replace(/\*([^*\n]+)\*/g, '<em class="text-inherit">$1</em>')

  // 4. 清理残留的孤立星号与格式符号（杜绝裸露的 ** 或孤立 *）
  s = s.replace(/\*\*+/g, '').replace(/(?:^|\s)\*(?:\s|$)/g, ' ')

  // 5. 安全还原行内代码 (使用回调函数防止 $ 字符插值误判)
  codes.forEach((c, i) => {
    s = s.replace(`__LABOPS_ALERT_CODE_${i}__`, () => c)
  })

  return s
}

// 办理指引结构化渲染函数（清洗前导垃圾字符并将 1. 2. 序号自动格式化为清晰的分行数字微标列表）
function renderAlertGuide(str) {
  if (!str) return ''
  // 清洗前导杂散字符（如原文本遗留的 "】 **" 或 ": "）
  let clean = String(str).replace(/^[\s\*\_】\]：:\-\—\.\,]+/, '').trim()

  // 智能规整分项序号：在分号/句号后的 " 1. "、" 2. " 以及紧随冒号的 " 1. " 处前置换行
  clean = clean.replace(/([；;。])\s*(\d+)\.\s*/g, '$1\n$2. ')
  clean = clean.replace(/([：:])\s*(\d+)\.\s*/g, '$1\n$2. ')

  const lines = clean.split(/\r?\n/).map(l => l.trim()).filter(Boolean)
  if (lines.length > 1) {
    return lines.map(line => {
      const listMatch = line.match(/^(\d+)\.\s*(.*)$/)
      if (listMatch) {
        return `<div class="flex items-start gap-1.5 mt-1.5 first:mt-0.5"><span class="w-4 h-4 rounded-full alert-guide-badge font-mono text-[10px] flex items-center justify-center shrink-0 mt-0.5 font-bold border">${listMatch[1]}</span><div class="flex-1">${renderAlertMarkdown(listMatch[2])}</div></div>`
      }
      return `<div>${renderAlertMarkdown(line)}</div>`
    }).join('')
  }

  return renderAlertMarkdown(clean)
}

const parsedInfo = computed(() => {
  const text = props.content || ''

  // 1. 标题提取 (优先匹配【权限拦截警报】或【权限拦截告知】后的内容，默认“越权敏感操作已被系统拦截”)
  const titleMatch = text.match(/【(?:权限拦截警报|权限拦截告知|越权拦截警报|越权拦截)】[：:\s]*(.*?)(?:\n|$)/)
  let title = titleMatch && titleMatch[1] ? titleMatch[1].trim() : ''
  // 彻底清洗包裹性符号 (如残留的 **、#、_、] 等)
  title = title.replace(/^[\*\#\_\]\】\:\s]+/, '').replace(/[\*\#\_\[\【\:\s]+$/, '').trim()
  if (!title || title.includes('告知') || title.includes('警报') || title.length <= 1) {
    title = '越权敏感操作已被系统拦截'
  }

  // 2. 尝试操作提取
  let action = ''
  const actionMatch = text.match(/(?:- 尝试操作|尝试操作|申请操作|\*\*尝试操作\*\*)[：:\s]*(.*?)(?:\n|$)/)
  if (actionMatch) {
    action = actionMatch[1].replace(/[\*\_`]/g, '').trim()
  } else if (text.includes('借出') || text.includes('借用') || text.includes('borrow_asset')) {
    action = '设备资产借调出库登记'
  } else if (text.includes('工单') && (text.includes('办结') || text.includes('关闭') || text.includes('流转'))) {
    action = '工单状态流转 / 终审办结'
  } else if (text.includes('健康') && (text.includes('修改') || text.includes('标定') || text.includes('下架报修'))) {
    action = '设备健康等级标定与状态变更'
  } else if (text.includes('设备') && (text.includes('增删') || text.includes('修改') || text.includes('下架'))) {
    action = '设备底层配置与物理状态变更'
  }

  // 3. 当前身份提取
  let identity = ''
  const idMatch = text.match(/(?:- 当前(?:操作用户|身份)|当前身份|您的身份|\*\*当前身份\*\*|\*\*您的身份\*\*)[：:\s]*(.*?)(?:\n|$)/)
  if (idMatch) {
    identity = idMatch[1].trim()
  } else {
    const studentMatch = text.match(/(.*?(?:同学|老师).*?)(?:您好|，|。)/)
    if (studentMatch && text.includes('STUDENT')) {
      identity = studentMatch[1].trim() + '（角色: 学生 STUDENT）'
    } else if (text.includes('学生') || text.includes('STUDENT')) {
      identity = '学生角色 (STUDENT)'
    }
  }
  identity = identity.replace(/^[\s\*\_：:\-]+/, '').replace(/[\s\*\_：:\-]+$/, '').trim()

  // 4. 拦截原因提取
  let reason = ''
  const reasonMatch = text.match(/(?:- 拦截原因|拦截原因|\*\*拦截原因\*\*)[：:\s]*(.*?)(?:\n-|\n\n|$)/s)
  if (reasonMatch) {
    reason = reasonMatch[1].trim()
  } else {
    // 宽泛自然语言提取
    const naturalReason = text.match(/(?:根据.*?准则.*?|根据.*?条例.*?)(?:，|。)(.*?)(?:因此|【|\n|$)/s)
    if (naturalReason) {
      reason = naturalReason[0].trim()
    } else if (text.includes('学生角色仅具有机房运行指标感知与工单只读查询权限')) {
      reason = '根据《高校机房资产安全管理条例》与 RBAC 三权分立安全准则，学生角色仅具有机房运行指标感知与工单只读查询权限，严禁调用 borrow_asset 等资产借调与底层管理工具。'
    } else {
      reason = '根据机房资产安全与分权管理规程，当前身份无权直接执行此项敏感写操作。'
    }
  }
  reason = reason.replace(/^[\s\*\_：:\-]+/, '').trim()

  // 5. 权限边界提取
  let boundary = ''
  const boundMatch = text.match(/(?:- 权限边界|权限边界|\*\*权限边界\*\*)[：:\s]*(.*?)(?:\n-|\n\n|$)/s)
  if (boundMatch) {
    boundary = boundMatch[1].trim()
  } else if (text.includes('只读查询') || text.includes('只读权限') || text.includes('只读感知')) {
    boundary = '学生身份仅可查验设备台账、运行监控与报修提单，严禁借调实体设备或修改运维工单。'
  }
  boundary = boundary.replace(/^[\s\*\_：:\-]+/, '').trim()

  // 6. 处置指引提取 (兼容各种前导符号)
  let guide = ''
  const guideMatch = text.match(/(?:- 处置指引|处置指引|办理途径|正确的办理途径|合规办理途径|\*\*处置指引\*\*|\*\*办理途径\*\*|\*\*正确的办理途径\*\*)[】\]\*\_：:\s]*(.*?)(?:\n-|\n\n【|$)/s)
  if (guideMatch) {
    guide = guideMatch[1].trim()
  } else if (text.includes('联系指导教师') || text.includes('导师')) {
    guide = '如需借用设备开展课程实验或科研，请联系您的指导教师（TEACHER 角色）或机房专管员（ADMIN 角色）登录系统代为办理。'
  }
  guide = guide.replace(/^[\s\*\_】\]：:\-\—\.\,]+/, '').trim()

  // 7. 备选补充说明 (若大模型输出了只读可协助内容)
  let extraNotes = ''
  if (text.includes('我可以为您做的') || text.includes('在权限范围内')) {
    extraNotes = '在权限范围内，系统可协助您完成运行指标感知与只读查询，供您和指导教师参考决策。'
  }

  return {
    title,
    action,
    identity,
    reason,
    boundary,
    guide,
    extraNotes,
  }
})
</script>

<style>
/* 核心视觉要素：红色警示安全盾牌卡片 (深色模式) */
.permission-alert-card {
  background: rgba(50, 10, 15, 0.65);
  border-color: rgba(244, 63, 94, 0.42);
  box-shadow: 0 10px 30px -4px rgba(225, 29, 72, 0.25), 0 0 0 1px rgba(244, 63, 94, 0.15);
}
.permission-alert-card .alert-shield-icon {
  background: rgba(244, 63, 94, 0.18);
  border-color: rgba(244, 63, 94, 0.45);
  color: #fb7185;
}
.permission-alert-card .alert-shield-svg .shield-body {
  fill: rgba(244, 63, 94, 0.25);
  stroke: #f43f5e;
}
.permission-alert-card .alert-title {
  color: #ffe4e6;
}
.permission-alert-card .alert-badge {
  background: rgba(225, 29, 72, 0.25);
  border-color: rgba(244, 63, 94, 0.5);
  color: #fecdd3;
}
.permission-alert-card .alert-subtitle {
  color: #fda4af;
}
.permission-alert-card .alert-action-badge {
  background: rgba(244, 63, 94, 0.15);
  border-color: rgba(244, 63, 94, 0.35);
  color: #fecdd3;
}
.permission-alert-card .alert-label {
  color: #fda4af;
}
.permission-alert-card .alert-val {
  color: #f3f4f6;
}
.permission-alert-card .alert-reason-box {
  background: rgba(20, 5, 8, 0.55);
  border-color: rgba(244, 63, 94, 0.32);
}
.permission-alert-card .alert-reason-title {
  color: #fb7185;
}
.permission-alert-card .alert-reason-desc {
  color: #ffe4e6;
}
.permission-alert-card .alert-boundary-text {
  color: #e2e8f0;
}
.permission-alert-card .alert-guide-label {
  color: #38bdf8;
}
.permission-alert-card .alert-guide-text {
  color: #bae6fd;
}
.permission-alert-card .alert-guide-badge {
  background: rgba(56, 189, 248, 0.18);
  border-color: rgba(56, 189, 248, 0.45);
  color: #38bdf8;
}
.permission-alert-card .alert-inline-code {
  background: rgba(244, 63, 94, 0.2);
  border: 1px solid rgba(244, 63, 94, 0.4);
  color: #fecdd3;
}
.permission-alert-card .alert-extra-notes {
  color: #cbd5e1;
}

/* 明亮模式高对比度红宝石警示适配 */
html.light .permission-alert-card {
  background: rgba(255, 241, 242, 0.98);
  border-color: rgba(244, 63, 94, 0.6);
  box-shadow: 0 8px 25px -4px rgba(225, 29, 72, 0.18), 0 0 0 1px rgba(244, 63, 94, 0.25);
}
html.light .permission-alert-card .alert-shield-icon {
  background: rgba(254, 205, 211, 0.95);
  border-color: rgba(244, 63, 94, 0.65);
  color: #e11d48;
}
html.light .permission-alert-card .alert-shield-svg .shield-body {
  fill: rgba(244, 63, 94, 0.2);
  stroke: #e11d48;
}
html.light .permission-alert-card .alert-title {
  color: #881337 !important;
}
html.light .permission-alert-card .alert-badge {
  background: rgba(255, 228, 230, 0.95);
  border-color: rgba(225, 29, 72, 0.55);
  color: #be123c;
}
html.light .permission-alert-card .alert-subtitle {
  color: #9f1239 !important;
}
html.light .permission-alert-card .alert-action-badge {
  background: rgba(255, 228, 230, 0.95);
  border-color: rgba(244, 63, 94, 0.45);
  color: #9f1239;
}
html.light .permission-alert-card .alert-label {
  color: #9f1239 !important;
}
html.light .permission-alert-card .alert-val {
  color: #0f172a !important;
}
html.light .permission-alert-card .alert-reason-box {
  background: rgba(255, 255, 255, 0.96);
  border-color: rgba(244, 63, 94, 0.4);
}
html.light .permission-alert-card .alert-reason-title {
  color: #be123c !important;
}
html.light .permission-alert-card .alert-reason-desc {
  color: #881337 !important;
}
html.light .permission-alert-card .alert-boundary-text {
  color: #334155 !important;
}
html.light .permission-alert-card .alert-guide-label {
  color: #0284c7 !important;
}
html.light .permission-alert-card .alert-guide-text {
  color: #0369a1 !important;
}
html.light .permission-alert-card .alert-guide-badge {
  background: rgba(186, 230, 253, 0.75);
  border-color: rgba(2, 132, 199, 0.5);
  color: #0369a1 !important;
}
html.light .permission-alert-card .alert-inline-code {
  background: rgba(254, 205, 211, 0.85);
  border: 1px solid rgba(244, 63, 94, 0.5);
  color: #9f1239 !important;
}
html.light .permission-alert-card .alert-extra-notes {
  color: #475569;
}
</style>
