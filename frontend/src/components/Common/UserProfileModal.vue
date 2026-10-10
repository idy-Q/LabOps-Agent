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
      <!-- 全屏微光高斯模糊遮罩 -->
      <div
        v-if="modelValue"
        @keydown.esc.window="close"
        class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-hidden transition-colors select-none"
        :class="effectiveTheme === 'light' ? 'bg-slate-900/40 backdrop-blur-sm' : 'bg-black/80 backdrop-blur-md'"
        @click.self="close"
      >
        <!-- 微光磨砂玻璃卡片 -->
        <div
          class="user-profile-modal-card w-full max-w-lg rounded-2xl sm:rounded-3xl border flex flex-col max-h-[92vh] overflow-hidden transition-all shadow-2xl select-text font-sans"
          :class="[
            effectiveTheme === 'light'
              ? 'bg-white/98 border-slate-200 shadow-[0_25px_60px_-15px_rgba(15,23,42,0.15)] text-slate-800'
              : 'bg-zinc-950/95 border-white/[0.12] shadow-black/80 text-zinc-100'
          ]"
        >
          <!-- 1. 弹窗顶部栏 -->
          <div
            class="flex items-center justify-between border-b px-5 py-3.5 shrink-0"
            :class="effectiveTheme === 'light' ? 'border-slate-200 bg-slate-50/90' : 'border-white/[0.08] bg-white/[0.02]'"
          >
            <div class="flex items-center space-x-2.5 min-w-0">
              <span
                class="p-1.5 rounded-xl border shrink-0 shadow-sm"
                :class="[
                  profile?.is_system_agent
                    ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                    : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                ]"
              >
                <!-- AI 或 人员图标 -->
                <svg v-if="profile?.is_system_agent" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </span>
              <div>
                <h3 class="text-sm font-semibold tracking-tight flex items-center gap-2">
                  <span>
                    {{
                      profile?.is_system_agent
                        ? 'AI 自治智能体专属档案'
                        : activeTab === 'edit_profile'
                          ? '编辑个人档案资料'
                          : activeTab === 'change_password'
                            ? '修改登录访问密码'
                            : (isMe ? '我的个人全景档案' : '工单处置人员全景档案')
                    }}
                  </span>
                  <span
                    class="text-[10px] px-2 py-0.5 rounded font-mono border"
                    :class="effectiveTheme === 'light' ? 'bg-slate-200/80 text-slate-700 border-slate-300' : 'bg-zinc-900 text-zinc-400 border-white/[0.08]'"
                  >
                    {{ profile?.is_system_agent ? 'Autonomous Agent' : (isMe ? 'Current User' : 'Audited Operator') }}
                  </span>
                </h3>
              </div>
            </div>

            <!-- 关闭按钮 -->
            <button
              @click="close"
              class="p-1.5 rounded-lg transition-colors"
              :class="effectiveTheme === 'light' ? 'text-slate-400 hover:text-slate-700 hover:bg-slate-100' : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.08]'"
              title="关闭 (Esc)"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- 模式切换 Tab 栏 (仅本人登录且非 AI 智能体时显示) -->
          <div
            v-if="isMe"
            class="flex items-center space-x-1.5 px-5 py-2.5 border-b text-xs shrink-0 select-none"
            :class="effectiveTheme === 'light' ? 'bg-slate-100/70 border-slate-200' : 'bg-zinc-900/50 border-white/[0.06]'"
          >
            <button
              @click="activeTab = 'view'"
              type="button"
              class="flex-1 py-1.5 px-3 rounded-xl font-medium transition-all flex items-center justify-center space-x-1.5"
              :class="[
                activeTab === 'view'
                  ? (effectiveTheme === 'light'
                      ? 'bg-white text-indigo-600 shadow-sm font-semibold border border-slate-200'
                      : 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]')
                  : (effectiveTheme === 'light'
                      ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]')
              ]"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>全景档案</span>
            </button>

            <button
              @click="activeTab = 'edit_profile'"
              type="button"
              class="flex-1 py-1.5 px-3 rounded-xl font-medium transition-all flex items-center justify-center space-x-1.5"
              :class="[
                activeTab === 'edit_profile'
                  ? (effectiveTheme === 'light'
                      ? 'bg-white text-indigo-600 shadow-sm font-semibold border border-slate-200'
                      : 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]')
                  : (effectiveTheme === 'light'
                      ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]')
              ]"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>编辑资料</span>
            </button>

            <button
              @click="activeTab = 'change_password'"
              type="button"
              class="flex-1 py-1.5 px-3 rounded-xl font-medium transition-all flex items-center justify-center space-x-1.5"
              :class="[
                activeTab === 'change_password'
                  ? (effectiveTheme === 'light'
                      ? 'bg-white text-indigo-600 shadow-sm font-semibold border border-slate-200'
                      : 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]')
                  : (effectiveTheme === 'light'
                      ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]')
              ]"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              <span>修改密码</span>
            </button>
          </div>

          <!-- 2. 内容主体区 (可滚动) -->
          <div class="p-5 overflow-y-auto space-y-4">
            <!-- 加载骨架屏 -->
            <div v-if="loading" class="animate-pulse space-y-4 py-4">
              <div class="flex items-center space-x-4">
                <div class="w-16 h-16 rounded-2xl bg-zinc-800"></div>
                <div class="space-y-2 flex-1">
                  <div class="h-5 bg-zinc-800 rounded w-1/3"></div>
                  <div class="h-4 bg-zinc-800 rounded w-1/2"></div>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-3 pt-2">
                <div class="h-16 bg-zinc-800 rounded-xl"></div>
                <div class="h-16 bg-zinc-800 rounded-xl"></div>
              </div>
            </div>

            <template v-else-if="profile">
              <!-- Tab 1: 全景档案视图 -->
              <div v-if="activeTab === 'view'" class="space-y-4 animate-fade-in">
                <!-- 人物头部 Hero 区 -->
                <div
                  class="p-4 rounded-2xl border flex items-center justify-between gap-4 relative overflow-hidden shadow-sm"
                  :class="[
                    effectiveTheme === 'light'
                      ? 'bg-slate-50 border-slate-200/90'
                      : 'bg-black/30 border-white/[0.08]'
                  ]"
                >
                  <!-- 头像与核心标识 -->
                  <div class="flex items-center space-x-3.5 min-w-0">
                    <!-- 头像徽章 -->
                    <div class="relative shrink-0">
                      <div
                        class="w-14 h-14 rounded-2xl flex items-center justify-center text-xl font-black text-white shadow-lg border border-white/20 select-none"
                        :class="avatarClass"
                      >
                        <template v-if="profile.is_system_agent">
                          <!-- AI 芯片/机器人矢量徽标 -->
                          <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        </template>
                        <template v-else>
                          {{ profile.avatar_text || profile.real_name?.slice(0, 1) || '运' }}
                        </template>
                      </div>

                      <!-- 状态绿点呼吸灯 -->
                      <span
                        class="absolute -bottom-1 -right-1 flex h-4 w-4"
                        :title="profile.status"
                      >
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span
                          class="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border-2"
                          :class="effectiveTheme === 'light' ? 'border-white' : 'border-zinc-950'"
                        ></span>
                      </span>
                    </div>

                    <!-- 姓名与工号/识别码 -->
                    <div class="min-w-0 space-y-1">
                      <div class="flex items-center space-x-2 flex-wrap gap-y-1">
                        <span class="font-bold text-base tracking-tight truncate">{{ profile.real_name }}</span>
                        <span
                          class="px-2 py-0.5 rounded-md text-[11px] font-mono border font-medium whitespace-nowrap"
                          :class="roleBadgeClass"
                        >
                          {{ profile.role_label }}
                        </span>
                      </div>

                      <div
                        class="flex items-center space-x-2 text-xs font-mono"
                        :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                      >
                        <span>{{ profile.is_system_agent ? '主体识别码:' : '工号/学号:' }}</span>
                        <span
                          class="font-semibold select-all"
                          :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-200'"
                        >
                          {{ profile.username }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- 运行状态标签 -->
                  <div class="hidden sm:flex flex-col items-end shrink-0">
                    <span
                      class="px-2.5 py-0.5 rounded-full text-[10px] font-mono border font-medium flex items-center space-x-1 shadow-sm"
                      :class="[
                        profile.is_system_agent
                          ? (effectiveTheme === 'light'
                              ? 'bg-cyan-50 text-cyan-700 border-cyan-200'
                              : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30')
                          : (effectiveTheme === 'light'
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30')
                      ]"
                    >
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                      <span>{{ profile.status }}</span>
                    </span>
                  </div>
                </div>

                <!-- 4 项基础档案卡片 Grid -->
                <div class="grid grid-cols-2 gap-2.5 text-xs">
                  <!-- 所属部门/教研室 -->
                  <div
                    class="p-3 rounded-xl border space-y-1 shadow-sm"
                    :class="effectiveTheme === 'light' ? 'bg-white border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.03)]' : 'bg-black/20 border-white/[0.06]'"
                  >
                    <div
                      class="text-[11px] flex items-center space-x-1"
                      :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                    >
                      <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                      </svg>
                      <span>所属部门/教研室</span>
                    </div>
                    <div class="font-medium truncate" :class="effectiveTheme === 'light' ? 'text-slate-900' : 'text-zinc-100'" :title="profile.department">{{ profile.department }}</div>
                  </div>

                  <!-- 联系电话 / 内部总线 -->
                  <div
                    class="p-3 rounded-xl border space-y-1 shadow-sm"
                    :class="effectiveTheme === 'light' ? 'bg-white border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.03)]' : 'bg-black/20 border-white/[0.06]'"
                  >
                    <div
                      class="text-[11px] flex items-center justify-between"
                      :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                    >
                      <span class="flex items-center space-x-1">
                        <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                        <span>联系方式</span>
                      </span>
                      <!-- 复制电话按钮 -->
                      <button
                        v-if="profile.phone && !profile.phone.includes('暂') && !profile.is_system_agent"
                        @click="copyPhone"
                        class="text-[10px] font-mono transition-colors"
                        :class="effectiveTheme === 'light' ? 'text-indigo-600 hover:text-indigo-800' : 'text-indigo-400 hover:text-indigo-300'"
                        title="点击复制电话号码"
                      >
                        {{ copiedPhone ? '已复制✓' : '复制' }}
                      </button>
                    </div>
                    <div class="font-mono font-medium truncate" :class="effectiveTheme === 'light' ? 'text-slate-900' : 'text-zinc-100'" :title="profile.phone">
                      {{ profile.phone || '暂未登记' }}
                    </div>
                  </div>

                  <!-- 主体属性类别 -->
                  <div
                    class="p-3 rounded-xl border space-y-1 shadow-sm"
                    :class="effectiveTheme === 'light' ? 'bg-white border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.03)]' : 'bg-black/20 border-white/[0.06]'"
                  >
                    <div
                      class="text-[11px] flex items-center space-x-1"
                      :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                    >
                      <svg class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>主体类别</span>
                    </div>
                    <div class="font-medium truncate" :class="effectiveTheme === 'light' ? 'text-slate-900' : 'text-zinc-100'">
                      {{ profile.is_system_agent ? 'AI 智能体 (ReAct+RAG)' : '高校实训认证主体' }}
                    </div>
                  </div>

                  <!-- 登记/投产时间 -->
                  <div
                    class="p-3 rounded-xl border space-y-1 shadow-sm"
                    :class="effectiveTheme === 'light' ? 'bg-white border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.03)]' : 'bg-black/20 border-white/[0.06]'"
                  >
                    <div
                      class="text-[11px] flex items-center space-x-1"
                      :class="effectiveTheme === 'light' ? 'text-slate-500' : 'text-zinc-400'"
                    >
                      <svg class="w-3.5 h-3.5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>上线/登记时间</span>
                    </div>
                    <div class="font-mono truncate" :class="effectiveTheme === 'light' ? 'text-slate-800' : 'text-zinc-200'" :title="profile.created_at">
                      {{ profile.created_at || '-' }}
                    </div>
                  </div>
                </div>

                <!-- 当前工单流转环节关联说明 (从时间轴点击进来时) -->
                <div
                  v-if="nodeContext"
                  class="p-3.5 rounded-xl border text-xs space-y-1.5 shadow-sm"
                  :class="[
                    effectiveTheme === 'light'
                      ? 'bg-amber-50/90 border-amber-200 text-amber-950 shadow-sm'
                      : 'bg-amber-500/[0.06] border-amber-500/20 text-amber-200'
                  ]"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-1.5 font-semibold" :class="effectiveTheme === 'light' ? 'text-amber-900' : 'text-amber-300'">
                      <svg class="w-3.5 h-3.5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>本工单流转环节协同记录</span>
                    </div>
                    <span
                      v-if="nodeContext.duration_from_start"
                      class="text-[10px] font-mono px-2 py-0.5 rounded-full border"
                      :class="effectiveTheme === 'light' ? 'bg-amber-100 text-amber-800 border-amber-200' : 'bg-amber-950/80 text-amber-300 border-amber-500/30'"
                    >
                      {{ nodeContext.duration_from_start }}
                    </span>
                  </div>
                  <div class="text-[11px]" :class="effectiveTheme === 'light' ? 'text-amber-900/90' : 'opacity-90'">
                    <span class="font-medium">流转节点：</span>{{ nodeContext.title }}
                  </div>
                  <div v-if="nodeContext.comment" class="text-[11px] whitespace-pre-line" :class="effectiveTheme === 'light' ? 'text-amber-900/80' : 'opacity-80'">
                    <span class="font-medium">处置批注：</span>{{ nodeContext.comment }}
                  </div>
                  <div v-if="nodeContext.timestamp" class="text-[10px] font-mono" :class="effectiveTheme === 'light' ? 'text-amber-800/70' : 'opacity-70'">
                    发生时间：{{ nodeContext.timestamp }}
                  </div>
                </div>

                <!-- 权责范围与能力清单 -->
                <div
                  class="p-3.5 rounded-xl border space-y-2 shadow-sm"
                  :class="effectiveTheme === 'light' ? 'bg-white border-slate-200/90 shadow-[0_1px_3px_rgba(0,0,0,0.03)]' : 'bg-black/20 border-white/[0.06]'"
                >
                  <div class="text-xs font-semibold flex items-center space-x-1.5" :class="effectiveTheme === 'light' ? 'text-slate-900' : 'text-zinc-200'">
                    <svg class="w-3.5 h-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    <span>{{ profile.is_system_agent ? '智能体机房自治权责与能力' : '机房运维与流程处置权责' }}</span>
                  </div>

                  <ul class="space-y-1.5 text-xs">
                    <li
                      v-for="(item, idx) in profile.responsibilities"
                      :key="idx"
                      class="flex items-start space-x-2 text-[11px] leading-relaxed"
                      :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                    >
                      <span :class="effectiveTheme === 'light' ? 'text-indigo-600 font-bold' : 'text-indigo-400'" class="shrink-0 select-none">✓</span>
                      <span>{{ item }}</span>
                    </li>
                  </ul>
                </div>

                <!-- 简介说明 -->
                <div
                  v-if="profile.description"
                  class="p-3 rounded-xl border text-[11px] leading-relaxed"
                  :class="effectiveTheme === 'light' ? 'bg-slate-50 border-slate-200/80 text-slate-600' : 'bg-zinc-900/60 border-white/[0.04] text-zinc-400'"
                >
                  {{ profile.description }}
                </div>
              </div>

              <!-- Tab 2: 编辑个人档案资料 -->
              <div v-else-if="activeTab === 'edit_profile'" class="space-y-4 animate-fade-in">
                <!-- 提示说明条 -->
                <div
                  class="p-3 rounded-xl border text-xs flex items-center space-x-2.5"
                  :class="effectiveTheme === 'light' ? 'bg-indigo-50/80 border-indigo-200/80 text-indigo-900' : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300'"
                >
                  <svg class="w-4 h-4 shrink-0 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>修改个人信息后，真实姓名和所属部门将即时同步至工单流转环节与全局日志审计台账中。</span>
                </div>

                <!-- 成功/错误反馈横幅 -->
                <div
                  v-if="editSuccess"
                  class="p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2 animate-fade-in"
                >
                  <svg class="w-4 h-4 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>{{ editSuccess }}</span>
                </div>
                <div
                  v-if="editError"
                  class="p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2 animate-fade-in"
                >
                  <svg class="w-4 h-4 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{{ editError }}</span>
                </div>

                <form @submit.prevent="handleSaveProfile" class="space-y-3.5 text-xs">
                  <!-- 登录账号 (只读锁定) -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      系统登录账号 (工号/学号)
                    </label>
                    <input
                      type="text"
                      :value="profile.username"
                      disabled
                      class="w-full px-3 py-2 rounded-xl border text-xs font-mono cursor-not-allowed opacity-80"
                      :class="effectiveTheme === 'light' ? 'bg-slate-100 border-slate-300 text-slate-500' : 'bg-zinc-900 border-white/[0.08] text-zinc-400'"
                    />
                    <p class="text-[10px] text-zinc-500">登录账号为系统唯一身份主键，不可更改。</p>
                  </div>

                  <!-- 真实姓名 -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      真实姓名 <span class="text-rose-400">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="editForm.real_name"
                      required
                      placeholder="请输入真实姓名"
                      class="w-full px-3 py-2 rounded-xl border text-xs outline-none transition-all"
                      :class="[
                        effectiveTheme === 'light'
                          ? 'bg-white border-slate-300 text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                          : 'bg-zinc-900/80 border-white/[0.12] text-zinc-100 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                      ]"
                    />
                  </div>

                  <!-- 所属部门/教研室 -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      所属部门 / 教研室 / 班级
                    </label>
                    <input
                      type="text"
                      v-model="editForm.department"
                      placeholder="例如：网络中心运维部 / 计算机学院"
                      class="w-full px-3 py-2 rounded-xl border text-xs outline-none transition-all"
                      :class="[
                        effectiveTheme === 'light'
                          ? 'bg-white border-slate-300 text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                          : 'bg-zinc-900/80 border-white/[0.12] text-zinc-100 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                      ]"
                    />
                  </div>

                  <!-- 联系电话 -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      联系电话 / 手机号
                    </label>
                    <input
                      type="tel"
                      v-model="editForm.phone"
                      placeholder="例如：13800000001"
                      class="w-full px-3 py-2 rounded-xl border text-xs font-mono outline-none transition-all"
                      :class="[
                        effectiveTheme === 'light'
                          ? 'bg-white border-slate-300 text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                          : 'bg-zinc-900/80 border-white/[0.12] text-zinc-100 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                      ]"
                    />
                  </div>

                  <!-- 当前分配角色 (只读) -->
                  <div class="space-y-1 pt-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      所属运维权责角色
                    </label>
                    <div class="flex items-center space-x-2">
                      <span
                        class="px-2.5 py-1 rounded-lg text-xs font-mono font-medium border"
                        :class="roleBadgeClass"
                      >
                        {{ profile.role_label }} [{{ profile.role }}]
                      </span>
                      <span class="text-[11px] text-zinc-500">角色权责由系统根据实训组织架构分配。</span>
                    </div>
                  </div>
                </form>
              </div>

              <!-- Tab 3: 修改登录密码 -->
              <div v-else-if="activeTab === 'change_password'" class="space-y-4 animate-fade-in">
                <!-- 提示说明条 -->
                <div
                  class="p-3 rounded-xl border text-xs flex items-center space-x-2.5"
                  :class="effectiveTheme === 'light' ? 'bg-amber-50/80 border-amber-200/80 text-amber-900' : 'bg-amber-500/10 border-amber-500/20 text-amber-300'"
                >
                  <svg class="w-4 h-4 shrink-0 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>密码修改成功后即时生效，下次使用工号登录时请使用新密码。</span>
                </div>

                <!-- 成功/错误反馈横幅 -->
                <div
                  v-if="passwordSuccess"
                  class="p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center space-x-2 animate-fade-in"
                >
                  <svg class="w-4 h-4 shrink-0 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  <span>{{ passwordSuccess }}</span>
                </div>
                <div
                  v-if="passwordError"
                  class="p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2 animate-fade-in"
                >
                  <svg class="w-4 h-4 shrink-0 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{{ passwordError }}</span>
                </div>

                <form @submit.prevent="handleChangePassword" class="space-y-3.5 text-xs">
                  <!-- 账号信息 (锁定) -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      登录账号 (工号)
                    </label>
                    <input
                      type="text"
                      :value="profile.username"
                      disabled
                      class="w-full px-3 py-2 rounded-xl border text-xs font-mono cursor-not-allowed opacity-80"
                      :class="effectiveTheme === 'light' ? 'bg-slate-100 border-slate-300 text-slate-500' : 'bg-zinc-900 border-white/[0.08] text-zinc-400'"
                    />
                  </div>

                  <!-- 原登录密码 -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      当前旧密码 <span class="text-rose-400">*</span>
                    </label>
                    <input
                      type="password"
                      v-model="passwordForm.old_password"
                      required
                      placeholder="请输入当前正在使用的密码"
                      autocomplete="current-password"
                      class="w-full px-3 py-2 rounded-xl border text-xs outline-none transition-all font-mono"
                      :class="[
                        effectiveTheme === 'light'
                          ? 'bg-white border-slate-300 text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                          : 'bg-zinc-900/80 border-white/[0.12] text-zinc-100 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                      ]"
                    />
                  </div>

                  <!-- 新登录密码 -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      新登录密码 <span class="text-rose-400">*</span>
                    </label>
                    <input
                      type="password"
                      v-model="passwordForm.new_password"
                      required
                      minlength="6"
                      placeholder="请输入新密码（至少 6 位字符）"
                      autocomplete="new-password"
                      class="w-full px-3 py-2 rounded-xl border text-xs outline-none transition-all font-mono"
                      :class="[
                        effectiveTheme === 'light'
                          ? 'bg-white border-slate-300 text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                          : 'bg-zinc-900/80 border-white/[0.12] text-zinc-100 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                      ]"
                    />
                  </div>

                  <!-- 确认新密码 -->
                  <div class="space-y-1">
                    <label class="block font-medium" :class="effectiveTheme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
                      再次输入新密码 <span class="text-rose-400">*</span>
                    </label>
                    <input
                      type="password"
                      v-model="passwordForm.confirm_password"
                      required
                      minlength="6"
                      placeholder="请再次输入新密码"
                      autocomplete="new-password"
                      class="w-full px-3 py-2 rounded-xl border text-xs outline-none transition-all font-mono"
                      :class="[
                        effectiveTheme === 'light'
                          ? 'bg-white border-slate-300 text-slate-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                          : 'bg-zinc-900/80 border-white/[0.12] text-zinc-100 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500'
                      ]"
                    />
                  </div>
                </form>
              </div>
            </template>
          </div>

          <!-- 3. 底部操作栏 -->
          <div
            class="flex items-center justify-between border-t px-5 py-3 shrink-0"
            :class="effectiveTheme === 'light' ? 'border-slate-200 bg-slate-50/80' : 'border-white/[0.08] bg-white/[0.02]'"
          >
            <!-- 视图模式下的底部按钮 -->
            <template v-if="activeTab === 'view'">
              <button
                @click="copyProfileSummary"
                class="px-3 py-1.5 rounded-xl border text-xs font-mono flex items-center space-x-1.5 transition-all active:scale-95 shadow-sm"
                :class="[
                  effectiveTheme === 'light'
                    ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300'
                    : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border-white/[0.1]'
                ]"
              >
                <svg class="w-3.5 h-3.5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                <span>{{ copiedSummary ? '档案已复制 ✓' : '复制档案概要' }}</span>
              </button>

              <button
                @click="close"
                class="px-4 py-1.5 rounded-xl text-xs font-medium transition-all active:scale-95 shadow-sm"
                :class="[
                  effectiveTheme === 'light'
                    ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                    : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                ]"
              >
                完成
              </button>
            </template>

            <!-- 编辑资料模式下的底部按钮 -->
            <template v-else-if="activeTab === 'edit_profile'">
              <button
                @click="activeTab = 'view'"
                type="button"
                class="px-3.5 py-1.5 rounded-xl border text-xs transition-all active:scale-95"
                :class="effectiveTheme === 'light' ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300' : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border-white/[0.1]'"
              >
                返回档案
              </button>

              <button
                @click="handleSaveProfile"
                :disabled="editSaving"
                type="button"
                class="px-4 py-1.5 rounded-xl text-xs font-medium transition-all active:scale-95 shadow-sm flex items-center space-x-1.5"
                :class="[
                  editSaving
                    ? 'opacity-60 cursor-not-allowed bg-indigo-600 text-white'
                    : effectiveTheme === 'light'
                      ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                ]"
              >
                <svg v-if="editSaving" class="animate-spin w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>{{ editSaving ? '保存中...' : '保存修改' }}</span>
              </button>
            </template>

            <!-- 修改密码模式下的底部按钮 -->
            <template v-else-if="activeTab === 'change_password'">
              <button
                @click="activeTab = 'view'"
                type="button"
                class="px-3.5 py-1.5 rounded-xl border text-xs transition-all active:scale-95"
                :class="effectiveTheme === 'light' ? 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300' : 'bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border-white/[0.1]'"
              >
                返回档案
              </button>

              <button
                @click="handleChangePassword"
                :disabled="passwordSaving"
                type="button"
                class="px-4 py-1.5 rounded-xl text-xs font-medium transition-all active:scale-95 shadow-sm flex items-center space-x-1.5"
                :class="[
                  passwordSaving
                    ? 'opacity-60 cursor-not-allowed bg-amber-600 text-white'
                    : 'bg-amber-600 hover:bg-amber-500 text-white'
                ]"
              >
                <svg v-if="passwordSaving" class="animate-spin w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>{{ passwordSaving ? '提交中...' : '确认修改密码' }}</span>
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  identifier: {
    type: String,
    default: '',
  },
  nodeContext: {
    type: Object,
    default: null,
  },
  currentUser: {
    type: Object,
    default: null,
  },
  theme: {
    type: String,
    default: 'dark',
  },
})

const emit = defineEmits(['update:modelValue', 'userUpdated'])

const loading = ref(false)
const profile = ref(null)
const activeTab = ref('view') // 'view' | 'edit_profile' | 'change_password'

const copiedPhone = ref(false)
const copiedSummary = ref(false)

// 编辑个人资料表单状态
const editForm = ref({
  real_name: '',
  phone: '',
  department: '',
})
const editSaving = ref(false)
const editError = ref('')
const editSuccess = ref('')

// 修改密码表单状态
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
})
const passwordSaving = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

// 判断当前所查看的档案是否是本人（且排除系统 AI 智能体与未登录访客）
const isMe = computed(() => {
  if (!profile.value || profile.value.is_system_agent) return false
  if (!props.currentUser || props.currentUser.username === 'guest') return false
  const myUser = (props.currentUser.username || '').trim().toLowerCase()
  const pUser = (profile.value.username || '').trim().toLowerCase()
  return Boolean(myUser && pUser && myUser === pUser)
})

const effectiveTheme = computed(() => {
  if (props.theme) return props.theme
  return document.documentElement.classList.contains('light') ? 'light' : 'dark'
})

const avatarClass = computed(() => {
  if (profile.value?.is_system_agent) {
    return 'bg-gradient-to-tr from-cyan-600 via-indigo-600 to-sky-500 shadow-cyan-500/20'
  }
  switch (profile.value?.role) {
    case 'ADMIN':
      return 'bg-gradient-to-tr from-rose-600 to-amber-600 shadow-rose-500/20'
    case 'TEACHER':
      return 'bg-gradient-to-tr from-indigo-600 to-blue-500 shadow-indigo-500/20'
    case 'STUDENT':
      return 'bg-gradient-to-tr from-emerald-600 to-teal-500 shadow-emerald-500/20'
    default:
      return 'bg-gradient-to-tr from-purple-600 to-indigo-500 shadow-purple-500/20'
  }
})

const roleBadgeClass = computed(() => {
  const isLight = effectiveTheme.value === 'light'
  if (profile.value?.is_system_agent) {
    return isLight
      ? 'bg-cyan-50 border-cyan-200 text-cyan-700 shadow-sm'
      : 'bg-cyan-500/15 border-cyan-500/30 text-cyan-300'
  }
  switch (profile.value?.role) {
    case 'ADMIN':
      return isLight
        ? 'bg-rose-50 border-rose-200 text-rose-700 shadow-sm'
        : 'bg-rose-500/15 border-rose-500/30 text-rose-300'
    case 'TEACHER':
      return isLight
        ? 'bg-indigo-50 border-indigo-200 text-indigo-700 shadow-sm'
        : 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300'
    case 'STUDENT':
      return isLight
        ? 'bg-emerald-50 border-emerald-200 text-emerald-700 shadow-sm'
        : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
    default:
      return isLight
        ? 'bg-slate-100 border-slate-200 text-slate-700'
        : 'bg-zinc-800 border-white/[0.08] text-zinc-300'
  }
})

// 独立捕获 ESC 事件，阻止冒泡到下层抽屉 (保证多层弹窗平稳关闭)
function onModalKeyDown(e) {
  if (e.key === 'Escape' && props.modelValue) {
    e.stopPropagation()
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onModalKeyDown, true)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onModalKeyDown, true)
})

watch(
  () => [props.modelValue, props.identifier],
  ([visible, id]) => {
    if (visible && id) {
      activeTab.value = 'view'
      editError.value = ''
      editSuccess.value = ''
      passwordError.value = ''
      passwordSuccess.value = ''
      passwordForm.value = {
        old_password: '',
        new_password: '',
        confirm_password: '',
      }
      fetchProfile(id)
    }
  },
  { immediate: true }
)

async function fetchProfile(id) {
  loading.value = true
  copiedPhone.value = false
  copiedSummary.value = false
  editError.value = ''
  editSuccess.value = ''
  passwordError.value = ''
  passwordSuccess.value = ''
  try {
    const data = await api.getUserProfile(id)
    profile.value = data
    editForm.value = {
      real_name: data.real_name || '',
      phone: data.phone && !data.phone.includes('暂') ? data.phone : '',
      department: data.department || '',
    }
  } catch (err) {
    // 降级生成保底档案，绝不让用户看到空屏
    profile.value = {
      username: id,
      real_name: id,
      role: 'OPERATOR',
      role_label: '现场运维人员',
      department: '高校实验实训保障组',
      phone: '暂未登记',
      status: '在线',
      is_system_agent: false,
      avatar_text: id.slice(0, 1),
      responsibilities: ['机房现场运维协同', '设备日常工况记录'],
      description: `流转人员 [${id}] 的历史档案记录`,
      created_at: '协同登记',
    }
    editForm.value = {
      real_name: id,
      phone: '',
      department: '高校实验实训保障组',
    }
  } finally {
    loading.value = false
  }
}

// 保存个人资料修改
async function handleSaveProfile() {
  if (!editForm.value.real_name.trim()) {
    editError.value = '姓名不能为空'
    return
  }
  editSaving.value = true
  editError.value = ''
  editSuccess.value = ''
  try {
    const res = await api.updateUserProfile(profile.value.username, {
      real_name: editForm.value.real_name.trim(),
      phone: editForm.value.phone.trim(),
      department: editForm.value.department.trim(),
    })
    const updated = (res && res.real_name) ? res : (res?.data || {
      real_name: editForm.value.real_name.trim(),
      phone: editForm.value.phone.trim(),
      department: editForm.value.department.trim(),
    })
    profile.value.real_name = updated.real_name
    profile.value.phone = updated.phone
    profile.value.department = updated.department
    if (updated.avatar_text) {
      profile.value.avatar_text = updated.avatar_text
    } else {
      profile.value.avatar_text = updated.real_name.slice(0, 1)
    }
    editSuccess.value = '个人资料更新成功！'
    emit('userUpdated', {
      username: profile.value.username,
      real_name: profile.value.real_name,
      phone: profile.value.phone,
      department: profile.value.department,
      role: profile.value.role,
    })
    setTimeout(() => {
      editSuccess.value = ''
    }, 2500)
  } catch (err) {
    editError.value = err.message || '更新个人资料失败，请重试'
  } finally {
    editSaving.value = false
  }
}

// 提交修改密码
async function handleChangePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''
  if (!passwordForm.value.old_password) {
    passwordError.value = '请输入原密码'
    return
  }
  if (!passwordForm.value.new_password) {
    passwordError.value = '请输入新密码'
    return
  }
  if (passwordForm.value.new_password.length < 6) {
    passwordError.value = '新密码长度至少需 6 位字符'
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = '两次输入的新密码不一致，请仔细核对'
    return
  }
  passwordSaving.value = true
  try {
    const res = await api.changePassword({
      username: profile.value.username,
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    })
    passwordSuccess.value = res.message || '密码修改成功，新密码已生效！'
    passwordForm.value = {
      old_password: '',
      new_password: '',
      confirm_password: '',
    }
    setTimeout(() => {
      passwordSuccess.value = ''
    }, 3000)
  } catch (err) {
    passwordError.value = err.message || '修改密码失败，请检查原密码是否正确'
  } finally {
    passwordSaving.value = false
  }
}

// 跨浏览器及非 HTTPS (高校局域网环境) 复制保底方法
async function copyTextToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch {}
  }
  try {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    const successful = document.execCommand('copy')
    textArea.remove()
    return successful
  } catch {
    return false
  }
}

async function copyPhone() {
  if (!profile.value?.phone || profile.value.phone.includes('暂')) return
  const ok = await copyTextToClipboard(profile.value.phone)
  if (ok) {
    copiedPhone.value = true
    setTimeout(() => {
      copiedPhone.value = false
    }, 2000)
  }
}

async function copyProfileSummary() {
  if (!profile.value) return
  const p = profile.value
  const text = `【LabOps 人员/智能体档案】\n姓名/主体：${p.real_name} (${p.username})\n角色类型：${p.role_label} [${p.role}]\n所属部门：${p.department}\n联系方式：${p.phone || '无'}\n运行状态：${p.status}`
  const ok = await copyTextToClipboard(text)
  if (ok) {
    copiedSummary.value = true
    setTimeout(() => {
      copiedSummary.value = false
    }, 2000)
  }
}

function close() {
  emit('update:modelValue', false)
}
</script>
