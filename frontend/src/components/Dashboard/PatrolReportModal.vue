<template>
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
      class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-hidden print:p-0 print:bg-white print:static print:inset-auto print:overflow-visible transition-colors"
      :class="theme === 'light' ? 'bg-slate-900/35 backdrop-blur-sm' : 'bg-black/80 backdrop-blur-md'"
      @click.self="close"
    >
      <!-- 简报主体卡片 -->
      <div
        id="printable-patrol-report"
        class="patrol-modal-card w-full max-w-3xl rounded-2xl sm:rounded-3xl border flex flex-col max-h-[92vh] overflow-hidden transition-all print:max-h-none print:shadow-none print:border-none print:rounded-none"
        :class="[
          theme === 'light'
            ? 'bg-white border-slate-200/90 shadow-2xl shadow-slate-400/20 text-slate-900'
            : 'bg-zinc-950/95 border-white/[0.12] shadow-2xl text-zinc-100'
        ]"
      >
        <!-- 1. 顶部 Header -->
        <div
          class="flex items-center justify-between border-b px-5 py-4 shrink-0"
          :class="theme === 'light' ? 'border-slate-200 bg-slate-50/90' : 'border-white/[0.08] bg-white/[0.02]'"
        >
          <div class="flex items-center space-x-3 min-w-0 pr-2">
            <div
              class="p-2 rounded-xl border shrink-0 shadow-sm"
              :class="iconBadgeClass"
            >
              <!-- 盾牌雷达脉冲图标 -->
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>

            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap sm:flex-nowrap">
                <h2
                  class="text-sm sm:text-base font-bold tracking-tight shrink-0"
                  :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'"
                >
                  高校实验室 IT 基础设施运行健康研判简报
                </h2>
                <!-- 态势评级胶囊：保证单行不折行、饱满精致 -->
                <span
                  class="px-2.5 py-0.5 rounded-full text-[10px] font-mono border font-semibold whitespace-nowrap shrink-0"
                  :class="postureBadgeClass"
                >
                  {{ reportData.posture_text || '态势平稳' }}
                </span>
              </div>
              <div
                class="flex items-center space-x-2.5 mt-1 text-[11px] font-mono flex-wrap"
                :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
              >
                <span>批次: <strong class="font-medium select-all" :class="theme === 'light' ? 'text-indigo-600' : 'text-indigo-400'">{{ reportData.batch_no || 'PTR-实时巡检' }}</strong></span>
                <span :class="theme === 'light' ? 'text-slate-300' : 'text-zinc-600'">|</span>
                <span>巡检专员: <span :class="theme === 'light' ? 'text-slate-700 font-medium' : 'text-zinc-300'">{{ reportData.operator || '系统自治巡检' }}</span></span>
                <span class="hidden sm:inline" :class="theme === 'light' ? 'text-slate-300' : 'text-zinc-600'">|</span>
                <span class="hidden sm:inline">{{ reportData.patrol_time }}</span>
              </div>
            </div>
          </div>

          <button
            @click="close"
            class="p-1.5 rounded-lg transition-colors shrink-0 print:hidden"
            :class="theme === 'light' ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-200/60' : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.08]'"
            title="关闭简报"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 2. 可滚动内容区 -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 print:p-0 print:overflow-visible">
          <!-- 2.1 态势综合评分仪表 + KPI 磁贴阵列 -->
          <div class="grid grid-cols-1 md:grid-cols-12 gap-3 items-stretch">
            <!-- 左侧仪表盘 (5 Cols) -->
            <div
              class="md:col-span-5 rounded-xl border p-3.5 flex flex-col items-center justify-center relative overflow-hidden"
              :class="theme === 'light' ? 'bg-slate-50/90 border-slate-200 shadow-sm' : 'bg-zinc-900/60 border-white/[0.08]'"
            >
              <div
                class="text-[11px] font-medium mb-1.5"
                :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
              >
                机房综合健康态势指数
              </div>
              <div class="relative w-28 h-28 flex items-center justify-center my-0.5">
                <!-- SVG 环形进度仪表 -->
                <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    :class="theme === 'light' ? 'stroke-slate-200' : 'stroke-zinc-800'"
                    stroke-width="8"
                    fill="none"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    :class="meterStrokeColor"
                    stroke-width="8"
                    stroke-linecap="round"
                    fill="none"
                    :stroke-dasharray="circumference"
                    :stroke-dashoffset="meterDashOffset"
                    class="transition-all duration-1000 ease-out"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span class="text-3xl font-black font-mono tracking-tight" :class="meterTextColor">
                    {{ healthScore }}
                  </span>
                  <span
                    class="text-[9px] font-mono -mt-0.5"
                    :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                  >
                    / 100 分
                  </span>
                </div>
              </div>
              <div class="text-xs font-semibold text-center mt-1" :class="meterTextColor">
                {{ reportData.posture_text || '整体平稳' }}
              </div>
            </div>

            <!-- 右侧 4 大 KPI 磁贴 (7 Cols) -->
            <div class="md:col-span-7 grid grid-cols-2 gap-2">
              <!-- 受检总览 -->
              <div
                class="rounded-xl border p-2.5 flex flex-col justify-between"
                :class="theme === 'light' ? 'bg-slate-50/90 border-slate-200 shadow-sm' : 'bg-zinc-900/60 border-white/[0.08]'"
              >
                <div
                  class="text-[11px] flex items-center justify-between"
                  :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                >
                  <span>受检资产全景</span>
                  <span class="text-xs">🖥️</span>
                </div>
                <div class="my-0.5">
                  <span
                    class="text-lg font-bold font-mono"
                    :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'"
                  >
                    {{ kpi.total_scanned || 0 }}
                  </span>
                  <span class="text-xs ml-1" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">台</span>
                </div>
                <div
                  class="text-[10px] font-mono pt-1 border-t flex justify-between"
                  :class="theme === 'light' ? 'border-slate-200/80 text-slate-500' : 'border-white/[0.04] text-zinc-400'"
                >
                  <span class="text-emerald-600 font-medium">正常: {{ kpi.healthy_count || 0 }}</span>
                  <span :class="kpi.overheat_count > 0 ? 'text-rose-600 font-semibold' : (theme === 'light' ? 'text-slate-400' : 'text-zinc-500')">
                    超温: {{ kpi.overheat_count || 0 }}
                  </span>
                </div>
              </div>

              <!-- 微环境均温 -->
              <div
                class="rounded-xl border p-2.5 flex flex-col justify-between"
                :class="theme === 'light' ? 'bg-slate-50/90 border-slate-200 shadow-sm' : 'bg-zinc-900/60 border-white/[0.08]'"
              >
                <div
                  class="text-[11px] flex items-center justify-between"
                  :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                >
                  <span>微环境均温</span>
                  <span class="text-xs">🌡️</span>
                </div>
                <div class="my-0.5 flex items-baseline space-x-1">
                  <span
                    class="text-lg font-bold font-mono"
                    :class="kpi.avg_temperature >= 40 ? 'text-rose-600' : kpi.avg_temperature >= 38 ? 'text-amber-600' : (theme === 'light' ? 'text-slate-900' : 'text-zinc-100')"
                  >
                    {{ kpi.avg_temperature || 25.0 }}
                  </span>
                  <span class="text-xs" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">℃</span>
                </div>
                <div
                  class="text-[10px] font-mono pt-1 border-t flex justify-between"
                  :class="theme === 'light' ? 'border-slate-200/80 text-slate-500' : 'border-white/[0.04] text-zinc-400'"
                >
                  <span>安全阈值: 40℃</span>
                  <span :class="kpi.avg_temperature < 40 ? 'text-emerald-600 font-medium' : 'text-rose-600 font-semibold'">
                    {{ kpi.avg_temperature < 40 ? '正常' : '越界' }}
                  </span>
                </div>
              </div>

              <!-- 算力集群均载 -->
              <div
                class="rounded-xl border p-2.5 flex flex-col justify-between"
                :class="theme === 'light' ? 'bg-slate-50/90 border-slate-200 shadow-sm' : 'bg-zinc-900/60 border-white/[0.08]'"
              >
                <div
                  class="text-[11px] flex items-center justify-between"
                  :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                >
                  <span>算力集群均载</span>
                  <span class="text-xs">⚡</span>
                </div>
                <div class="my-0.5 flex items-baseline space-x-1">
                  <span
                    class="text-lg font-bold font-mono"
                    :class="theme === 'light' ? 'text-cyan-700' : 'text-cyan-400'"
                  >
                    {{ kpi.avg_cpu_load || 0 }}
                  </span>
                  <span class="text-xs" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">%</span>
                </div>
                <div
                  class="text-[10px] font-mono pt-1 border-t"
                  :class="theme === 'light' ? 'border-slate-200/80 text-slate-500' : 'border-white/[0.04] text-zinc-400'"
                >
                  <span>负荷状态: 平稳</span>
                </div>
              </div>

              <!-- 动力总功耗 -->
              <div
                class="rounded-xl border p-2.5 flex flex-col justify-between"
                :class="theme === 'light' ? 'bg-slate-50/90 border-slate-200 shadow-sm' : 'bg-zinc-900/60 border-white/[0.08]'"
              >
                <div
                  class="text-[11px] flex items-center justify-between"
                  :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                >
                  <span>实时供电负荷</span>
                  <span class="text-xs">🔌</span>
                </div>
                <div class="my-0.5 flex items-baseline space-x-1">
                  <span
                    class="text-lg font-bold font-mono"
                    :class="theme === 'light' ? 'text-indigo-700' : 'text-indigo-400'"
                  >
                    {{ kpi.total_power_watts || 0 }}
                  </span>
                  <span class="text-xs" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">W</span>
                </div>
                <div
                  class="text-[10px] font-mono pt-1 border-t"
                  :class="theme === 'light' ? 'border-slate-200/80 text-slate-500' : 'border-white/[0.04] text-zinc-400'"
                >
                  <span>PDU负荷: {{ Math.round(((kpi.total_power_watts || 0) / 4500) * 100) }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 2.2 巡检研判简报总结摘要 -->
          <div
            class="rounded-xl border p-3 text-xs leading-relaxed"
            :class="theme === 'light' ? 'bg-blue-50/80 border-blue-200 text-slate-800' : 'bg-indigo-950/20 border-indigo-500/20 text-indigo-200'"
          >
            <div
              class="font-semibold flex items-center space-x-1.5 mb-1"
              :class="theme === 'light' ? 'text-blue-700' : 'text-indigo-400'"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>研判结论与自主处置概况</span>
            </div>
            <p class="leading-normal">{{ reportData.summary_text || '机房基础设施主动巡检完成，各项遥测参数符合安全管理要求。' }}</p>
          </div>

          <!-- 2.3 异常设备排查台账与自治闭环工单 -->
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <h3
                class="text-xs sm:text-sm font-semibold flex items-center space-x-2"
                :class="theme === 'light' ? 'text-slate-800' : 'text-zinc-200'"
              >
                <span
                  class="p-1 rounded border"
                  :class="theme === 'light' ? 'bg-amber-100 border-amber-300 text-amber-800' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'"
                >
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </span>
                <span>隐患异常设备台账 ({{ abnormalDevices.length }} 处)</span>
              </h3>
              <span class="text-[11px]" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">点击工单标签可快速跳转受理</span>
            </div>

            <!-- 无异常状态展示 -->
            <div
              v-if="abnormalDevices.length === 0"
              class="py-6 rounded-xl border text-center space-y-1.5"
              :class="theme === 'light' ? 'bg-emerald-50/80 border-emerald-200 text-emerald-800' : 'bg-emerald-950/10 border-emerald-500/20 text-emerald-400'"
            >
              <div class="text-xl">🎉</div>
              <div class="text-xs font-semibold">全机房在册设备运行良好，未检测到超温或脱网隐患</div>
              <div class="text-[11px] font-mono" :class="theme === 'light' ? 'text-emerald-700' : 'text-zinc-400'">
                全部温度均在 40℃ 安全阈值内，网络及供电连接通畅
              </div>
            </div>

            <!-- 异常节点卡片列表 -->
            <div v-else class="space-y-2">
              <div
                v-for="dev in abnormalDevices"
                :key="dev.asset_no"
                class="rounded-xl border p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs transition-all shadow-sm"
                :class="[
                  theme === 'light'
                    ? (dev.is_overheat ? 'bg-rose-50/70 border-rose-200' : dev.is_offline ? 'bg-slate-50 border-slate-200' : 'bg-amber-50/70 border-amber-200')
                    : (dev.is_overheat ? 'bg-rose-950/20 border-rose-500/30' : dev.is_offline ? 'bg-zinc-900/80 border-white/[0.1]' : 'bg-amber-950/20 border-amber-500/30')
                ]"
              >
                <!-- 设备基本与遥测信息 -->
                <div class="space-y-1 min-w-0">
                  <div class="flex items-center space-x-2 flex-wrap gap-1">
                    <span
                      class="font-mono font-bold select-all"
                      :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-200'"
                    >
                      {{ dev.asset_no }}
                    </span>
                    <span :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">({{ dev.name }})</span>
                    <span
                      class="px-2 py-0.5 rounded text-[10px] font-mono font-medium border whitespace-nowrap"
                      :class="[
                        dev.is_overheat
                          ? (theme === 'light' ? 'bg-rose-100 border-rose-300 text-rose-700' : 'bg-rose-500/10 border-rose-500/30 text-rose-400')
                          : dev.is_offline
                          ? (theme === 'light' ? 'bg-slate-200 border-slate-300 text-slate-700' : 'bg-zinc-800 border-white/[0.1] text-zinc-400')
                          : (theme === 'light' ? 'bg-amber-100 border-amber-300 text-amber-800' : 'bg-amber-500/10 border-amber-500/30 text-amber-400')
                      ]"
                    >
                      {{ dev.is_overheat ? '超温告警' : dev.is_offline ? '脱网离线' : '预警' }}
                    </span>
                  </div>

                  <div
                    class="text-[11px] flex items-center space-x-3 flex-wrap font-mono"
                    :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'"
                  >
                    <span>位置: {{ dev.location }}</span>
                    <span>温度: <strong :class="dev.temperature >= 40 ? 'text-rose-600 font-bold' : 'text-amber-600 font-bold'">{{ dev.temperature }}℃</strong></span>
                    <span>CPU: {{ dev.cpu_usage }}%</span>
                    <span>功耗: {{ dev.power_watts }}W</span>
                  </div>

                  <div class="text-[11px]" :class="theme === 'light' ? (dev.is_overheat ? 'text-rose-950 font-medium' : dev.is_offline ? 'text-slate-700 font-medium' : 'text-amber-950 font-medium') : 'text-zinc-400'">
                    {{ dev.alert_message || '检测到传感器指标偏离正常基线。' }}
                  </div>
                </div>

                <!-- 自治工单闭环标签与操作 -->
                <div class="shrink-0 flex items-center space-x-2 self-end sm:self-center">
                  <button
                    v-if="dev.ticket_no"
                    @click="jumpToTicket(dev.ticket_no)"
                    class="px-2.5 py-1 rounded-lg border text-xs font-mono font-semibold flex items-center space-x-1 transition-all active:scale-95 shadow-sm"
                    :class="[
                      dev.ticket_action === 'CREATED'
                        ? (theme === 'light' ? 'bg-rose-100/90 border-rose-300 text-rose-800 hover:bg-rose-200' : 'bg-rose-500/15 border-rose-500/40 text-rose-300 hover:bg-rose-500/25')
                        : (theme === 'light' ? 'bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100' : 'bg-indigo-500/15 border-indigo-500/40 text-indigo-300 hover:bg-indigo-500/25')
                    ]"
                    :title="`点击在工单流转库中聚焦工单 ${dev.ticket_no}`"
                  >
                    <span>{{ dev.ticket_action === 'CREATED' ? '🆕 自动建单' : '🔄 跟踪工单' }}</span>
                    <span>{{ dev.ticket_no }}</span>
                    <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </button>
                  <span
                    v-else
                    class="px-2 py-0.5 rounded text-[10px] border"
                    :class="theme === 'light' ? 'bg-slate-100 text-slate-600 border-slate-200' : 'bg-zinc-800 text-zinc-500 border-white/[0.06]'"
                  >
                    例行监控
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 2.4 RAG 知识库规程条款溯源 -->
          <div class="space-y-2">
            <h3
              class="text-xs sm:text-sm font-semibold flex items-center space-x-2"
              :class="theme === 'light' ? 'text-slate-800' : 'text-zinc-200'"
            >
              <span
                class="p-1 rounded border"
                :class="theme === 'light' ? 'bg-indigo-100 border-indigo-300 text-indigo-700' : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </span>
              <span>RAG 规程溯源与处置依据</span>
            </h3>

            <div class="space-y-2">
              <div
                v-for="(reg, idx) in citedRegulations"
                :key="idx"
                class="rounded-xl border p-2.5 text-xs space-y-1"
                :class="theme === 'light' ? 'bg-slate-50/90 border-slate-200 text-slate-800' : 'bg-zinc-900/60 border-white/[0.08] text-zinc-300'"
              >
                <div
                  class="flex items-center space-x-2 font-medium"
                  :class="theme === 'light' ? 'text-indigo-700' : 'text-indigo-400'"
                >
                  <span>📖 《{{ reg.doc_name }}》</span>
                  <span v-if="reg.clause" class="font-mono text-[10px]" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">
                    [{{ reg.clause }}]
                  </span>
                </div>
                <p
                  class="text-[11px] leading-relaxed italic"
                  :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'"
                >
                  “{{ reg.content }}”
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. 底部操作工具栏 (Action Toolbar) -->
        <div
          class="border-t px-5 py-3 flex items-center justify-between shrink-0 print:hidden"
          :class="theme === 'light' ? 'border-slate-200 bg-slate-50/90' : 'border-white/[0.08] bg-white/[0.02]'"
        >
          <div class="flex items-center space-x-2">
            <!-- 一键复制 Markdown 报告 -->
            <button
              @click="copyMarkdownReport"
              class="px-3 py-1.5 rounded-xl border text-xs font-medium flex items-center space-x-1.5 transition-all active:scale-95 shadow-sm"
              :class="[
                copied
                  ? (theme === 'light' ? 'bg-emerald-100 border-emerald-400 text-emerald-800' : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300')
                  : (theme === 'light' ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300' : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border-white/[0.1] hover:border-white/[0.2]')
              ]"
            >
              <svg v-if="!copied" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" :class="theme === 'light' ? 'text-emerald-700' : 'text-emerald-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>{{ copied ? '已复制 Markdown' : '复制简报 (Markdown)' }}</span>
            </button>

            <!-- 打印报告 / 导出 PDF -->
            <button
              @click="printReport"
              class="px-3 py-1.5 rounded-xl border text-xs font-medium flex items-center space-x-1.5 transition-all active:scale-95 shadow-sm"
              :class="[
                theme === 'light'
                  ? 'bg-white hover:bg-indigo-50 text-indigo-700 border-indigo-200 hover:border-indigo-300'
                  : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border-white/[0.1] hover:border-white/[0.2]'
              ]"
            >
              <svg class="w-3.5 h-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <span>打印简报 / 导出 PDF</span>
            </button>
          </div>

          <button
            @click="close"
            class="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-all shadow-md active:scale-95"
          >
            确认并关闭
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  report: {
    type: Object,
    default: () => ({}),
  },
  theme: {
    type: String,
    default: 'dark',
  },
})

const emit = defineEmits(['update:modelValue', 'inspectTicket', 'inspectDevice'])

const copied = ref(false)

const reportData = computed(() => props.report || {})
const healthScore = computed(() => reportData.value.health_score ?? 85)
const kpi = computed(() => reportData.value.kpi || {})
const abnormalDevices = computed(() => reportData.value.abnormal_devices || [])
const citedRegulations = computed(() => reportData.value.cited_regulations || [])

// 环形进度仪表计算
const r = 40
const circumference = 2 * Math.PI * r // ~251.32
const meterDashOffset = computed(() => {
  const score = Math.max(0, Math.min(100, healthScore.value))
  const progress = score / 100
  return circumference * (1 - progress)
})

const meterStrokeColor = computed(() => {
  if (healthScore.value >= 90) return 'stroke-emerald-500'
  if (healthScore.value >= 75) return 'stroke-blue-500'
  if (healthScore.value >= 60) return 'stroke-amber-500'
  return 'stroke-rose-500'
})

const meterTextColor = computed(() => {
  if (props.theme === 'light') {
    if (healthScore.value >= 90) return 'text-emerald-700'
    if (healthScore.value >= 75) return 'text-blue-700'
    if (healthScore.value >= 60) return 'text-amber-700'
    return 'text-rose-700'
  }
  if (healthScore.value >= 90) return 'text-emerald-400'
  if (healthScore.value >= 75) return 'text-blue-400'
  if (healthScore.value >= 60) return 'text-amber-400'
  return 'text-rose-400'
})

const iconBadgeClass = computed(() => {
  if (props.theme === 'light') {
    if (healthScore.value >= 90) return 'bg-emerald-100 border-emerald-300 text-emerald-700'
    if (healthScore.value >= 75) return 'bg-blue-100 border-blue-300 text-blue-700'
    if (healthScore.value >= 60) return 'bg-amber-100 border-amber-300 text-amber-700'
    return 'bg-rose-100 border-rose-300 text-rose-700'
  }
  if (healthScore.value >= 90) return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
  if (healthScore.value >= 75) return 'bg-blue-500/10 border-blue-500/30 text-blue-400'
  if (healthScore.value >= 60) return 'bg-amber-500/10 border-amber-500/30 text-amber-400'
  return 'bg-rose-500/10 border-rose-500/30 text-rose-400'
})

const postureBadgeClass = computed(() => {
  if (props.theme === 'light') {
    if (healthScore.value >= 90) return 'bg-emerald-50 border-emerald-300 text-emerald-700'
    if (healthScore.value >= 75) return 'bg-blue-50 border-blue-300 text-blue-700'
    if (healthScore.value >= 60) return 'bg-amber-50 border-amber-300 text-amber-700'
    return 'bg-rose-50 border-rose-300 text-rose-700'
  }
  if (healthScore.value >= 90) return 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
  if (healthScore.value >= 75) return 'bg-blue-500/15 border-blue-500/30 text-blue-400'
  if (healthScore.value >= 60) return 'bg-amber-500/15 border-amber-500/30 text-amber-400'
  return 'bg-rose-500/15 border-rose-500/30 text-rose-400'
})

function close() {
  emit('update:modelValue', false)
}

function jumpToTicket(ticketNo) {
  emit('update:modelValue', false)
  emit('inspectTicket', ticketNo)
}

async function copyMarkdownReport() {
  const md = reportData.value.markdown_report || ''
  if (!md) return

  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(md)
      copied.value = true
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = md
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      copied.value = true
    }
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('复制报告失败:', err)
  }
}

/**
 * 专为 A4 纸张排版打印构建纯正的“明亮版”官方研判简报 HTML 文档
 * 无论当前界面处于暗黑还是明亮主题，打印出来的永远是统一、标准、融洽的白底彩色高校专业简报
 */
function buildLightPrintDocument(report, kpiData, score, abnormalList, regList) {
  let postureBg = '#ecfdf5'
  let postureBorder = '#a7f3d0'
  let postureColor = '#047857'
  let ringStroke = '#10b981'

  if (score >= 90) {
    postureBg = '#ecfdf5'
    postureBorder = '#a7f3d0'
    postureColor = '#047857'
    ringStroke = '#10b981'
  } else if (score >= 75) {
    postureBg = '#eff6ff'
    postureBorder = '#bfdbfe'
    postureColor = '#1d4ed8'
    ringStroke = '#3b82f6'
  } else if (score >= 60) {
    postureBg = '#fffbeb'
    postureBorder = '#fde68a'
    postureColor = '#b45309'
    ringStroke = '#f59e0b'
  } else {
    postureBg = '#fef2f2'
    postureBorder = '#fecaca'
    postureColor = '#b91c1c'
    ringStroke = '#ef4444'
  }

  const radius = 40
  const circ = 2 * Math.PI * radius
  const boundedScore = Math.max(0, Math.min(100, score))
  const dashOffset = circ * (1 - boundedScore / 100)

  // 渲染异常设备清单
  let abnormalHtml = ''
  if (!abnormalList || abnormalList.length === 0) {
    abnormalHtml = `
      <div style="padding: 20px; text-align: center; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; color: #065f46;">
        <div style="font-size: 16px; font-weight: bold; margin-bottom: 4px;">🎉 全机房在册设备运行良好，未检测到超温或脱网隐患</div>
        <div style="font-size: 11px; color: #047857;">全部节点温度均处于 40℃ 安全阈值内，动力负荷与网络通信通畅。</div>
      </div>
    `
  } else {
    abnormalHtml = abnormalList.map((dev) => {
      let cardBg = '#fffbeb'
      let cardBorder = '#fde68a'
      let badgeStyle = 'background: #fef3c7; color: #92400e; border: 1px solid #fcd34d;'
      let badgeText = '亚健康预警'
      let tempStyle = 'color: #b45309; font-weight: bold;'

      if (dev.is_overheat) {
        cardBg = '#fef2f2'
        cardBorder = '#fecaca'
        badgeStyle = 'background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;'
        badgeText = '超温红线告警'
        tempStyle = 'color: #dc2626; font-weight: bold;'
      } else if (dev.is_offline) {
        cardBg = '#f8fafc'
        cardBorder = '#e2e8f0'
        badgeStyle = 'background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1;'
        badgeText = '脱网离线'
        tempStyle = 'color: #64748b; font-weight: bold;'
      }

      let ticketBadge = ''
      if (dev.ticket_no) {
        const actionLabel = dev.ticket_action === 'CREATED' ? '🆕 自动建单' : '🔄 跟踪工单'
        ticketBadge = `
          <div style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; background: #e0e7ff; border: 1px solid #c7d2fe; border-radius: 6px; font-size: 11px; font-family: monospace; color: #3730a3; font-weight: 600;">
            <span>${actionLabel}</span>
            <span>工单: ${dev.ticket_no}</span>
          </div>
        `
      } else {
        ticketBadge = `<span style="padding: 2px 6px; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 10px; color: #64748b;">例行监控</span>`
      }

      return `
        <div style="background: ${cardBg}; border: 1px solid ${cardBorder}; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; page-break-inside: avoid;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-family: monospace; font-size: 13px; font-weight: 700; color: #0f172a;">${dev.asset_no}</span>
              <span style="font-size: 12px; color: #475569;">(${dev.name || '核心节点'})</span>
              <span style="padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; ${badgeStyle}">${badgeText}</span>
            </div>
            ${ticketBadge}
          </div>
          <div style="display: flex; gap: 14px; font-size: 11px; font-family: monospace; color: #334155; margin-bottom: 4px;">
            <span>位置: <strong>${dev.location || '实训楼机房'}</strong></span>
            <span>温度: <strong style="${tempStyle}">${dev.temperature || 0}℃</strong></span>
            <span>CPU: <strong>${dev.cpu_usage || 0}%</strong></span>
            <span>功耗: <strong>${dev.power_watts || 0}W</strong></span>
          </div>
          <div style="font-size: 11px; color: #1e293b; line-height: 1.4;">
            ${dev.alert_message || '检测到传感器遥测指标偏离预置健康基准。'}
          </div>
        </div>
      `
    }).join('')
  }

  // 渲染 RAG 条例
  let regulationsHtml = ''
  if (regList && regList.length > 0) {
    regulationsHtml = `
      <div style="margin-top: 14px; page-break-inside: avoid;">
        <div style="font-size: 12px; font-weight: 700; color: #1e293b; margin-bottom: 6px; display: flex; align-items: center; gap: 4px;">
          <span>📘 RAG 安全规程依据与研判条款</span>
        </div>
        ${regList.map((reg) => `
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 11px;">
            <div style="color: #4338ca; font-weight: 600; margin-bottom: 2px;">
              《${reg.doc_name}》 ${reg.clause ? `<span style="color: #64748b; font-size: 10px; font-family: monospace;">[${reg.clause}]</span>` : ''}
            </div>
            <div style="color: #475569; font-style: italic; line-height: 1.4;">“${reg.content}”</div>
          </div>
        `).join('')}
      </div>
    `
  }

  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>高校实验室 IT 基础设施运行健康研判简报 - ${report.batch_no || ''}</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 12mm 15mm;
    }
    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
      color-adjust: exact !important;
    }
    body {
      background: #ffffff !important;
      color: #0f172a !important;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0;
      padding: 0;
      font-size: 12px;
      line-height: 1.5;
    }
    .header-box {
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 10px;
      margin-bottom: 12px;
    }
    .title-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .main-title {
      font-size: 17px;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.2px;
      margin: 0;
    }
    .posture-pill {
      padding: 3px 10px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 700;
      font-family: monospace;
      white-space: nowrap;
      background: ${postureBg};
      border: 1px solid ${postureBorder};
      color: ${postureColor};
    }
    .meta-row {
      display: flex;
      gap: 16px;
      color: #64748b;
      font-size: 10px;
      font-family: monospace;
      margin-top: 5px;
    }
    .dashboard-grid {
      display: grid;
      grid-template-columns: 2fr 3.5fr;
      gap: 10px;
      margin-bottom: 12px;
    }
    .gauge-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
    }
    .kpi-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .kpi-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .kpi-title {
      font-size: 10px;
      color: #64748b;
      display: flex;
      justify-content: space-between;
    }
    .kpi-val {
      font-size: 18px;
      font-weight: 800;
      font-family: monospace;
      margin: 2px 0;
      color: #0f172a;
    }
    .kpi-foot {
      font-size: 9px;
      color: #64748b;
      font-family: monospace;
      border-top: 1px solid #e2e8f0;
      padding-top: 3px;
      display: flex;
      justify-content: space-between;
    }
    .summary-card {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 12px;
      color: #1e3a8a;
      font-size: 11px;
      line-height: 1.5;
    }
    .section-head {
      font-size: 12px;
      font-weight: 700;
      color: #0f172a;
      margin: 12px 0 8px 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .footer-note {
      margin-top: 20px;
      padding-top: 10px;
      border-top: 1px dashed #cbd5e1;
      display: flex;
      justify-content: space-between;
      color: #94a3b8;
      font-size: 9px;
      font-family: monospace;
    }
  </style>
</head>
<body>
  <div>
    <!-- 头部 Header -->
    <div class="header-box">
      <div class="title-row">
        <h1 class="main-title">高校实验室 IT 基础设施运行健康研判简报</h1>
        <span class="posture-pill">${report.posture_text || '态势平稳'}</span>
      </div>
      <div class="meta-row">
        <span>巡检批次: <strong>${report.batch_no || 'PTR-实时巡检'}</strong></span>
        <span>执行架构: <strong>${report.operator || '系统自治巡检'}</strong></span>
        <span>研判时间: <strong>${report.patrol_time || ''}</strong></span>
      </div>
    </div>

    <!-- 态势仪表与四大 KPI -->
    <div class="dashboard-grid">
      <div class="gauge-card">
        <div style="font-size: 10px; font-weight: 600; color: #64748b; margin-bottom: 4px;">机房综合健康态势指数</div>
        <div style="position: relative; width: 95px; height: 95px; margin: 2px auto;">
          <svg style="width: 100%; height: 100%; transform: rotate(-90deg);" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" stroke="#e2e8f0" stroke-width="8" fill="none" />
            <circle cx="50" cy="50" r="40" stroke="${ringStroke}" stroke-width="8" stroke-linecap="round" fill="none"
              stroke-dasharray="${circ}" stroke-dashoffset="${dashOffset}" />
          </svg>
          <div style="position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <span style="font-size: 26px; font-weight: 900; font-family: monospace; color: ${postureColor}; line-height: 1;">${score}</span>
            <span style="font-size: 9px; color: #64748b; font-family: monospace;">/ 100 分</span>
          </div>
        </div>
        <div style="font-size: 11px; font-weight: 700; color: ${postureColor}; margin-top: 2px;">
          ${report.posture_text || '态势平稳'}
        </div>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title"><span>受检资产全景</span><span>🖥️</span></div>
          <div class="kpi-val">${kpiData.total_scanned || 0} <span style="font-size: 11px; font-weight: normal; color: #64748b;">台</span></div>
          <div class="kpi-foot">
            <span style="color: #059669; font-weight: 600;">正常: ${kpiData.healthy_count || 0}</span>
            <span style="color: ${kpiData.overheat_count > 0 ? '#dc2626' : '#64748b'}; font-weight: 600;">超温: ${kpiData.overheat_count || 0}</span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title"><span>微环境均温</span><span>🌡️</span></div>
          <div class="kpi-val" style="color: ${kpiData.avg_temperature >= 40 ? '#dc2626' : kpiData.avg_temperature >= 38 ? '#d97706' : '#0f172a'};">
            ${kpiData.avg_temperature || 25.0} <span style="font-size: 11px; font-weight: normal; color: #64748b;">℃</span>
          </div>
          <div class="kpi-foot">
            <span>安全阈值: 40℃</span>
            <span style="color: ${kpiData.avg_temperature < 40 ? '#059669' : '#dc2626'}; font-weight: 600;">
              ${kpiData.avg_temperature < 40 ? '正常受控' : '超出红线'}
            </span>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title"><span>算力集群均载</span><span>⚡</span></div>
          <div class="kpi-val" style="color: #0e7490;">${kpiData.avg_cpu_load || 0} <span style="font-size: 11px; font-weight: normal; color: #64748b;">%</span></div>
          <div class="kpi-foot"><span>工况: 动态均衡</span><span>算力平稳</span></div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title"><span>实时供电负荷</span><span>🔌</span></div>
          <div class="kpi-val" style="color: #4338ca;">${kpiData.total_power_watts || 0} <span style="font-size: 11px; font-weight: normal; color: #64748b;">W</span></div>
          <div class="kpi-foot"><span>PDU 负荷率: ${Math.round(((kpiData.total_power_watts || 0) / 4500) * 100)}%</span><span>额定: 4500W</span></div>
        </div>
      </div>
    </div>

    <!-- 研判结论与概况 -->
    <div class="summary-card">
      <div style="font-weight: 700; color: #1e40af; margin-bottom: 3px;">📌 研判结论与自主处置概况</div>
      <div>${report.summary_text || '机房基础设施主动巡检完成，各项遥测参数符合安全管理要求。'}</div>
    </div>

    <!-- 异常台账 -->
    <div class="section-head">
      <span>⚠️ 隐患异常设备台账 (${abnormalList.length} 处)</span>
      <span style="font-size: 10px; font-weight: normal; color: #64748b;">系统已按条例完成自动调度闭环</span>
    </div>
    ${abnormalHtml}

    <!-- RAG 条例 -->
    ${regulationsHtml}

    <!-- 页脚标注 -->
    <div class="footer-note">
      <span>高校实验室轻量化智能自治运维系统 (LabOps-Agent) · 运行健康研判归档件</span>
      <span>打印导出时间: ${new Date().toLocaleString()}</span>
    </div>
  </div>
</body>
</html>
  `
}

function printReport() {
  // 1. 创建独立沙箱 iframe 进行纯净打印
  const printFrame = document.createElement('iframe')
  printFrame.setAttribute(
    'style',
    'position:fixed;top:0;left:0;width:1px;height:1px;border:none;opacity:0.01;pointer-events:none;z-index:-9999;'
  )
  document.body.appendChild(printFrame)

  const frameDoc = printFrame.contentWindow?.document
  if (!frameDoc) {
    window.print()
    return
  }

  // 2. 直接根据巡检数据，生成纯正、融洽的白底彩色“明亮版”标准打印 HTML 文档
  const lightHtml = buildLightPrintDocument(
    reportData.value,
    kpi.value,
    healthScore.value,
    abnormalDevices.value,
    citedRegulations.value
  )

  frameDoc.open()
  frameDoc.write(lightHtml)
  frameDoc.close()

  // 3. 确保 iframe 渲染完毕后唤起打印
  setTimeout(() => {
    try {
      printFrame.contentWindow.focus()
      printFrame.contentWindow.print()
    } catch (err) {
      console.error('iframe 打印触发失败，回退到主窗口打印:', err)
      window.print()
    } finally {
      setTimeout(() => {
        if (printFrame && printFrame.parentNode) {
          printFrame.parentNode.removeChild(printFrame)
        }
      }, 2500)
    }
  }, 250)
}
</script>

<!-- 全局打印兜底样式：若用户在当前窗口直接按下键盘 Ctrl + P，亦能以白底深字优雅输出 -->
<style>
@media print {
  html, body {
    height: auto !important;
    overflow: visible !important;
    background: #ffffff !important;
    color: #0f172a !important;
  }
  #app {
    height: auto !important;
    overflow: visible !important;
  }
  #app > div > header,
  #app > div > div.flex-1 {
    display: none !important;
  }
  .fixed.inset-0.z-50 {
    position: static !important;
    overflow: visible !important;
    background: transparent !important;
    padding: 0 !important;
    height: auto !important;
  }
  #printable-patrol-report {
    position: static !important;
    max-height: none !important;
    overflow: visible !important;
    box-shadow: none !important;
    border: none !important;
    background: #ffffff !important;
    color: #0f172a !important;
    width: 100% !important;
    height: auto !important;
    padding: 0 !important;
  }
  #printable-patrol-report .overflow-y-auto {
    overflow: visible !important;
    max-height: none !important;
    height: auto !important;
  }
  #printable-patrol-report button,
  .print\:hidden {
    display: none !important;
  }
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }
}
</style>
