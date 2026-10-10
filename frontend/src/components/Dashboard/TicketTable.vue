<template>
  <div class="rounded-xl glass-panel border p-4 space-y-3.5 shadow-sm transition-colors flex flex-col">
    <!-- 头部：标题 + 操作按钮 -->
    <div class="flex items-center justify-between gap-2.5 pb-2 border-b border-white/[0.06]">
      <div class="flex items-center space-x-2">
        <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-amber-400">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-medium text-zinc-100 glass-text">机房运维工单流转库</h3>
        <span class="px-2 py-0.5 rounded-md bg-zinc-900/80 border border-white/[0.08] text-zinc-400 text-[10px] font-mono">
          共 {{ filteredTickets.length }} 条记录
        </span>
      </div>

      <!-- 导出 / 打印 下拉菜单按钮 -->
      <div class="relative shrink-0" ref="exportMenuRef">
        <button
          @click="showExportMenu = !showExportMenu"
          class="px-2.5 py-1 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all shadow-sm active:scale-95 shrink-0 bg-zinc-900/90 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-white/[0.08] hover:border-white/[0.16]"
          title="导出当前筛选工单或调用纸质打印归档"
        >
          <svg class="w-3.5 h-3.5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span class="font-sans">导出 / 打印</span>
          <svg class="w-3 h-3 text-zinc-400 transition-transform duration-200" :class="showExportMenu ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- 下拉浮层 -->
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="showExportMenu"
            class="absolute right-0 mt-1.5 w-44 rounded-xl bg-zinc-900/95 border border-white/[0.12] shadow-2xl p-1 z-50 backdrop-blur-xl origin-top-right text-xs"
          >
            <button
              @click="exportTicketsCSV(); showExportMenu = false"
              class="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center space-x-2 text-zinc-200 hover:text-amber-300 hover:bg-white/[0.08] transition-colors"
            >
              <svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="flex-1">
                <div class="font-medium">导出 CSV 表格</div>
                <div class="text-[10px] text-zinc-400">含 UTF-8 BOM 兼容 Excel</div>
              </div>
            </button>

            <div class="my-1 border-t border-white/[0.06]"></div>

            <button
              @click="printTicketsTable(); showExportMenu = false"
              class="w-full px-2.5 py-1.5 rounded-lg text-left flex items-center space-x-2 text-zinc-200 hover:text-indigo-300 hover:bg-white/[0.08] transition-colors"
            >
              <svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <div class="flex-1">
                <div class="font-medium">打印工单清册</div>
                <div class="text-[10px] text-zinc-400">标准 A4 白底交接单</div>
              </div>
            </button>
          </div>
        </Transition>
      </div>
    </div>

    <!-- 状态过滤胶囊（独立行） -->
    <div class="flex items-center space-x-1 text-xs bg-zinc-900/60 p-0.5 rounded-lg border border-white/[0.06] w-fit">
      <button
        v-for="s in statusOptions"
        :key="s.value"
        @click="selectedStatus = s.value"
        :class="[
          'px-2.5 py-1 rounded-md text-[11px] transition-all',
          selectedStatus === s.value
            ? 'bg-zinc-800 text-zinc-100 font-medium shadow-sm border border-white/[0.08]'
            : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50 border border-transparent'
        ]"
      >
        {{ s.label }}
      </button>
    </div>

    <!-- 搜索栏与刷新栏 -->
    <div class="flex items-center space-x-2">
      <div class="relative flex-1">
        <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索工单编号、故障描述、关联设备或报修内容..."
          class="w-full bg-black/25 backdrop-blur-sm border border-white/[0.08] focus:border-indigo-500/60 rounded-lg pl-8 pr-8 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
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

      <button
        @click="$emit('refresh')"
        class="px-2.5 py-1.5 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-white/[0.08] hover:border-white/[0.15] text-xs flex items-center space-x-1 transition-all shrink-0 active:scale-95 shadow-sm"
        title="刷新工单列表"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span class="hidden sm:inline">刷新</span>
      </button>
    </div>

    <!-- 表格区域 (Linear Dark Table) -->
    <div ref="tableContainerRef" class="overflow-x-hidden rounded-xl border border-white/[0.08] min-h-[300px] max-h-[580px] overflow-y-auto bg-black/25 backdrop-blur-sm shadow-sm">
      <table class="w-full table-fixed text-left text-xs text-zinc-300 border-separate border-spacing-0">
        <thead class="bg-black/50 text-[11px] text-zinc-300 sticky top-0 uppercase tracking-wider border-b border-white/[0.06] backdrop-blur-md z-10">
          <tr>
            <th class="w-[124px] py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">工单编号</th>
            <th class="w-auto py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text">工单标题与处置内容</th>
            <th class="w-[70px] py-2.5 px-1 text-center border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">等级</th>
            <th class="w-[76px] py-2.5 px-1 text-center border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">流转状态</th>
            <th class="w-[102px] py-2.5 px-2 border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">关联设备</th>
            <th class="w-[190px] py-2.5 px-3 text-right border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">处置操作</th>
          </tr>
        </thead>
        <tbody class="font-sans">
          <tr v-if="filteredTickets.length === 0">
            <td colspan="6" class="py-12 text-center text-zinc-500 text-xs">
              未检索到符合条件的运维工单
            </td>
          </tr>
          <tr
            v-for="t in filteredTickets"
            :key="t.id"
            :class="[
              'transition-all duration-300 hover:bg-white/[0.06] text-xs border-b border-white/[0.04]',
              t.ticket_no === highlightedTicketNo
                ? 'animate-pulse-ticket font-medium text-amber-200'
                : ''
            ]"
          >
            <!-- 工单编号 (点击在左侧对话中查询此工单进展) -->
            <td class="py-2.5 px-3 font-mono text-[11px] text-zinc-300 whitespace-nowrap truncate">
              <span
                @click="$emit('inspectTicket', t.ticket_no)"
                class="hover:underline hover:text-amber-400 cursor-pointer inline-flex items-center gap-1.5 transition-colors truncate max-w-full"
                title="点击在左侧对话中查询此工单进展"
              >
                <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="t.status === 'RESOLVED' || t.status === 'CLOSED' ? 'bg-zinc-600' : 'bg-amber-400'"></span>
                <span class="truncate">{{ t.ticket_no }}</span>
              </span>
            </td>

            <!-- 标题与排查要求 -->
            <td class="py-2.5 px-3 overflow-hidden">
              <div class="font-medium text-zinc-200 truncate" :title="t.title">{{ t.title }}</div>
              <div class="text-[11px] text-zinc-500 truncate" :title="t.description">{{ t.description }}</div>
            </td>

            <!-- 优先级 (Linear Badge) -->
            <td class="py-2.5 px-1 text-center whitespace-nowrap">
              <span :class="['px-1.5 py-0.5 rounded text-[10px] font-mono inline-block', priorityClass(t.priority)]">
                {{ t.priority }}
              </span>
            </td>

            <!-- 状态 (Linear Badge) -->
            <td class="py-2.5 px-1 text-center whitespace-nowrap">
              <span :class="['px-1.5 py-0.5 rounded text-[10px] font-mono inline-block', statusClass(t.status)]">
                {{ statusLabel(t.status) }}
              </span>
            </td>

            <!-- 关联设备 -->
            <td class="py-2.5 px-2 font-mono text-[11px] text-zinc-400 whitespace-nowrap truncate" :title="t.device_id || '-'">
              {{ t.device_id || '-' }}
            </td>

            <!-- 快速流转推进与操作按钮 (固定宽度严整对齐) -->
            <td class="py-2.5 px-3 text-right whitespace-nowrap">
              <div class="flex items-center justify-end gap-2">
                <!-- 辅助功能按钮容器 (固定宽度 84px 与左对齐槽位排列，各行垂直严格对齐) -->
                <div class="w-[84px] flex items-center justify-start gap-1.5 shrink-0">
                  <!-- 1. 工单流转脉络时间轴按钮 (所有角色包括学生均可查阅) -->
                  <button
                    @click="$emit('viewTimeline', t.ticket_no)"
                    class="w-6 h-6 flex items-center justify-center shrink-0 rounded-md bg-zinc-800/80 hover:bg-zinc-700 text-zinc-400 hover:text-amber-400 border border-white/[0.08] text-[11px] transition-all active:scale-95 shadow-sm"
                    title="查看工单流转脉络时间轴"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>

                  <!-- 教师与管理员：编辑与作废删除按钮 -->
                  <template v-if="!isStudent">
                    <!-- 2. 编辑工单按钮 (管理员可编辑全部工单；教师仅可编辑本人创建的工单，否则禁用置灰) -->
                    <button
                      v-if="canEditTicket(t)"
                      @click="openEditTicketModal(t)"
                      class="w-6 h-6 flex items-center justify-center shrink-0 rounded-md bg-zinc-800/80 hover:bg-zinc-700 text-zinc-400 hover:text-indigo-400 border border-white/[0.08] text-[11px] transition-all active:scale-95 shadow-sm"
                      title="编辑工单要素 (标题、描述、优先级、关联设备)"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      v-else
                      disabled
                      class="w-6 h-6 flex items-center justify-center shrink-0 rounded-md bg-zinc-900/40 text-zinc-600 border border-white/[0.04] text-[11px] cursor-not-allowed opacity-40"
                      :title="isTeacher ? '无权编辑：教师仅可编辑本人创建的工单' : '无权编辑：仅工单创建教师或超级管理员可编辑'"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>

                    <!-- 3. 作废/删除工单按钮 -->
                    <button
                      @click="openDeleteTicketModal(t)"
                      class="w-6 h-6 flex items-center justify-center shrink-0 rounded-md bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 text-[11px] transition-all active:scale-95 shadow-sm"
                      title="作废并删除此工单"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </template>
                </div>

                <!-- 处置主操作区域 (严格定宽 w-16，确保各状态按钮居中且绝不影响左侧三个按钮对齐) -->
                <div class="w-16 flex items-center justify-center shrink-0">
                  <!-- 学生角色：显示微标「学生只读」 -->
                  <span
                    v-if="isStudent"
                    class="w-full text-center py-0.5 rounded text-[10px] font-mono bg-zinc-800/80 text-zinc-400 border border-white/[0.08] inline-block shadow-sm"
                    title="学生角色对机房运维工单仅有只读权限"
                  >
                    学生只读
                  </span>

                  <!-- 教师与管理员：根据工单状态显示对应处置操作 -->
                  <template v-else>
                    <!-- 待处理工单：受理 -->
                    <button
                      v-if="t.status === 'PENDING'"
                      @click="openWorkflowModal(t, 'PROCESSING')"
                      class="w-full text-center py-0.5 rounded-md bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 text-[11px] transition-all active:scale-95 shadow-sm font-mono"
                      title="认领并开始处理工单，录入处置排查备忘"
                    >
                      受理
                    </button>

                    <!-- 处理中工单：办结 -->
                    <button
                      v-else-if="t.status === 'PROCESSING'"
                      @click="openWorkflowModal(t, 'RESOLVED')"
                      class="w-full text-center py-0.5 rounded-md text-[11px] transition-all font-mono border bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border-emerald-500/20 active:scale-95 shadow-sm"
                      title="办结此工单并出具排查处置说明"
                    >
                      办结
                    </button>

                    <!-- 已解决工单：归档 -->
                    <button
                      v-else-if="t.status === 'RESOLVED'"
                      @click="openWorkflowModal(t, 'CLOSED')"
                      class="w-full text-center py-0.5 rounded-md text-[11px] transition-all font-mono border bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/[0.08] active:scale-95 shadow-sm"
                      title="归档此工单"
                    >
                      归档
                    </button>

                    <!-- 已关闭工单：已闭环 -->
                    <span
                      v-else-if="t.status === 'CLOSED'"
                      class="w-full text-center py-0.5 text-[11px] text-zinc-500 font-mono"
                    >
                      已闭环
                    </span>
                  </template>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 运维工单流转处置小结录入独立弹窗 -->
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
          v-if="showWorkflowModal"
          @keydown.esc.window="showWorkflowModal = false"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/75 backdrop-blur-md overflow-hidden"
          @click.self="showWorkflowModal = false"
        >
          <div
            class="w-full max-w-lg rounded-3xl bg-zinc-900/95 border border-white/[0.12] ring-1 ring-white/[0.05] p-5 sm:p-6 space-y-4 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] backdrop-blur-2xl text-zinc-100"
          >
            <!-- 头部 -->
            <div class="flex items-center justify-between border-b border-white/[0.08] pb-3">
              <div class="flex items-center space-x-3">
                <span
                  class="p-2.5 rounded-2xl border flex items-center justify-center shrink-0 shadow-sm"
                  :class="targetWorkflowStatus === 'PROCESSING' ? 'bg-blue-500/10 border-blue-500/30 text-blue-400' : targetWorkflowStatus === 'RESOLVED' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-zinc-800 border-white/[0.1] text-zinc-300'"
                >
                  <svg v-if="targetWorkflowStatus === 'PROCESSING'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else-if="targetWorkflowStatus === 'RESOLVED'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                  </svg>
                </span>
                <div>
                  <h4 class="text-sm sm:text-base font-semibold tracking-tight">
                    {{ workflowModalTitle }}
                  </h4>
                  <div class="flex items-center space-x-2 mt-0.5 text-xs text-zinc-400">
                    <span class="font-mono text-cyan-400 font-semibold">{{ targetTicket?.ticket_no }}</span>
                    <span>·</span>
                    <span class="truncate max-w-[200px]">{{ targetTicket?.title }}</span>
                  </div>
                </div>
              </div>

              <button
                @click="showWorkflowModal = false"
                class="text-zinc-400 hover:text-zinc-100 p-1.5 rounded-full hover:bg-white/[0.08] transition-colors"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- 流转状态动向胶囊 -->
            <div class="p-2.5 rounded-xl bg-zinc-950/60 border border-white/[0.06] flex items-center justify-between text-xs font-mono">
              <span class="text-zinc-400">流转节点变迁:</span>
              <div class="flex items-center space-x-2">
                <span :class="['px-2 py-0.5 rounded text-[10px] font-mono', statusClass(targetTicket?.status)]">
                  {{ statusLabel(targetTicket?.status) }}
                </span>
                <span class="text-zinc-500">➔</span>
                <span :class="['px-2 py-0.5 rounded text-[10px] font-mono font-semibold', statusClass(targetWorkflowStatus)]">
                  {{ statusLabel(targetWorkflowStatus) }}
                </span>
              </div>
            </div>

            <!-- 处置人 -->
            <div class="space-y-1">
              <label class="text-xs font-medium text-zinc-300 flex items-center justify-between">
                <span>处置操作人 (Operator)</span>
                <span class="text-[10px] text-zinc-500">自动带入当前登录身份</span>
              </label>
              <input
                v-model="workflowOperator"
                type="text"
                placeholder="请输入处置人姓名或工号..."
                class="w-full bg-zinc-950/80 border border-white/[0.08] focus:border-cyan-500 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors font-mono"
              />
            </div>

            <!-- 快捷处理小结选项 -->
            <div class="space-y-1.5">
              <label class="text-xs font-medium text-zinc-300 flex items-center justify-between">
                <span>快捷常用处理小结</span>
                <span class="text-[10px] text-zinc-500">点击自动填入处置备忘</span>
              </label>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="(preset, idx) in currentWorkflowPresets"
                  :key="idx"
                  type="button"
                  @click="applyPresetComment(preset)"
                  class="px-2.5 py-1 rounded-lg text-[11px] bg-zinc-800/80 hover:bg-zinc-700 hover:text-cyan-300 text-zinc-300 border border-white/[0.06] transition-all active:scale-95 text-left"
                >
                  + {{ preset }}
                </button>
              </div>
            </div>

            <!-- 自定义处置说明输入框 -->
            <div class="space-y-1">
              <label class="text-xs font-medium text-zinc-300 flex items-center justify-between">
                <span>排查处置说明 (Comment) <span class="text-rose-400">*</span></span>
                <span class="text-[10px] text-zinc-500">将写入全生命周期工单时序履历</span>
              </label>
              <textarea
                v-model="workflowComment"
                rows="3"
                placeholder="请详细记录排障现场检查情况、处置动作与测试结论..."
                class="w-full bg-zinc-950/80 border border-white/[0.08] focus:border-cyan-500 rounded-xl p-3 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors resize-none leading-relaxed"
              ></textarea>
            </div>

            <!-- 错误提示 -->
            <div v-if="workflowError" class="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {{ workflowError }}
            </div>

            <!-- 底部按钮 -->
            <div class="flex items-center justify-end space-x-2 pt-2 border-t border-white/[0.08]">
              <button
                @click="showWorkflowModal = false"
                class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors"
              >
                取消
              </button>
              <button
                @click="submitWorkflowUpdate"
                :disabled="isSubmittingWorkflow || !workflowComment.trim()"
                class="px-5 py-2 rounded-xl text-white font-medium text-xs shadow-md transition-all active:scale-95 disabled:opacity-40 flex items-center space-x-1.5"
                :class="targetWorkflowStatus === 'PROCESSING' ? 'bg-blue-600 hover:bg-blue-500' : targetWorkflowStatus === 'RESOLVED' ? 'bg-emerald-600 hover:bg-emerald-500' : 'bg-zinc-700 hover:bg-zinc-600'"
              >
                <span v-if="isSubmittingWorkflow" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>{{ isSubmittingWorkflow ? '提交流转中...' : '确认流转并记录备忘' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 运维工单快速编辑模态框 -->
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
          v-if="showEditTicketModal"
          @keydown.esc.window="showEditTicketModal = false"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/75 backdrop-blur-md overflow-hidden"
          @click.self="showEditTicketModal = false"
        >
          <div
            class="w-full max-w-lg rounded-3xl bg-zinc-900/95 border border-white/[0.12] ring-1 ring-white/[0.05] p-5 sm:p-6 space-y-4 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] backdrop-blur-2xl text-zinc-100"
          >
            <!-- 头部 -->
            <div class="flex items-center justify-between border-b border-white/[0.08] pb-3">
              <div class="flex items-center space-x-3">
                <span class="p-2.5 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 flex items-center justify-center shrink-0 shadow-sm">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </span>
                <div>
                  <h4 class="text-sm sm:text-base font-semibold tracking-tight">
                    编辑机房运维工单
                  </h4>
                  <p class="text-xs text-zinc-400 mt-0.5 font-mono">
                    工单编号: {{ editTicketData.ticket_no }}
                  </p>
                </div>
              </div>

              <button
                @click="showEditTicketModal = false"
                class="text-zinc-400 hover:text-zinc-100 p-1.5 rounded-full hover:bg-white/[0.08] transition-colors"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- 表单内容 -->
            <form @submit.prevent="submitEditTicket" class="space-y-3.5 text-xs">
              <div class="space-y-1">
                <label class="font-medium text-zinc-300">工单标题 <span class="text-rose-400">*</span></label>
                <input
                  v-model="editTicketData.title"
                  type="text"
                  required
                  placeholder="请输入工单标题..."
                  class="w-full bg-zinc-950/80 border border-white/[0.08] focus:border-cyan-500 rounded-xl px-3.5 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
                />
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="space-y-1">
                  <label class="font-medium text-zinc-300">优先级等级</label>
                  <select
                    v-model="editTicketData.priority"
                    class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-xl px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
                  >
                    <option value="LOW">LOW (低)</option>
                    <option value="MEDIUM">MEDIUM (中)</option>
                    <option value="HIGH">HIGH (高)</option>
                    <option value="CRITICAL">CRITICAL (紧急高危)</option>
                  </select>
                </div>

                <div class="space-y-1">
                  <label class="font-medium text-zinc-300">关联设备编号</label>
                  <input
                    v-model="editTicketData.device_id"
                    type="text"
                    placeholder="例如: DEV-SRV-201"
                    class="w-full bg-zinc-950/80 border border-white/[0.08] focus:border-cyan-500 rounded-xl px-3.5 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
                  />
                </div>
              </div>

              <div class="space-y-1">
                <label class="font-medium text-zinc-300">故障排查描述与处置内容 <span class="text-rose-400">*</span></label>
                <textarea
                  v-model="editTicketData.description"
                  rows="3"
                  required
                  placeholder="详细记录故障现象、报修原因与排障要求..."
                  class="w-full bg-zinc-950/80 border border-white/[0.08] focus:border-cyan-500 rounded-xl p-3 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors resize-none leading-relaxed"
                ></textarea>
              </div>

              <div v-if="editTicketError" class="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
                {{ editTicketError }}
              </div>

              <div class="flex items-center justify-end space-x-2 pt-2 border-t border-white/[0.08]">
                <button
                  type="button"
                  @click="showEditTicketModal = false"
                  class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  :disabled="isSubmittingEdit || !editTicketData.title.trim() || !editTicketData.description.trim()"
                  class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs shadow-md transition-all active:scale-95 disabled:opacity-40 flex items-center space-x-1.5"
                >
                  <span v-if="isSubmittingEdit" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  <span>{{ isSubmittingEdit ? '保存中...' : '保存工单修改' }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 运维工单作废/删除二次确认模态框 -->
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
          v-if="showDeleteTicketModal"
          @keydown.esc.window="showDeleteTicketModal = false"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/75 backdrop-blur-md overflow-hidden"
          @click.self="showDeleteTicketModal = false"
        >
          <div
            class="w-full max-w-sm rounded-3xl bg-zinc-900 border border-white/[0.12] p-5 space-y-4 shadow-2xl backdrop-blur-2xl text-zinc-100"
          >
            <div class="flex items-center space-x-3">
              <span class="p-2.5 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-400">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </span>
              <div>
                <h4 class="text-sm font-semibold tracking-tight">作废/删除工单确认</h4>
                <p class="text-xs text-zinc-400 mt-0.5">此操作将彻底物理删除该工单与所有流转时序记录</p>
              </div>
            </div>

            <div class="p-3 rounded-2xl bg-zinc-950/60 border border-white/[0.04] text-xs space-y-1">
              <div>待作废工单：<span class="font-medium text-rose-400 font-mono">{{ ticketToDelete?.ticket_no }}</span></div>
              <div class="truncate text-zinc-300">工单标题：{{ ticketToDelete?.title }}</div>
              <div class="text-[11px] text-zinc-500 pt-1 border-t border-white/[0.04]">状态：{{ statusLabel(ticketToDelete?.status) }} · 优先级：{{ ticketToDelete?.priority }}</div>
            </div>

            <div v-if="deleteTicketError" class="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {{ deleteTicketError }}
            </div>

            <div class="flex items-center justify-end space-x-2 pt-2 border-t border-white/[0.06]">
              <button
                @click="showDeleteTicketModal = false"
                class="px-3.5 py-1.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-white/[0.06] text-xs transition-colors"
              >
                取消
              </button>
              <button
                @click="confirmDeleteTicket"
                :disabled="isDeletingTicket"
                class="px-4 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md transition-all active:scale-95 disabled:opacity-50 flex items-center space-x-1.5"
              >
                <span v-if="isDeletingTicket" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>{{ isDeletingTicket ? '正在作废删除...' : '确认作废删除' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  tickets: {
    type: Array,
    default: () => [],
  },
  currentUser: {
    type: Object,
    default: null,
  },
  highlightedTicketNo: {
    type: String,
    default: '',
  },
})

const userRole = computed(() => (props.currentUser?.role || 'STUDENT').toUpperCase())
const isStudent = computed(() => userRole.value === 'STUDENT')
const isTeacher = computed(() => userRole.value === 'TEACHER')
const isAdmin = computed(() => userRole.value === 'ADMIN')

const emit = defineEmits(['refresh', 'updateStatus', 'inspectTicket', 'viewTimeline'])

// 运维工单流转处置备忘弹窗状态与操作
const showWorkflowModal = ref(false)
const targetTicket = ref(null)
const targetWorkflowStatus = ref('PROCESSING')
const workflowOperator = ref('')
const workflowComment = ref('')
const isSubmittingWorkflow = ref(false)
const workflowError = ref('')

const workflowModalTitle = computed(() => {
  switch (targetWorkflowStatus.value) {
    case 'PROCESSING':
      return '认领并开始处置工单 (流转至处理中)'
    case 'RESOLVED':
      return '出具工单排查处置报告 (流转至已解决)'
    case 'CLOSED':
      return '核验并正式闭环归档工单'
    default:
      return '运维工单流转处置备忘'
  }
})

const presetOptions = {
  PROCESSING: [
    '现场巡检已启动，正核实告警硬件指标',
    '已联系责任教师核实验证异常现象',
    '已根据安全规程启动前置降频保护，展开故障排查',
  ],
  RESOLVED: [
    '现场巡检已完成并更换风扇',
    '已根据安全条例完成降频降载处置',
    '动环温湿度探针校准完毕，告警消除',
    '硬件冷备板卡热插拔替换完毕，性能恢复正常',
    '高负荷计算作业迁移至从机架，实测功率已回落至安全阈值以下',
  ],
  CLOSED: [
    '连续观察24小时各项遥测参数平稳，确认故障根除',
    '运维主管现场核验合格，同意归档结案',
  ],
}

const currentWorkflowPresets = computed(() => {
  return presetOptions[targetWorkflowStatus.value] || []
})

function applyPresetComment(preset) {
  if (!workflowComment.value.trim()) {
    workflowComment.value = preset
  } else {
    workflowComment.value += `；${preset}`
  }
}

function openWorkflowModal(ticket, newStatus) {
  targetTicket.value = ticket
  targetWorkflowStatus.value = newStatus
  workflowOperator.value = props.currentUser?.real_name || props.currentUser?.username || '运维值班员'
  workflowComment.value = ''
  workflowError.value = ''
  showWorkflowModal.value = true
}

async function submitWorkflowUpdate() {
  if (!targetTicket.value) return
  if (!workflowComment.value.trim()) {
    workflowError.value = '请填写流转处置说明'
    return
  }
  isSubmittingWorkflow.value = true
  workflowError.value = ''

  const payload = {
    status: targetWorkflowStatus.value,
    operator: workflowOperator.value.trim() || '系统管理员',
    operator_role: props.currentUser?.role || 'ADMIN',
    comment: workflowComment.value.trim(),
  }

  try {
    await api.updateTicket(targetTicket.value.id, payload)
    showWorkflowModal.value = false
    emit('refresh')
    emit('updateStatus', targetTicket.value.id, targetWorkflowStatus.value, payload)
  } catch (err) {
    workflowError.value = err.message || '更新工单状态失败，请重试'
  } finally {
    isSubmittingWorkflow.value = false
  }
}

// -------------------------------------------------------------
// [EDIT & DELETE] 运维工单快速编辑与作废物理删除闭环
// -------------------------------------------------------------
const showEditTicketModal = ref(false)
const editTicketData = reactive({
  id: null,
  ticket_no: '',
  title: '',
  description: '',
  priority: 'MEDIUM',
  device_id: '',
})
const isSubmittingEdit = ref(false)
const editTicketError = ref('')

function canEditTicket(ticket) {
  if (!props.currentUser) return false
  if (isStudent.value) return false
  if (isAdmin.value) return true
  if (isTeacher.value) {
    const creator = (ticket?.creator || '').trim().toLowerCase()
    const username = (props.currentUser?.username || '').trim().toLowerCase()
    const realName = (props.currentUser?.real_name || '').trim().toLowerCase()
    if (!creator) return false
    return (
      (username && creator === username) ||
      (realName && creator === realName) ||
      (username && creator.includes(username)) ||
      (realName && creator.includes(realName))
    )
  }
  return false
}

function openEditTicketModal(ticket) {
  if (!canEditTicket(ticket)) {
    return
  }
  editTicketData.id = ticket.id
  editTicketData.ticket_no = ticket.ticket_no
  editTicketData.title = ticket.title || ''
  editTicketData.description = ticket.description || ''
  editTicketData.priority = ticket.priority || 'MEDIUM'
  editTicketData.device_id = ticket.device_id || ''
  editTicketError.value = ''
  showEditTicketModal.value = true
}

async function submitEditTicket() {
  if (!editTicketData.id || !editTicketData.title.trim() || !editTicketData.description.trim()) {
    editTicketError.value = '请完整填写工单标题与处置内容描述'
    return
  }
  const target = props.tickets.find((t) => t.id === editTicketData.id)
  if (target && !canEditTicket(target)) {
    editTicketError.value = '您暂无权限修改此工单（教师仅可修改本人创建的工单）'
    return
  }
  isSubmittingEdit.value = true
  editTicketError.value = ''
  try {
    await api.updateTicket(editTicketData.id, {
      title: editTicketData.title.trim(),
      description: editTicketData.description.trim(),
      priority: editTicketData.priority,
      device_id: editTicketData.device_id.trim() || null,
      operator: props.currentUser?.real_name || props.currentUser?.username || '管理员',
      operator_role: props.currentUser?.role || 'ADMIN',
      comment: '更新了工单基本要素属性',
    })
    showEditTicketModal.value = false
    emit('refresh')
  } catch (err) {
    editTicketError.value = err.message || '更新工单失败，请重试'
  } finally {
    isSubmittingEdit.value = false
  }
}

const showDeleteTicketModal = ref(false)
const ticketToDelete = ref(null)
const isDeletingTicket = ref(false)
const deleteTicketError = ref('')

function openDeleteTicketModal(ticket) {
  ticketToDelete.value = ticket
  deleteTicketError.value = ''
  showDeleteTicketModal.value = true
}

async function confirmDeleteTicket() {
  if (!ticketToDelete.value) return
  isDeletingTicket.value = true
  deleteTicketError.value = ''
  try {
    await api.deleteTicket(ticketToDelete.value.id)
    showDeleteTicketModal.value = false
    ticketToDelete.value = null
    emit('refresh')
  } catch (err) {
    deleteTicketError.value = err.message || '作废删除工单失败，请重试'
  } finally {
    isDeletingTicket.value = false
  }
}

const tableContainerRef = ref(null)
const selectedStatus = ref('ALL')
const keyword = ref('')

watch(
  () => props.highlightedTicketNo,
  (newVal) => {
    if (newVal) {
      selectedStatus.value = 'ALL'
      keyword.value = ''
      nextTick(() => {
        if (tableContainerRef.value) {
          tableContainerRef.value.scrollTop = 0
        }
      })
    }
  }
)

const statusOptions = [
  { label: '全部', value: 'ALL' },
  { label: '待处理', value: 'PENDING' },
  { label: '处理中', value: 'PROCESSING' },
  { label: '已解决', value: 'RESOLVED' },
  { label: '已关闭', value: 'CLOSED' },
]

const filteredTickets = computed(() => {
  return props.tickets.filter((t) => {
    if (selectedStatus.value !== 'ALL' && t.status !== selectedStatus.value) {
      return false
    }
    if (keyword.value.trim()) {
      const kw = keyword.value.trim().toLowerCase()
      const matchNo = (t.ticket_no || '').toLowerCase().includes(kw)
      const matchTitle = (t.title || '').toLowerCase().includes(kw)
      const matchDev = (t.device_id || '').toLowerCase().includes(kw)
      const matchDesc = (t.description || '').toLowerCase().includes(kw)
      return matchNo || matchTitle || matchDev || matchDesc
    }
    return true
  })
})

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

function statusClass(status) {
  switch (status) {
    case 'PENDING':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'PROCESSING':
      return 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
    case 'RESOLVED':
      return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
    case 'CLOSED':
      return 'bg-zinc-800 text-zinc-500 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}

// -------------------------------------------------------------
// [FEAT-06] 工单明细一键导出 (CSV) 与 A4 纸质打印归档
// -------------------------------------------------------------
const exportMenuRef = ref(null)
const showExportMenu = ref(false)

function handleDocumentClick(e) {
  if (exportMenuRef.value && !exportMenuRef.value.contains(e.target)) {
    showExportMenu.value = false
  }
}

function handleDocumentKeydown(e) {
  if (e.key === 'Escape' && showExportMenu.value) {
    showExportMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleDocumentKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleDocumentKeydown)
})

function padZero(n) {
  return String(n).padStart(2, '0')
}

function getFormattedTimestamp() {
  const now = new Date()
  const y = now.getFullYear()
  const m = padZero(now.getMonth() + 1)
  const d = padZero(now.getDate())
  const h = padZero(now.getHours())
  const min = padZero(now.getMinutes())
  const s = padZero(now.getSeconds())
  return `${y}${m}${d}_${h}${min}${s}`
}

function escapeHtml(val) {
  if (val === null || val === undefined) return ''
  return String(val)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function escapeCsv(val) {
  if (val === null || val === undefined) return '""'
  let str = String(val)
  // 防范 Excel 宏/公式注入 (DDE attack)
  if (/^[=+@\t\r]/.test(str) || /^-[0-9a-zA-Z(]/.test(str)) {
    str = "'" + str
  }
  return `"${str.replace(/"/g, '""')}"`
}

function priorityLabel(priority) {
  switch (priority) {
    case 'CRITICAL':
      return '紧急'
    case 'HIGH':
      return '高'
    case 'MEDIUM':
      return '中'
    case 'LOW':
      return '低'
    default:
      return priority || '-'
  }
}

function formatDateTime(val) {
  if (!val) return '-'
  const d = new Date(val)
  if (isNaN(d.getTime())) return String(val)
  return d.toLocaleString('zh-CN', { hour12: false })
}

function exportTicketsCSV() {
  const list = filteredTickets.value || []
  const headers = [
    '工单编号',
    '工单标题',
    '关联设备',
    '优先级',
    '当前状态',
    '创建时间',
    '更新时间',
    '故障描述摘要',
  ]
  const rows = list.map((t) => [
    escapeCsv(t.ticket_no || ''),
    escapeCsv(t.title || ''),
    escapeCsv(t.device_id || ''),
    escapeCsv(priorityLabel(t.priority)),
    escapeCsv(statusLabel(t.status)),
    escapeCsv(formatDateTime(t.created_at)),
    escapeCsv(formatDateTime(t.updated_at)),
    escapeCsv(t.description || ''),
  ])

  const csvContent = [
    headers.map(escapeCsv).join(','),
    ...rows.map((r) => r.join(',')),
  ].join('\r\n')

  const bom = '\uFEFF'
  const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `运维工单明细_${getFormattedTimestamp()}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function printTicketsTable() {
  const list = filteredTickets.value || []
  const operatorName = props.currentUser?.real_name || props.currentUser?.username || '运维工程师'
  const printTime = new Date().toLocaleString('zh-CN', { hour12: false })

  const rowsHtml = list
    .map((t, index) => {
      let priorityBadgeStyle = 'background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;'
      if (t.priority === 'CRITICAL') priorityBadgeStyle = 'background:#fef2f2;color:#991b1b;border:1px solid #fecaca;font-weight:bold;'
      if (t.priority === 'HIGH') priorityBadgeStyle = 'background:#fffbeb;color:#92400e;border:1px solid #fde68a;'
      if (t.priority === 'MEDIUM') priorityBadgeStyle = 'background:#f0f9ff;color:#0369a1;border:1px solid #bae6fd;'

      let statusBadgeStyle = 'background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;'
      if (t.status === 'PENDING') statusBadgeStyle = 'background:#fffbeb;color:#92400e;border:1px solid #fde68a;'
      if (t.status === 'PROCESSING') statusBadgeStyle = 'background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;'
      if (t.status === 'RESOLVED') statusBadgeStyle = 'background:#f0fdf4;color:#166534;border:1px solid #bbf7d0;'

      return `
        <tr style="border-bottom: 1px solid #e2e8f0; ${index % 2 === 1 ? 'background-color: #f8fafc;' : ''}">
          <td style="padding: 6px 8px; text-align: center; color: #64748b; font-family: monospace;">${index + 1}</td>
          <td style="padding: 6px 8px; text-align: center; font-family: monospace; font-weight: 600; color: #d97706;">${escapeHtml(t.ticket_no || '-')}</td>
          <td style="padding: 6px 8px; font-weight: 600; color: #0f172a;">${escapeHtml(t.title || '-')}</td>
          <td style="padding: 6px 8px; text-align: center; font-family: monospace; color: #475569;">${escapeHtml(t.device_id || '-')}</td>
          <td style="padding: 6px 8px; text-align: center;">
            <span style="display:inline-block;padding:2px 6px;border-radius:4px;font-size:10px;${priorityBadgeStyle}">${escapeHtml(priorityLabel(t.priority))}</span>
          </td>
          <td style="padding: 6px 8px; text-align: center;">
            <span style="display:inline-block;padding:2px 6px;border-radius:4px;font-size:10px;${statusBadgeStyle}">${escapeHtml(statusLabel(t.status))}</span>
          </td>
          <td style="padding: 6px 8px; text-align: center; font-size: 10px; color: #64748b;">${escapeHtml(formatDateTime(t.created_at))}</td>
          <td style="padding: 6px 8px; text-align: center; font-size: 10px; color: #64748b;">${escapeHtml(formatDateTime(t.updated_at))}</td>
          <td style="padding: 6px 8px; color: #475569; font-size: 10.5px; max-width: 260px;">${escapeHtml(t.description || '-')}</td>
        </tr>
      `
    })
    .join('')

  const printHtml = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>高校实验室运维工单流转与交接归档清册</title>
  <style>
    @page {
      size: A4 landscape;
      margin: 12mm;
    }
    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
      color-adjust: exact !important;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
      margin: 0;
      padding: 0;
      background: #ffffff;
      color: #0f172a;
      font-size: 11px;
      line-height: 1.4;
    }
    .print-header {
      border-bottom: 2px solid #d97706;
      padding-bottom: 8px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    .title-area h1 {
      margin: 0 0 4px 0;
      font-size: 18px;
      font-weight: 700;
      color: #b45309;
      letter-spacing: 0.5px;
    }
    .title-area p {
      margin: 0;
      font-size: 11px;
      color: #64748b;
    }
    .meta-area {
      text-align: right;
      font-size: 10px;
      color: #475569;
    }
    .meta-tag {
      font-weight: 600;
      color: #0f172a;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      border: 1px solid #cbd5e1;
      table-layout: fixed;
      word-break: break-word;
    }
    thead {
      display: table-header-group;
    }
    tr {
      page-break-inside: avoid;
      break-inside: avoid;
    }
    th {
      background-color: #f1f5f9;
      color: #1e293b;
      font-weight: 600;
      padding: 7px 8px;
      border: 1px solid #cbd5e1;
      text-align: center;
      font-size: 11px;
    }
    td {
      border: 1px solid #cbd5e1;
      font-size: 10.5px;
    }
    .footer-signatures {
      margin-top: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: #334155;
      padding-top: 10px;
      border-top: 1px dashed #cbd5e1;
      page-break-inside: avoid;
      break-inside: avoid;
    }
    .footer-note {
      margin-top: 12px;
      font-size: 9.5px;
      color: #94a3b8;
      text-align: center;
      page-break-inside: avoid;
      break-inside: avoid;
    }
  </style>
</head>
<body>
  <div class="print-header">
    <div class="title-area">
      <h1>高校实验室运维工单流转与交接归档清册</h1>
      <p>所属单位：高校人工智能与软件工程重点实验室 · 智能化运维响应组</p>
    </div>
    <div class="meta-area">
      <div>工单总计：<span class="meta-tag">${list.length} 条</span> (当前筛选视图)</div>
      <div>运维责任人 / 经办人：<span class="meta-tag">${escapeHtml(operatorName)}</span></div>
      <div>打印归档时间：<span>${escapeHtml(printTime)}</span></div>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th style="width: 32px;">序号</th>
        <th style="width: 95px;">工单编号</th>
        <th style="width: 150px;">工单标题与处置内容</th>
        <th style="width: 90px;">关联设备</th>
        <th style="width: 55px;">优先级</th>
        <th style="width: 65px;">当前状态</th>
        <th style="width: 110px;">创建时间</th>
        <th style="width: 110px;">更新时间</th>
        <th>故障描述摘要</th>
      </tr>
    </thead>
    <tbody>
      ${rowsHtml || '<tr><td colspan="9" style="text-align:center;padding:20px;color:#94a3b8;">暂无符合条件的工单记录</td></tr>'}
    </tbody>
  </table>

  <div class="footer-signatures">
    <div>运维班组长签字：____________________</div>
    <div>处置工程师 / 经办人签字：____________________</div>
    <div>闭环交接日期：20____年____月____日</div>
  </div>

  <div class="footer-note">
    高校实验室轻量化智能自治运维系统 (LabOps-Agent) · 运维工单流转与纸质交接归档专用件
  </div>
</body>
</html>
  `

  const printFrame = document.createElement('iframe')
  printFrame.setAttribute(
    'style',
    'position:fixed;top:0;left:0;width:1px;height:1px;border:none;opacity:0.01;pointer-events:none;z-index:-9999;'
  )
  document.body.appendChild(printFrame)

  const cleanup = () => {
    try {
      if (printFrame && printFrame.parentNode) {
        printFrame.parentNode.removeChild(printFrame)
      }
    } catch (e) {
      // ignore
    }
  }

  const frameDoc = printFrame.contentWindow?.document
  if (!frameDoc) {
    cleanup()
    window.print()
    return
  }

  frameDoc.open()
  frameDoc.write(printHtml)
  frameDoc.close()

  try {
    printFrame.contentWindow.addEventListener('afterprint', cleanup)
  } catch (e) {
    // fallback
  }

  // 60秒保底释放，防止浏览器不支持 afterprint 时长期驻留 DOM
  setTimeout(cleanup, 60000)

  setTimeout(() => {
    try {
      printFrame.contentWindow.focus()
      printFrame.contentWindow.print()
    } catch (err) {
      console.error('iframe 打印触发失败，回退到主窗口打印:', err)
      cleanup()
      window.print()
    }
  }, 250)
}
</script>
