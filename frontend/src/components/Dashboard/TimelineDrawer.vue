<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <!-- 全屏高斯模糊与暗黑遮罩 -->
      <div
        v-if="modelValue"
        @keydown.esc.window="close"
        class="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm overflow-hidden select-none"
        v-backdrop-dismiss="close"
      >
        <!-- 右侧滑出抽屉面板 (Timeline Drawer) -->
        <Transition
          enter-active-class="transform transition duration-300 ease-out"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transform transition duration-200 ease-in"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full"
        >
          <div
            v-if="modelValue"
            class="timeline-drawer-panel w-full max-w-xl sm:max-w-2xl h-full border-l p-5 sm:p-6 space-y-4 flex flex-col backdrop-blur-2xl overflow-hidden select-text font-sans relative transition-all"
            :class="[
              effectiveTheme === 'light'
                ? 'bg-white/95 border-slate-200 shadow-[-20px_0_50px_rgba(0,0,0,0.15)] text-slate-800'
                : 'bg-zinc-950/95 border-white/[0.12] shadow-[-20px_0_50px_rgba(0,0,0,0.8)] text-zinc-200'
            ]"
          >
            <!-- 头部栏：标题、模式标识与关闭按钮 -->
            <div
              class="flex items-center justify-between pb-3.5 border-b shrink-0"
              :class="effectiveTheme === 'light' ? 'border-slate-200' : 'border-white/[0.08]'"
            >
              <div class="flex items-center space-x-2.5">
                <span
                  class="p-2 rounded-xl border shadow-sm"
                  :class="mode === 'ticket' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'"
                >
                  <!-- 工单流转图标 -->
                  <svg v-if="mode === 'ticket'" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <!-- 资产履历图标 -->
                  <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </span>
                <div>
                  <h3
                    class="text-sm sm:text-base font-semibold tracking-tight flex items-center gap-2"
                    :class="effectiveTheme === 'light' ? 'text-slate-900' : 'text-zinc-100'"
                  >
                    <span>{{ mode === 'ticket' ? '运维工单流转全景脉络' : '资产全生命周期时序履历' }}</span>
                    <span
                      class="text-[10px] px-2 py-0.5 rounded font-mono border"
                      :class="effectiveTheme === 'light' ? 'bg-slate-100 text-slate-600 border-slate-200' : 'bg-zinc-900/80 text-zinc-400 border-white/[0.08]'"
                    >
                      {{ mode === 'ticket' ? 'Audit Trail' : 'Lifecycle' }}
                    </span>
                  </h3>
                  <p
                    class="text-[11px] mt-0.5"
                    :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                  >
                    {{ mode === 'ticket' ? '全程防抵赖留痕：系统感知、多级流转处置与耗时分析' : '一机一档全时序追溯：采购投产、借调流转与巡检维保' }}
                  </p>
                </div>
              </div>

              <!-- 右侧控制区 -->
              <div class="flex items-center space-x-1.5">
                <button
                  @click="fetchTimelineData"
                  class="p-1.5 rounded-lg transition-colors"
                  :class="effectiveTheme === 'light' ? 'hover:bg-slate-100 text-slate-500 hover:text-slate-800' : 'hover:bg-white/[0.08] text-zinc-400 hover:text-zinc-200'"
                  title="刷新时间轴"
                >
                  <svg class="w-4 h-4" :class="loading ? 'animate-spin' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button
                  @click="close"
                  class="p-1.5 rounded-lg transition-colors"
                  :class="effectiveTheme === 'light' ? 'hover:bg-slate-100 text-slate-500 hover:text-slate-800' : 'hover:bg-white/[0.08] text-zinc-400 hover:text-zinc-100'"
                  title="关闭抽屉 (Esc)"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- 实体元数据概览卡片 -->
            <div
              v-if="ticketData || assetData"
              class="p-3.5 rounded-2xl border space-y-2 shrink-0 shadow-sm"
              :class="effectiveTheme === 'light' ? 'bg-slate-50 border-slate-200' : 'bg-black/35 border-white/[0.06]'"
            >
              <!-- 工单模式元数据 -->
              <div v-if="mode === 'ticket' && ticketData" class="space-y-1.5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <span class="font-mono text-xs font-semibold text-amber-500 select-all">{{ ticketData.ticket_no }}</span>
                    <span :class="['px-2 py-0.5 rounded text-[10px] font-mono', priorityClass(ticketData.priority)]">
                      {{ ticketData.priority }}
                    </span>
                    <span :class="['px-2 py-0.5 rounded text-[10px] font-mono', statusClass(ticketData.status)]">
                      {{ statusLabel(ticketData.status) }}
                    </span>
                  </div>
                  <div
                    class="text-[10px] font-mono flex items-center space-x-1.5"
                    :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                  >
                    <span>提单人:</span>
                    <button
                      @click="openUserProfile(ticketData.creator || '系统', { title: '工单创建 - ' + ticketData.title, comment: ticketData.description, timestamp: ticketData.created_at, duration_from_start: '+0分钟' })"
                      type="button"
                      class="underline decoration-dashed transition-colors font-sans"
                      :class="effectiveTheme === 'light' ? 'text-indigo-600 hover:text-indigo-800 decoration-slate-400 hover:decoration-indigo-600' : 'text-zinc-200 hover:text-white decoration-zinc-500 hover:decoration-indigo-400'"
                      :title="`查看提单人 [${ticketData.creator}] 档案`"
                    >
                      {{ ticketData.creator }}
                    </button>
                  </div>
                </div>
                <div
                  class="text-xs font-medium truncate"
                  :class="effectiveTheme === 'light' ? 'text-slate-800' : 'text-zinc-200'"
                  :title="ticketData.title"
                >
                  {{ ticketData.title }}
                </div>
                <div
                  class="flex items-center justify-between text-[11px] font-mono pt-0.5 border-t"
                  :class="effectiveTheme === 'light' ? 'border-slate-200 text-slate-500' : 'border-white/[0.04] text-zinc-400'"
                >
                  <div>关联设备: <span class="text-cyan-500 font-medium select-all">{{ ticketData.device_id || '无关联设备' }}</span></div>
                  <div>创建时间: <span>{{ ticketData.created_at || '-' }}</span></div>
                </div>
              </div>

              <!-- 资产模式元数据 -->
              <div v-else-if="mode === 'asset' && assetData" class="space-y-1.5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <span class="font-mono text-xs font-semibold text-cyan-500 select-all">{{ assetData.asset_no }}</span>
                    <span
                      class="text-[10px] px-2 py-0.5 rounded font-medium border"
                      :class="effectiveTheme === 'light' ? 'bg-slate-200/80 text-slate-700 border-slate-300' : 'bg-zinc-800 text-zinc-300 border-white/[0.06]'"
                    >
                      {{ assetData.category }}
                    </span>
                    <span :class="['px-2 py-0.5 rounded text-[10px] font-mono', healthClass(assetData.health_status)]">
                      {{ assetData.health_status }}
                    </span>
                    <span :class="['px-2 py-0.5 rounded text-[10px] font-mono', borrowClass(assetData.borrow_status)]">
                      {{ assetData.borrow_status === 'AVAILABLE' ? '空闲可用' : assetData.borrow_status === 'IN_USE' ? '借调在用' : '检修维护' }}
                    </span>
                  </div>
                  <div
                    class="text-[10px] font-mono flex items-center space-x-1"
                    :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                  >
                    <span>借用人:</span>
                    <button
                      v-if="assetData.borrower && assetData.borrower !== '暂无'"
                      @click="openUserProfile(assetData.borrower, { title: '设备借用 - ' + assetData.name, comment: '当前借用人/使用主体: ' + assetData.borrower, timestamp: assetData.detail?.purchase_date || '', duration_from_start: '' })"
                      type="button"
                      class="underline decoration-dashed transition-colors font-sans"
                      :class="effectiveTheme === 'light' ? 'text-amber-700 hover:text-amber-900 decoration-amber-400' : 'text-amber-300 hover:text-amber-200 decoration-amber-500/50 hover:decoration-amber-400'"
                      :title="`查看借用人 [${assetData.borrower}] 档案`"
                    >
                      {{ assetData.borrower }}
                    </button>
                    <span v-else :class="effectiveTheme === 'light' ? 'text-slate-400' : 'text-zinc-500'">暂无</span>
                  </div>
                </div>
                <div
                  class="text-xs font-medium truncate"
                  :class="effectiveTheme === 'light' ? 'text-slate-800' : 'text-zinc-200'"
                  :title="assetData.name"
                >
                  {{ assetData.name }}
                </div>
                <div
                  class="flex items-center justify-between text-[11px] font-mono pt-0.5 border-t"
                  :class="effectiveTheme === 'light' ? 'border-slate-200 text-slate-500' : 'border-white/[0.04] text-zinc-400'"
                >
                  <div>机房机柜: <span :class="effectiveTheme === 'light' ? 'text-slate-700 font-medium' : 'text-zinc-300'">{{ assetData.location }}</span></div>
                  <div>投产采购: <span>{{ assetData.detail?.purchase_date || assetData.created_at || '未登记' }}</span></div>
                </div>
              </div>

              <!-- 统计胶囊条 -->
              <div
                class="flex items-center space-x-3 pt-1 text-[11px] font-mono"
                :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
              >
                <span class="flex items-center space-x-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                  <span>总计节点: <strong :class="effectiveTheme === 'light' ? 'text-slate-800' : 'text-zinc-200'">{{ timelineSummary?.total_nodes || timelineSummary?.total_events || timelineNodes.length }}</strong> 处</span>
                </span>
                <span v-if="mode === 'ticket'" class="flex items-center space-x-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                  <span>流转总耗时: <strong :class="effectiveTheme === 'light' ? 'text-amber-700' : 'text-amber-300'">{{ timelineSummary?.total_duration || '计算中' }}</strong></span>
                </span>
                <span v-else class="flex items-center space-x-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                  <span>借还次数: <strong :class="effectiveTheme === 'light' ? 'text-cyan-700' : 'text-cyan-300'">{{ timelineSummary?.total_borrows ?? 0 }}</strong> 次</span>
                  <span class="mx-1" :class="effectiveTheme === 'light' ? 'text-slate-300' : 'text-zinc-600'">|</span>
                  <span>运维工单: <strong :class="effectiveTheme === 'light' ? 'text-rose-700' : 'text-rose-300'">{{ timelineSummary?.total_tickets ?? 0 }}</strong> 起</span>
                </span>
              </div>
            </div>

            <!-- 中间核心区域：微光光纤导轨垂直时间轴 (可滚动) -->
            <div class="flex-1 overflow-y-auto pr-1 relative custom-scrollbar space-y-4">
              <!-- 加载中动画 -->
              <div v-if="loading" class="py-16 flex flex-col items-center justify-center space-y-3" :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'">
                <div class="w-7 h-7 border-2 border-indigo-500/30 border-t-indigo-400 rounded-full animate-spin"></div>
                <div class="text-xs font-mono">正在检索时序审计链与流转节点...</div>
              </div>

              <!-- 错误提示 -->
              <div v-else-if="error" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs space-y-2">
                <div class="font-semibold flex items-center space-x-1.5">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>获取时间轴流转数据失败</span>
                </div>
                <div>{{ error }}</div>
                <button
                  @click="fetchTimelineData"
                  class="px-3 py-1 rounded-md bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-[11px] transition-colors"
                >
                  重新加载
                </button>
              </div>

              <!-- 空状态 -->
              <div v-else-if="timelineNodes.length === 0" class="py-16 text-center text-xs font-mono" :class="effectiveTheme === 'light' ? 'text-slate-400' : 'text-zinc-500'">
                暂未检索到该实体的流转时序节点
              </div>

              <!-- 时间轴节点流 -->
              <div v-else class="relative pl-10 py-2">
                <!-- 垂直发光导轨 (Luminous Rail) -->
                <div
                  class="absolute left-[27px] top-4 bottom-4 w-[2px]"
                  :class="effectiveTheme === 'light'
                    ? 'bg-gradient-to-b from-indigo-400 via-sky-400 to-indigo-300/50 shadow-[0_0_6px_rgba(99,102,241,0.25)]'
                    : 'bg-gradient-to-b from-indigo-500/60 via-cyan-500/40 to-indigo-500/20 shadow-[0_0_8px_rgba(99,102,241,0.4)]'"
                ></div>

                <div class="space-y-4">
                  <div
                    v-for="(node, idx) in timelineNodes"
                    :key="node.id || idx"
                    class="relative group"
                  >
                    <!-- 发光呼吸节点图标 (左侧留足 14px 扩散空间，消除阴影切边) -->
                    <div
                      class="absolute -left-[26px] top-2.5 w-7 h-7 rounded-full flex items-center justify-center border shadow-sm transition-all duration-300 z-10 group-hover:scale-110"
                      :class="nodeIconStyle(node.node_type)"
                    >
                      <!-- 节点内部专属简明图标 -->
                      <component :is="getNodeIcon(node.node_type)" class="w-3.5 h-3.5" />
                    </div>

                    <!-- 磨砂玻璃节点卡片 -->
                    <div
                      class="ml-4 p-3.5 rounded-2xl border transition-all duration-200 space-y-2 shadow-sm"
                      :class="[
                        effectiveTheme === 'light'
                          ? 'bg-slate-50/90 border-slate-200 hover:border-slate-300 shadow-slate-200/50'
                          : 'bg-black/25 border-white/[0.07] hover:border-white/[0.18]'
                      ]"
                    >
                      <!-- 节点头部：标题与相对耗时 -->
                      <div class="flex items-start justify-between gap-2">
                        <div class="space-y-0.5 min-w-0">
                          <div class="flex items-center space-x-2 flex-wrap">
                            <span
                              class="font-medium text-xs"
                              :class="effectiveTheme === 'light' ? 'text-slate-900' : 'text-zinc-100'"
                            >{{ node.title }}</span>
                            <span
                              class="px-1.5 py-0.5 rounded text-[9px] font-mono border uppercase"
                              :class="nodeTypeTagStyle(node.node_type)"
                            >
                              {{ nodeTypeLabel(node.node_type) }}
                            </span>
                          </div>
                        </div>

                        <!-- 相对耗时胶囊 -->
                        <span
                          v-if="node.duration_from_start"
                          class="px-2 py-0.5 rounded-full text-[10px] font-mono shrink-0 shadow-sm border"
                          :class="effectiveTheme === 'light' ? 'bg-slate-100 text-slate-600 border-slate-200' : 'bg-zinc-900/90 text-zinc-400 border-white/[0.08]'"
                          title="相对提单/投产起点的时序位移"
                        >
                          {{ node.duration_from_start }}
                        </span>
                      </div>

                      <!-- 操作人与绝对发生时间 -->
                      <div
                        class="flex items-center space-x-3 text-[11px] flex-wrap gap-y-1"
                        :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                      >
                        <div class="flex items-center space-x-1.5 font-mono">
                          <button
                            @click="openUserProfile(node.operator || '系统', node)"
                            type="button"
                            class="group/op inline-flex items-center space-x-1 px-2 py-0.5 rounded-lg border font-mono text-[11px] transition-all duration-200 active:scale-95 shadow-sm select-none"
                            :class="[
                              isSystemAgent(node.operator)
                                ? (effectiveTheme === 'light'
                                    ? 'bg-cyan-50 hover:bg-cyan-100 text-cyan-700 border-cyan-300 shadow-cyan-500/5'
                                    : 'bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border-cyan-500/30 hover:border-cyan-400/60 shadow-cyan-500/10')
                                : (effectiveTheme === 'light'
                                    ? 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-300 shadow-indigo-500/5'
                                    : 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-200 border-indigo-500/30 hover:border-indigo-400/60 shadow-indigo-500/10')
                            ]"
                            :title="`点击查阅 [${node.operator || '系统'}] 的人物/主体档案与处置权责`"
                          >
                            <svg v-if="isSystemAgent(node.operator)" class="w-3 h-3 text-cyan-500 shrink-0 group-hover/op:rotate-12 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            <svg v-else class="w-3 h-3 text-indigo-500 shrink-0 group-hover/op:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            <span
                              class="font-sans font-medium"
                              :class="effectiveTheme === 'light' ? 'text-slate-800 group-hover/op:text-slate-950' : 'text-zinc-100 group-hover/op:text-white'"
                            >{{ node.operator || '系统' }}</span>
                            <span
                              class="text-[9px] opacity-70 group-hover/op:opacity-100 group-hover/op:translate-x-0.5 group-hover/op:-translate-y-0.5 transition-all"
                              :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                            >↗</span>
                          </button>
                        </div>
                        <span :class="effectiveTheme === 'light' ? 'text-slate-300' : 'text-zinc-600'">|</span>
                        <div
                          class="font-mono text-[10px] flex items-center space-x-1"
                          :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                        >
                          <svg class="w-3 h-3 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span>{{ node.timestamp }}</span>
                        </div>
                      </div>

                      <!-- 状态变迁演化胶囊 (PREV -> NEXT) -->
                      <div
                        v-if="node.previous_status && node.next_status"
                        class="flex items-center space-x-2 text-[10px] font-mono pt-1"
                      >
                        <span :class="['px-2 py-0.5 rounded border font-medium', statusClass(node.previous_status)]">
                          {{ statusLabel(node.previous_status) }}
                        </span>
                        <svg class="w-3 h-3 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                        <span :class="['px-2 py-0.5 rounded border font-medium', statusClass(node.next_status)]">
                          {{ statusLabel(node.next_status) }}
                        </span>
                      </div>

                      <!-- 处置说明或内容详情 -->
                      <div
                        v-if="node.comment"
                        class="p-2.5 rounded-xl border text-xs leading-relaxed font-sans whitespace-pre-line"
                        :class="effectiveTheme === 'light' ? 'bg-white border-slate-200 text-slate-700' : 'bg-black/30 border-white/[0.04] text-zinc-300'"
                      >
                        {{ node.comment }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 底部操作栏：仅当工单未闭环且为工单模式时展示快捷流转推进区 -->
            <div
              v-if="mode === 'ticket' && ticketData && ticketData.status !== 'CLOSED'"
              class="pt-3 border-t space-y-2.5 shrink-0"
              :class="effectiveTheme === 'light' ? 'border-slate-200' : 'border-white/[0.08]'"
            >
              <div
                class="text-[11px] flex items-center justify-between"
                :class="effectiveTheme === 'light' ? 'text-slate-600' : 'text-zinc-400'"
              >
                <span
                  class="font-medium flex items-center space-x-1"
                  :class="effectiveTheme === 'light' ? 'text-slate-800' : 'text-zinc-300'"
                >
                  <svg class="w-3.5 h-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>工单快速流转处置</span>
                </span>
                <span v-if="isStudent" :class="effectiveTheme === 'light' ? 'text-slate-400' : 'text-zinc-500'" class="font-mono text-[10px]">学生账号仅具查阅权限</span>
              </div>

              <!-- 快捷处置说明输入 -->
              <input
                v-if="!isStudent"
                v-model="quickComment"
                @keydown.enter.prevent="handleQuickEnter"
                type="text"
                placeholder="填写流转处置说明（可选，按回车或右下角按钮提交）..."
                class="w-full rounded-xl px-3 py-1.5 text-xs placeholder-zinc-500 focus:outline-none transition-colors font-sans border"
                :class="[
                  effectiveTheme === 'light'
                    ? 'bg-slate-50 border-slate-200 text-slate-800 focus:border-indigo-500 focus:bg-white'
                    : 'bg-zinc-900/80 border-white/[0.08] text-zinc-200 focus:border-indigo-500/60'
                ]"
              />

              <!-- 操作失败非阻塞警告条 -->
              <div
                v-if="actionError"
                class="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-mono"
              >
                {{ actionError }}
              </div>

              <!-- 状态推进按钮组 -->
              <div class="flex items-center justify-end space-x-2">
                <!-- 待处理工单：受理 -->
                <button
                  v-if="ticketData.status === 'PENDING'"
                  :disabled="isStudent || submitting"
                  @click="submitQuickStatus('PROCESSING')"
                  class="px-3.5 py-1.5 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 text-xs font-mono transition-all active:scale-95 shadow-sm disabled:opacity-50"
                >
                  {{ submitting ? '正在受理...' : '认领受理 (PROCESSING)' }}
                </button>

                <!-- 处理中工单：办结 -->
                <button
                  v-if="ticketData.status === 'PROCESSING'"
                  :disabled="isTeacher || isStudent || submitting"
                  @click="!isTeacher && submitQuickStatus('RESOLVED')"
                  :class="[
                    'px-3.5 py-1.5 rounded-xl text-xs font-mono transition-all border shadow-sm',
                    isTeacher
                      ? 'bg-zinc-800/50 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-60'
                      : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border-emerald-500/30 active:scale-95'
                  ]"
                  :title="isTeacher ? '需管理员核验后办结' : '办结此工单'"
                >
                  {{ submitting ? '处理中...' : '办结工单 (RESOLVED)' }}
                </button>

                <!-- 已解决工单：归档 -->
                <button
                  v-if="ticketData.status === 'RESOLVED'"
                  :disabled="isTeacher || isStudent || submitting"
                  @click="!isTeacher && submitQuickStatus('CLOSED')"
                  :class="[
                    'px-3.5 py-1.5 rounded-xl text-xs font-mono transition-all border shadow-sm',
                    isTeacher
                      ? (effectiveTheme === 'light' ? 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed' : 'bg-zinc-800/50 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-60')
                      : (effectiveTheme === 'light' ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300 active:scale-95' : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-white/[0.1] active:scale-95')
                  ]"
                  :title="isTeacher ? '需管理员核验后归档' : '归档关闭工单'"
                >
                  {{ submitting ? '处理中...' : '归档闭环 (CLOSED)' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>

    <!-- 人物与智能体专属档案弹窗 -->
    <UserProfileModal
      v-model="showUserProfileModal"
      :identifier="selectedProfileIdentifier"
      :nodeContext="selectedProfileNodeContext"
      :currentUser="currentUser"
      :theme="effectiveTheme"
      @userUpdated="handleUserUpdated"
    />
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, h } from 'vue'
import { api } from '../../api/client'
import UserProfileModal from '../Common/UserProfileModal.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  mode: {
    type: String,
    default: 'ticket', // 'ticket' | 'asset'
    validator: (v) => ['ticket', 'asset'].includes(v),
  },
  target: {
    type: [String, Number],
    default: '',
  },
  currentUser: {
    type: Object,
    default: () => ({ role: 'ADMIN', real_name: '王主管' }),
  },
  theme: {
    type: String,
    default: 'dark',
  },
})

const emit = defineEmits(['update:modelValue', 'ticketUpdated', 'userUpdated'])

const loading = ref(false)
const submitting = ref(false)
const error = ref('')
const actionError = ref('')
const ticketData = ref(null)
const assetData = ref(null)
const timelineNodes = ref([])
const timelineSummary = ref(null)
const quickComment = ref('')

// 主题动态感知 (支持 Light / Dark 双模态)
const effectiveTheme = computed(() => {
  if (props.theme) return props.theme
  return document.documentElement.classList.contains('light') ? 'light' : 'dark'
})

// 人物与智能体专属档案弹窗交互状态
const showUserProfileModal = ref(false)
const selectedProfileIdentifier = ref('')
const selectedProfileNodeContext = ref(null)

function isSystemAgent(op) {
  if (!op) return false
  const s = op.toLowerCase()
  return (
    s.includes('agent') ||
    s.includes('监控') ||
    s.includes('巡检') ||
    s.includes('系统')
  )
}

function openUserProfile(operatorName, node) {
  selectedProfileIdentifier.value = operatorName || '系统'
  selectedProfileNodeContext.value = node || null
  showUserProfileModal.value = true
}

function handleUserUpdated(updatedUser) {
  emit('userUpdated', updatedUser)
  emit('ticketUpdated')
}

const userRole = computed(() => (props.currentUser?.role || 'STUDENT').toUpperCase())
const isStudent = computed(() => userRole.value === 'STUDENT')
const isTeacher = computed(() => userRole.value === 'TEACHER')
const isAdmin = computed(() => userRole.value === 'ADMIN')

function onKeyDown(e) {
  if (e.key === 'Escape' && props.modelValue) {
    // 若上层人物档案详情弹窗正开启，优先消费 ESC 供其关闭，不连带关闭抽屉
    if (showUserProfileModal.value) {
      return
    }
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})

watch(
  () => [props.modelValue, props.target, props.mode],
  ([visible, newTarget]) => {
    if (visible && newTarget) {
      fetchTimelineData()
    }
  },
  { immediate: true }
)

async function fetchTimelineData() {
  if (!props.target) return
  loading.value = true
  error.value = ''
  quickComment.value = ''
  try {
    if (props.mode === 'ticket') {
      const res = await api.getTicketTimeline(props.target)
      ticketData.value = res.ticket
      assetData.value = null
      timelineNodes.value = res.timeline || []
      timelineSummary.value = res.summary
    } else {
      const res = await api.getAssetTimeline(props.target)
      assetData.value = res.asset
      ticketData.value = null
      timelineNodes.value = res.timeline || []
      timelineSummary.value = res.summary
    }
  } catch (err) {
    error.value = err.message || '加载时间轴数据失败'
  } finally {
    loading.value = false
  }
}

function handleQuickEnter() {
  if (!ticketData.value || submitting.value || isStudent.value) return
  if (ticketData.value.status === 'PENDING') {
    submitQuickStatus('PROCESSING')
  } else if (ticketData.value.status === 'PROCESSING' && !isTeacher.value) {
    submitQuickStatus('RESOLVED')
  } else if (ticketData.value.status === 'RESOLVED' && !isTeacher.value) {
    submitQuickStatus('CLOSED')
  }
}

async function submitQuickStatus(newStatus) {
  if (!ticketData.value || submitting.value) return
  submitting.value = true
  actionError.value = ''
  try {
    const operator = props.currentUser?.real_name || props.currentUser?.username || '系统管理员'
    await api.updateTicket(ticketData.value.id, {
      status: newStatus,
      operator,
      comment: quickComment.value.trim() || undefined,
    })
    quickComment.value = ''
    await fetchTimelineData()
    emit('ticketUpdated')
  } catch (err) {
    console.error('流转状态更新失败:', err)
    actionError.value = err.message || '流转状态更新失败'
    setTimeout(() => {
      actionError.value = ''
    }, 5000)
  } finally {
    submitting.value = false
  }
}

function close() {
  emit('update:modelValue', false)
}

function nodeIconStyle(type) {
  const isLight = effectiveTheme.value === 'light'
  if (isLight) {
    switch (type) {
      case 'CREATED':
      case 'COMMISSIONING':
        return 'bg-white border-2 border-cyan-500 text-cyan-600 shadow-[0_2px_10px_rgba(6,182,212,0.35)] ring-4 ring-cyan-100/60'
      case 'PROCESSING':
        return 'bg-white border-2 border-blue-500 text-blue-600 shadow-[0_2px_10px_rgba(59,130,246,0.35)] ring-4 ring-blue-100/60'
      case 'RESOLVED':
      case 'RETURN':
        return 'bg-white border-2 border-emerald-500 text-emerald-600 shadow-[0_2px_10px_rgba(16,185,129,0.35)] ring-4 ring-emerald-100/60'
      case 'CLOSED':
        return 'bg-white border-2 border-slate-400 text-slate-600 shadow-[0_2px_8px_rgba(100,116,139,0.2)] ring-4 ring-slate-100'
      case 'AUTOMATION':
      case 'BORROW':
        return 'bg-white border-2 border-amber-500 text-amber-600 shadow-[0_2px_10px_rgba(245,158,11,0.35)] ring-4 ring-amber-100/60'
      case 'INCIDENT':
        return 'bg-white border-2 border-rose-500 text-rose-600 shadow-[0_2px_10px_rgba(244,63,94,0.35)] ring-4 ring-rose-100/60'
      case 'MAINTENANCE':
        return 'bg-white border-2 border-indigo-500 text-indigo-600 shadow-[0_2px_10px_rgba(99,102,241,0.35)] ring-4 ring-indigo-100/60'
      default:
        return 'bg-white border-2 border-slate-300 text-slate-600 shadow-sm ring-4 ring-slate-100'
    }
  }

  // 暗黑极客模式保持深邃发光拟态
  switch (type) {
    case 'CREATED':
    case 'COMMISSIONING':
      return 'bg-cyan-950/80 border-cyan-400/60 text-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.5)]'
    case 'PROCESSING':
      return 'bg-blue-950/80 border-blue-400/60 text-blue-400 shadow-[0_0_12px_rgba(59,130,246,0.5)]'
    case 'RESOLVED':
    case 'RETURN':
      return 'bg-emerald-950/80 border-emerald-400/60 text-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.5)]'
    case 'CLOSED':
      return 'bg-zinc-900 border-zinc-500/60 text-zinc-300 shadow-[0_0_12px_rgba(161,161,170,0.3)]'
    case 'AUTOMATION':
    case 'BORROW':
      return 'bg-amber-950/80 border-amber-400/60 text-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.5)]'
    case 'INCIDENT':
      return 'bg-rose-950/80 border-rose-400/60 text-rose-400 shadow-[0_0_12px_rgba(244,63,94,0.5)]'
    case 'MAINTENANCE':
      return 'bg-indigo-950/80 border-indigo-400/60 text-indigo-400 shadow-[0_0_12px_rgba(99,102,241,0.5)]'
    default:
      return 'bg-zinc-900 border-zinc-600 text-zinc-400'
  }
}

function nodeTypeTagStyle(type) {
  const isLight = effectiveTheme.value === 'light'
  if (isLight) {
    switch (type) {
      case 'CREATED':
      case 'COMMISSIONING':
        return 'bg-cyan-50 text-cyan-700 border-cyan-200'
      case 'PROCESSING':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'RESOLVED':
      case 'RETURN':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200'
      case 'CLOSED':
        return 'bg-slate-100 text-slate-600 border-slate-200'
      case 'AUTOMATION':
      case 'BORROW':
        return 'bg-amber-50 text-amber-700 border-amber-200'
      case 'INCIDENT':
        return 'bg-rose-50 text-rose-700 border-rose-200'
      case 'MAINTENANCE':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200'
      default:
        return 'bg-slate-100 text-slate-600 border-slate-200'
    }
  }

  switch (type) {
    case 'CREATED':
    case 'COMMISSIONING':
      return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
    case 'PROCESSING':
      return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    case 'RESOLVED':
    case 'RETURN':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'CLOSED':
      return 'bg-zinc-800 text-zinc-400 border-white/[0.08]'
    case 'AUTOMATION':
    case 'BORROW':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'INCIDENT':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20'
    case 'MAINTENANCE':
      return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
    default:
      return 'bg-zinc-800 text-zinc-400 border-white/[0.08]'
  }
}

function nodeTypeLabel(type) {
  switch (type) {
    case 'CREATED':
      return '提单创建'
    case 'COMMISSIONING':
      return '采购投产'
    case 'PROCESSING':
      return '认领受理'
    case 'RESOLVED':
      return '排查完成'
    case 'CLOSED':
      return '办结归档'
    case 'AUTOMATION':
      return 'Agent 自动化'
    case 'BORROW':
      return '借调登记'
    case 'RETURN':
      return '验收入库'
    case 'INCIDENT':
      return '故障提单'
    case 'MAINTENANCE':
      return '维保流转'
    default:
      return type
  }
}

function getNodeIcon(type) {
  return {
    render() {
      if (type === 'CREATED' || type === 'COMMISSIONING') {
        return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
          h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '2', d: 'M12 4v16m8-8H4' }),
        ])
      }
      if (type === 'RESOLVED' || type === 'RETURN') {
        return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
          h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '2', d: 'M5 13l4 4L19 7' }),
        ])
      }
      if (type === 'CLOSED') {
        return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
          h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '2', d: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4' }),
        ])
      }
      if (type === 'AUTOMATION') {
        return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
          h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' }),
        ])
      }
      if (type === 'BORROW') {
        return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
          h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '2', d: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4' }),
        ])
      }
      if (type === 'INCIDENT') {
        return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
          h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '2', d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' }),
        ])
      }
      // default: arrow/flow
      return h('svg', { fill: 'none', viewBox: '0 0 24 24', stroke: 'currentColor' }, [
        h('path', { strokeLinecap: 'round', strokeLinejoin: 'round', strokeWidth: '2', d: 'M9 5l7 7-7 7' }),
      ])
    },
  }
}

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

function statusClass(status) {
  switch (status) {
    case 'PENDING':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'PROCESSING':
      return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    case 'RESOLVED':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'CLOSED':
      return 'bg-zinc-800 text-zinc-500 border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border-white/[0.06]'
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

function healthClass(status) {
  switch (status) {
    case 'HEALTHY':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'WARNING':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'OVERHEAT':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20 font-semibold animate-pulse'
    case 'OFFLINE':
      return 'bg-zinc-800 text-zinc-500 border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border-white/[0.06]'
  }
}

function borrowClass(status) {
  switch (status) {
    case 'AVAILABLE':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'IN_USE':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'MAINTENANCE':
      return 'bg-zinc-800 text-zinc-400 border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border-white/[0.06]'
  }
}
</script>

<style>
/* ========================================================
   明亮模式 (Light Mode) 专属高对比度与柔光阴影适配
   ======================================================== */
html.light .timeline-drawer-panel {
  background-color: rgba(255, 255, 255, 0.98) !important;
  border-left: 1px solid rgba(203, 213, 225, 0.9) !important;
  color: #0f172a !important;
  box-shadow: -15px 0 35px rgba(15, 23, 42, 0.12) !important;
}

html.light .timeline-drawer-panel .text-zinc-100 {
  color: #0f172a !important;
}

html.light .timeline-drawer-panel .text-zinc-200 {
  color: #1e293b !important;
}

html.light .timeline-drawer-panel .text-zinc-300 {
  color: #334155 !important;
}

html.light .timeline-drawer-panel .text-zinc-400 {
  color: #64748b !important;
}

html.light .timeline-drawer-panel .text-zinc-500 {
  color: #94a3b8 !important;
}

html.light .timeline-drawer-panel [class*="border-white"] {
  border-color: rgba(226, 232, 240, 0.9) !important;
}

html.light .timeline-drawer-panel [class*="bg-black/35"],
html.light .timeline-drawer-panel [class*="bg-black/25"],
html.light .timeline-drawer-panel [class*="bg-black/30"],
html.light .timeline-drawer-panel [class*="bg-black/20"] {
  background-color: rgba(248, 250, 252, 0.95) !important;
  border-color: rgba(226, 232, 240, 0.9) !important;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
}

html.light .timeline-drawer-panel .bg-zinc-900\/90,
html.light .timeline-drawer-panel .bg-zinc-900\/80,
html.light .timeline-drawer-panel .bg-zinc-900 {
  background-color: #f1f5f9 !important;
  border-color: rgba(203, 213, 225, 0.9) !important;
  color: #334155 !important;
}

html.light .timeline-drawer-panel input {
  background-color: #ffffff !important;
  border-color: rgba(203, 213, 225, 0.9) !important;
  color: #0f172a !important;
}
</style>
