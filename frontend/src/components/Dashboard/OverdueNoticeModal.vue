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
      :class="theme === 'light' ? 'bg-slate-900/40 backdrop-blur-sm' : 'bg-black/80 backdrop-blur-md'"
      v-backdrop-dismiss="close"
    >
      <!-- 公函模态框主体卡片 -->
      <div
        id="printable-overdue-notice"
        class="overdue-modal-card w-full max-w-3xl rounded-2xl sm:rounded-3xl border flex flex-col max-h-[92vh] overflow-hidden transition-all print:max-h-none print:shadow-none print:border-none print:rounded-none"
        :class="[
          theme === 'light'
            ? 'bg-white border-slate-200 shadow-2xl shadow-slate-400/25 text-slate-900'
            : 'bg-zinc-950/95 border-white/[0.12] shadow-2xl text-zinc-100'
        ]"
      >
        <!-- 1. 顶部操作条 (屏幕显示，打印时隐藏) -->
        <div
          class="flex items-center justify-between border-b px-5 py-3.5 shrink-0 print:hidden"
          :class="theme === 'light' ? 'border-slate-200 bg-slate-50/90' : 'border-white/[0.08] bg-white/[0.02]'"
        >
          <div class="flex items-center space-x-2.5">
            <span class="p-1.5 rounded-lg bg-rose-500/10 text-rose-500 border border-rose-500/20">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </span>
            <div>
              <div class="text-xs font-semibold tracking-wide flex items-center gap-2">
                <span>超期借用催告公文系统</span>
                <span
                  v-if="notice"
                  class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20"
                >
                  已逾期 {{ notice.overdue_days }} 天
                </span>
              </div>
              <p class="text-[11px] text-zinc-400 font-mono">
                公文字号: {{ notice?.doc_code || (loading ? '公文生成中...' : '暂无字号') }}
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <!-- 一键复制按钮 -->
            <button
              v-if="notice"
              @click="copyNoticeContent"
              class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1.5 transition-all active:scale-95 shadow-sm"
              :class="[
                copied
                  ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400'
                  : theme === 'light'
                    ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300'
                    : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border-white/[0.12]'
              ]"
              :title="copied ? '已复制公文全文' : '复制催告函全文至剪贴板'"
            >
              <svg v-if="copied" class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
              </svg>
              <span>{{ copied ? '已复制' : '复制公文' }}</span>
            </button>

            <!-- 打印/导出 PDF 按钮 -->
            <button
              v-if="notice"
              @click="printNotice"
              class="px-2.5 py-1.5 rounded-lg text-xs font-medium border flex items-center space-x-1.5 transition-all active:scale-95 shadow-sm"
              :class="theme === 'light' ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300' : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border-white/[0.12]'"
              title="调用打印机或导出 A4 单页 PDF"
            >
              <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4H7v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <span>打印/导出</span>
            </button>

            <!-- 关闭按钮 -->
            <button
              @click="close"
              class="p-1.5 rounded-lg transition-colors"
              :class="theme === 'light' ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-200/60' : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.08]'"
              title="关闭弹窗"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 2. 加载中状态 -->
        <div v-if="loading" class="flex-1 flex flex-col items-center justify-center p-12 space-y-4">
          <div class="relative w-10 h-10">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-60"></span>
            <span class="relative inline-flex rounded-full h-10 w-10 border-2 border-rose-500 border-t-transparent animate-spin"></span>
          </div>
          <p class="text-xs font-mono" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">正在研判并起草合规《设备资产超期归还催告单》公文...</p>
        </div>

        <!-- 3. 错误或无须催告状态 -->
        <div v-else-if="errorMessage" class="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-4">
          <div class="p-3 rounded-2xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="max-w-md space-y-1.5">
            <h4 class="text-sm font-semibold" :class="theme === 'light' ? 'text-slate-800' : 'text-zinc-200'">无需出具催告通知函</h4>
            <p class="text-xs leading-relaxed" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">{{ errorMessage }}</p>
          </div>
          <button
            @click="close"
            class="px-4 py-2 rounded-xl text-xs font-medium transition-colors border"
            :class="theme === 'light' ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-300' : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-white/[0.08]'"
          >
            返回台账
          </button>
        </div>

        <!-- 4. 红头公文正文区 (支持滚动与单页打印) -->
        <div v-else-if="notice" class="flex-1 overflow-y-auto p-5 sm:p-8 space-y-6 print:p-0 print:overflow-visible">
          <!-- 4.1 红头公文首部 (Red-letter Official Header) -->
          <div class="text-center space-y-2 border-b-2 border-rose-600/80 pb-4 relative">
            <div class="text-[11px] sm:text-xs font-serif tracking-[0.35em] text-rose-600 uppercase font-semibold">
              高校实验室与仪器设备安全管理工作委员会
            </div>
            <h1 class="text-xl sm:text-2xl font-bold font-serif tracking-widest text-rose-600">
              {{ notice.title }}
            </h1>
            <div class="flex items-center justify-between text-[11px] font-mono pt-1 print:text-black" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">
              <span>字号：<strong>{{ notice.doc_code }}</strong></span>
              <span>签发日期：<strong>{{ notice.issued_at }}</strong></span>
            </div>
          </div>

          <!-- 4.2 主送受文对象 -->
          <div class="text-xs sm:text-sm font-medium flex items-center space-x-2">
            <span class="print:text-black" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">主送单位/主送人：</span>
            <span class="font-bold underline decoration-rose-500/50 underline-offset-4 print:text-black" :class="theme === 'light' ? 'text-indigo-600' : 'text-indigo-400'">
              {{ notice.recipient }}
            </span>
          </div>

          <!-- 4.3 催告正文导言 -->
          <p class="text-xs leading-relaxed print:text-zinc-800 indent-6" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
            经机房资产全周期物联网智能感知系统核验，由贵方于
            <span class="font-mono font-semibold print:text-black" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'">{{ notice.borrow_log?.borrow_time }}</span>
            借调登记领用的实验仪器设备，已超过既定约定归还日期
            （<span class="font-mono font-semibold text-rose-500 print:text-black">{{ notice.borrow_log?.expected_return_time }}</span>），
            当前已累计超期占用达
            <span class="font-mono font-bold text-rose-500 text-sm px-1 underline">{{ notice.overdue_days }}</span> 天。
            为保证实验室日常实践教学与重大科研算力资源的合理有序流转，特签发此催告通知单：
          </p>

          <!-- 4.4 超期借用设备核验档案表格 -->
          <div class="rounded-xl border overflow-hidden" :class="theme === 'light' ? 'border-slate-200' : 'border-white/[0.1]'">
            <div class="bg-rose-500/10 px-3 py-1.5 text-xs font-semibold text-rose-400 flex items-center justify-between border-b" :class="theme === 'light' ? 'border-slate-200' : 'border-white/[0.08]'">
              <span class="flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                超期借用设备核验档案
              </span>
              <span class="text-[10px] font-mono print:text-black" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">
                流水号: {{ notice.borrow_log?.log_no }}
              </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 text-xs divide-y sm:divide-y-0 sm:divide-x" :class="theme === 'light' ? 'divide-slate-200' : 'divide-white/[0.08]'">
              <!-- 左侧列 -->
              <div class="p-3 space-y-2">
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">设备唯一编号</span>
                  <span class="font-mono font-semibold print:text-black" :class="theme === 'light' ? 'text-cyan-600' : 'text-cyan-400'">{{ notice.asset?.asset_no }}</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">设备官方名称</span>
                  <span class="font-medium print:text-black" :class="theme === 'light' ? 'text-slate-800' : 'text-zinc-200'">{{ notice.asset?.name }}</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">厂商品牌型号</span>
                  <span class="print:text-black" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'">{{ notice.asset?.brand }} {{ notice.asset?.model_name }}</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">原归属机房位置</span>
                  <span class="print:text-black" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'">{{ notice.asset?.location }}</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">带外/管理 IP</span>
                  <span class="font-mono print:text-black" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'">{{ notice.asset?.management_ip || 'DHCP' }}</span>
                </div>
              </div>

              <!-- 右侧列 -->
              <div class="p-3 space-y-2">
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">借调责任教师</span>
                  <span class="font-semibold print:text-black" :class="theme === 'light' ? 'text-amber-700' : 'text-amber-300'">{{ notice.borrower?.name }} ({{ notice.borrower?.department }})</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">登记借用用途</span>
                  <span class="truncate max-w-[200px] print:text-black" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'" :title="notice.borrow_log?.purpose">{{ notice.borrow_log?.purpose }}</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">原出库登记时间</span>
                  <span class="font-mono print:text-black" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'">{{ notice.borrow_log?.borrow_time }}</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">既定约定归还</span>
                  <span class="font-mono text-rose-500 print:text-black font-semibold">{{ notice.borrow_log?.expected_return_time }}</span>
                </div>
                <div class="flex justify-between">
                  <span :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">累计超期天数</span>
                  <span class="font-mono font-bold text-rose-500">⚠️ {{ notice.overdue_days }} 天</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 4.5 管理规章条例与限期处置要求 -->
          <div class="space-y-3">
            <h4 class="text-xs font-semibold tracking-wide flex items-center gap-1.5" :class="theme === 'light' ? 'text-slate-800' : 'text-zinc-200'">
              <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
              管理规章溯源与处置闭环规程
            </h4>

            <div class="space-y-2">
              <div
                v-for="(r, idx) in notice.regulations"
                :key="idx"
                class="p-3 rounded-xl border text-xs leading-relaxed"
                :class="theme === 'light' ? 'bg-slate-50 border-slate-200 text-slate-700' : 'bg-white/[0.02] border-white/[0.08] text-zinc-300'"
              >
                <div class="font-semibold text-rose-500 print:text-black mb-1 flex items-center gap-1">
                  <span>§</span> {{ r.clause }}
                </div>
                <p class="text-[11px] print:text-zinc-800" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">{{ r.content }}</p>
              </div>
            </div>

            <!-- 处置要求清单 -->
            <div
              class="p-3.5 rounded-xl border space-y-2 text-xs"
              :class="theme === 'light' ? 'bg-amber-50/60 border-amber-200 text-amber-900' : 'bg-amber-950/20 border-amber-500/30 text-amber-200'"
            >
              <div class="font-semibold flex items-center gap-1.5 text-amber-500 print:text-black">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                催告闭环指令要求：
              </div>
              <ol class="list-decimal list-inside space-y-1 text-[11px] leading-relaxed pl-1 print:text-black" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                <li>
                  <strong>限期归还或续借：</strong>请借用人于
                  <span class="font-mono underline font-semibold text-rose-500 print:text-black">{{ notice.deadline }}</span>
                  前（3个工作日内），将设备完好送还归属机房办理交接，或于系统补办延期审批。
                </li>
                <li>
                  <strong>设备健康核验：</strong>归还入库时需由机房主管对散热、外观、计算卡参数及系统日志执行完整性安全验收。
                </li>
                <li>
                  <strong>安全履职问责：</strong>逾期未处置且未说明正当理由者，系统将按规程暂停借调权限并通报教研室安全负责人。
                </li>
              </ol>
            </div>
          </div>

          <!-- 4.6 签发落款与公章仿真水印 -->
          <div class="pt-4 flex justify-between items-end relative min-h-[90px]">
            <div class="text-[11px] space-y-0.5 print:text-zinc-700" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-500'">
              <div>催办联系电话：010-82600380 / 内线 8021</div>
              <div>借用验收专管员：{{ notice.borrow_log?.approver || '王主管' }}</div>
            </div>

            <div class="text-right space-y-1 relative pr-4">
              <div class="text-xs font-semibold print:text-black" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-200'">
                {{ notice.issuer }}
              </div>
              <div class="font-mono text-xs print:text-black" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">
                {{ notice.issued_at }}
              </div>

              <!-- 仿真拟真红头印章印记 (Official Stamp) -->
              <div
                class="absolute right-0 bottom-[-10px] w-24 h-24 rounded-full border-2 border-rose-600/70 flex flex-col items-center justify-center pointer-events-none rotate-[-12deg] select-none opacity-85 print:opacity-100"
              >
                <div class="text-[8px] text-rose-600 font-serif font-bold text-center leading-tight px-1">
                  高校实验室与设备管理处
                </div>
                <div class="text-rose-600 text-[10px] my-0.5">★</div>
                <div class="text-[8px] text-rose-600 font-serif font-bold tracking-widest">
                  公文签发章
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. 底部操作栏 (AI 对话联动催办) -->
        <div
          v-if="notice"
          class="border-t px-5 py-3 shrink-0 flex flex-col sm:flex-row items-center justify-between gap-2.5 print:hidden"
          :class="theme === 'light' ? 'border-slate-200 bg-slate-50/90' : 'border-white/[0.08] bg-zinc-950'"
        >
          <div class="text-[11px] flex items-center space-x-1" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>合规公文已同步至资产全生命周期时序履历底座</span>
          </div>

          <div class="flex items-center space-x-2 w-full sm:w-auto justify-end">
            <!-- 核心交互：管理员向李老师发送催办通知 -->
            <button
              v-if="!currentUser || currentUser.role === 'ADMIN'"
              @click="triggerAgentUrge"
              :disabled="sendingUrge"
              class="px-3.5 py-1.5 rounded-xl text-xs font-medium bg-gradient-to-r from-rose-500/20 to-indigo-500/20 hover:from-rose-500/30 hover:to-indigo-500/30 text-rose-300 hover:text-rose-200 border border-rose-500/30 hover:border-rose-500/50 flex items-center space-x-1.5 transition-all shadow-sm active:scale-95 disabled:opacity-50"
              title="向借调教师下发站内超期催还待办通知并联动 AI 对话流起草公文"
            >
              <svg v-if="sendingUrge" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-3.5 h-3.5 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span>{{ sendingUrge ? '下发中...' : '向李老师发送催办通知' }}</span>
            </button>

            <!-- 教师角色查看公文：一键办理设备归还登记 -->
            <button
              v-else-if="currentUser?.role === 'TEACHER'"
              @click="triggerTeacherReturn"
              class="px-3.5 py-1.5 rounded-xl text-xs font-medium bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 hover:text-emerald-200 border border-emerald-500/30 hover:border-emerald-500/50 flex items-center space-x-1.5 transition-all shadow-sm active:scale-95"
              title="前往机房或呼叫 AI 协助办理该设备的归还验收登记"
            >
              <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>办理设备归还登记</span>
            </button>

            <!-- 学生角色：只读说明 -->
            <div
              v-else
              class="px-3 py-1 rounded-lg text-[11px] text-zinc-500 font-mono"
            >
              只读查阅模式
            </div>

            <button
              @click="close"
              class="px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors"
              :class="theme === 'light' ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300' : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border-white/[0.1]'"
            >
              关闭
            </button>
          </div>
        </div>

        <!-- 催办成功 Toast 提醒 -->
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div
            v-if="toastMessage"
            class="absolute top-16 left-1/2 -translate-x-1/2 z-[70] px-4 py-2 rounded-xl text-xs font-medium border bg-emerald-500/90 text-white border-emerald-400/50 shadow-2xl backdrop-blur-md flex items-center gap-2 pointer-events-none"
          >
            <svg class="w-4 h-4 text-white shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
            </svg>
            <span>{{ toastMessage }}</span>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  assetNo: {
    type: String,
    default: '',
  },
  theme: {
    type: String,
    default: 'dark',
  },
  initialNotice: {
    type: Object,
    default: null,
  },
  currentUser: {
    type: Object,
    default: () => ({ role: 'ADMIN', username: 'admin' }),
  },
})

const emit = defineEmits(['update:modelValue', 'promptAgent', 'urgeSent'])

const notice = ref(props.initialNotice)
const loading = ref(false)
const errorMessage = ref('')
const copied = ref(false)
const sendingUrge = ref(false)
const toastMessage = ref('')

async function fetchNotice(assetNo) {
  if (!assetNo) return
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await api.getOverdueNotice(assetNo)
    notice.value = data
  } catch (err) {
    console.error('获取超期催告通知失败:', err)
    errorMessage.value = err.message || '获取超期催告通知失败'
    notice.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      copied.value = false
      errorMessage.value = ''
      if (props.assetNo) {
        fetchNotice(props.assetNo)
      }
    } else {
      notice.value = null
      errorMessage.value = ''
    }
  }
)

watch(
  () => props.assetNo,
  (newNo) => {
    if (props.modelValue && newNo) {
      fetchNotice(newNo)
    }
  }
)

function close() {
  emit('update:modelValue', false)
}

async function copyNoticeContent() {
  const content = notice.value?.markdown_content || ''
  if (!content) return
  try {
    await navigator.clipboard.writeText(content)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2500)
  } catch (e) {
    // 回退方案
    const ta = document.createElement('textarea')
    ta.value = content
    ta.style.position = 'fixed'
    ta.style.left = '-9999px'
    ta.style.top = '-9999px'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2500)
  }
}

function printNotice() {
  window.print()
}

function triggerTeacherReturn() {
  const targetNo = notice.value?.asset?.asset_no || props.assetNo || 'DEV-SRV-201'
  close()
  emit('promptAgent', `办理设备 ${targetNo} 的归还登记`)
}

async function triggerAgentUrge() {
  if (sendingUrge.value) return
  const targetNo = notice.value?.asset?.asset_no || props.assetNo || 'DEV-SRV-201'
  sendingUrge.value = true
  try {
    await api.sendOverdueUrge(targetNo, '管理员通过催告公文系统直接下发限期归还催办待办')
    toastMessage.value = '已向借调人李老师 (teacher_li) 成功下发超期催还待办通知！'
    emit('urgeSent', targetNo)
    setTimeout(() => {
      toastMessage.value = ''
    }, 3500)
  } catch (err) {
    console.error('发送催办通知失败:', err)
  } finally {
    sendingUrge.value = false
  }

  const promptText = `请为设备 ${targetNo} 生成超期归还催告单并出具公文`
  emit('promptAgent', promptText)
}
</script>

<style scoped>
@media print {
  @page {
    size: A4 portrait;
    margin: 15mm;
  }
  body * {
    visibility: hidden;
  }
  #printable-overdue-notice,
  #printable-overdue-notice * {
    visibility: visible;
  }
  #printable-overdue-notice {
    position: absolute;
    left: 0;
    top: 0;
    width: 100% !important;
    max-width: 100% !important;
    background: white !important;
    color: black !important;
    border: none !important;
    box-shadow: none !important;
    padding: 10mm 15mm !important;
    break-inside: avoid;
    page-break-inside: avoid;
  }
}
</style>
