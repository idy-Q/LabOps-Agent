<template>
  <div class="space-y-4">
    <!-- 顶部状态栏与操作控制 -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="flex items-center space-x-2">
        <span
          class="p-1.5 rounded-lg border shadow-sm flex items-center justify-center"
          :class="theme === 'light' ? 'bg-white border-slate-200 text-indigo-600' : 'bg-zinc-900/90 border-white/[0.08] text-indigo-400'"
        >
          <!-- 书本知识库矢量 SVG -->
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </span>
        <div>
          <h3 class="text-xs sm:text-sm font-medium flex items-center gap-2" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'">
            <span>规章规程知识中心</span>
            <span
              class="text-[10px] px-2 py-0.5 rounded-full font-mono font-medium border"
              :class="theme === 'light' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300'"
            >
              安全规约库
            </span>
          </h3>
        </div>
      </div>

      <div class="flex items-center space-x-2 flex-wrap gap-y-1">
        <!-- 【+ 录入新规程】按钮（仅系统超级管理员可见） -->
        <button
          v-if="canAddRegulation"
          @click="openCreateModal"
          class="text-xs flex items-center space-x-1.5 transition-all px-3 py-1.5 rounded-lg border font-medium active:scale-95 shadow-sm select-none"
          :class="[
            theme === 'light'
              ? 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border-emerald-300 shadow-emerald-100'
              : 'bg-emerald-600/90 hover:bg-emerald-500 text-white border-emerald-400/40 shadow-emerald-500/20'
          ]"
          title="录入新机房安全规程，自动完成语义切块并同步至向量知识库"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>录入新规程</span>
        </button>

        <!-- 快速向 AI 咨询机房安全总则 -->
        <button
          @click="askAIGeneral"
          class="text-xs flex items-center space-x-1.5 transition-all px-3 py-1.5 rounded-lg border font-medium active:scale-95 shadow-sm select-none"
          :class="[
            theme === 'light'
              ? 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-200 shadow-indigo-100'
              : 'bg-indigo-600/90 hover:bg-indigo-500 text-white border-indigo-400/30 shadow-indigo-500/20'
          ]"
          title="将机房安全规章咨询直接注入左侧 AI 运维管家"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <span>向 AI 咨询规程</span>
        </button>

        <!-- 刷新数据 -->
        <button
          @click="loadAll"
          :disabled="loading"
          class="text-xs flex items-center space-x-1.5 transition-all px-2.5 py-1.5 rounded-lg border active:scale-95 shadow-sm"
          :class="[
            theme === 'light'
              ? 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
              : 'bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border-white/[0.08]'
          ]"
          title="刷新安全规约库与规约细则"
        >
          <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="hidden sm:inline">刷新</span>
        </button>
      </div>
    </div>


    <!-- 规程录入与修改独立弹窗组件 (带 Teleport 顶层挂载、两段式防误触与明暗双模态深度优化) -->
    <RegulationFormModal
      v-model="showCreateModal"
      :theme="theme"
      :currentUser="currentUser"
      :editDoc="editingDoc"
      @saved="handleRegulationSaved"
    />

    <!-- 2. 搜索栏与分类过滤 Controls -->
    <div
      class="p-3.5 sm:p-4 rounded-xl border glass-panel transition-all shadow-sm"
      :class="theme === 'light' ? 'border-slate-200/80 shadow-slate-100' : ''"
    >
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <!-- 分类选择 Tabs -->
        <div class="flex items-center space-x-1 p-1 rounded-xl border glass-card-sub text-xs overflow-x-auto select-none"
          :class="theme === 'light' ? 'border-slate-200' : ''"
        >
          <button
            v-for="cat in categoryOptions"
            :key="cat.value"
            @click="selectCategory(cat.value)"
            class="px-3 py-1.5 rounded-lg font-medium transition-all flex items-center space-x-1.5 whitespace-nowrap"
            :class="[
              activeCategory === cat.value
                ? (theme === 'light' ? 'bg-white text-indigo-600 shadow-sm border border-slate-200' : 'bg-zinc-800 text-white shadow-sm border border-white/[0.08]')
                : (theme === 'light' ? 'text-slate-600 hover:text-slate-900' : 'text-zinc-400 hover:text-zinc-200')
            ]"
          >
            <span>{{ cat.label }}</span>
            <span
              class="px-1.5 py-0.2 rounded-full text-[10px] font-mono"
              :class="activeCategory === cat.value ? 'bg-indigo-500/20 text-indigo-400' : 'opacity-60'"
            >
              {{ cat.count }}
            </span>
          </button>
        </div>

        <!-- 搜索输入框 -->
        <div class="relative flex-1 max-w-md">
          <input
            v-model="searchQuery"
            @keydown.enter="handleSearch"
            type="text"
            placeholder="搜索规程编号、规程标题、条例细则或安全规范..."
            class="w-full pl-9 pr-20 py-2 rounded-xl text-xs border outline-none transition-all placeholder:text-zinc-500"
            :class="[
              theme === 'light'
                ? 'bg-white border-slate-200 focus:border-indigo-500 text-slate-800 shadow-sm'
                : 'bg-zinc-950/70 border-white/[0.08] focus:border-indigo-500 text-zinc-100'
            ]"
          />
          <svg class="w-4 h-4 absolute left-3 top-2.5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <div class="absolute right-2 top-1.5 flex items-center space-x-1">
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="p-1 rounded-md text-zinc-400 hover:text-zinc-200 transition-colors"
              title="清空检索"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <button
              @click="handleSearch"
              class="px-2.5 py-1 rounded-lg text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-sm active:scale-95"
            >
              检索
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 语义检索匹配结果卡片流 (当处于检索模式时渲染) -->
    <div v-if="isSearchMode" class="space-y-3">
      <div class="flex items-center justify-between px-1">
        <div class="flex items-center space-x-2 text-xs">
          <span class="font-medium" :class="theme === 'light' ? 'text-slate-800' : 'text-zinc-200'">
            检索结果匹配项
          </span>
          <span
            class="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium border"
            :class="theme === 'light' ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300'"
          >
            关键词：“{{ lastSearchedQuery }}” · 共 {{ searchResults.length }} 条规约细则
          </span>
        </div>
        <button
          @click="clearSearch"
          class="text-xs text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
        >
          <span>返回全部规程全貌</span>
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 检索中 Loading -->
      <div v-if="isSearching" class="p-8 text-center rounded-xl border" :class="theme === 'light' ? 'bg-white border-slate-200' : 'bg-zinc-900/40 border-white/[0.08]'">
        <div class="inline-flex items-center justify-center p-3 rounded-xl bg-indigo-500/10 text-indigo-400 mb-2 animate-pulse">
          <svg class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        <div class="text-xs font-medium" :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'">
          正在调用向量引擎进行语义检索与相似度评分计算...
        </div>
      </div>

      <!-- 空检索结果 -->
      <div v-else-if="searchResults.length === 0" class="p-8 text-center rounded-xl border" :class="theme === 'light' ? 'bg-white border-slate-200' : 'bg-zinc-900/40 border-white/[0.08]'">
        <div class="text-zinc-400 text-xs">未找到与“{{ lastSearchedQuery }}”相符的规约细则，建议更换关键词重试。</div>
      </div>

      <!-- 结果卡片列表 -->
      <div v-else class="space-y-3">
        <div
          v-for="(item, idx) in searchResults"
          :key="idx"
          class="p-4 rounded-xl border glass-card transition-all shadow-sm space-y-2.5 relative overflow-hidden group hover:border-indigo-400/50"
          :class="theme === 'light' ? 'border-slate-200/90 shadow-slate-100' : ''"
        >
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center space-x-2">
              <span
                class="px-2 py-0.5 rounded text-[10px] font-mono font-medium border"
                :class="getScoreBadgeClass(item.score)"
              >
                匹配度: {{ (item.score * 100).toFixed(0) }}%
              </span>
              <span class="text-xs font-semibold" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'">
                {{ item.doc_title }}
              </span>
              <span class="text-xs font-medium" :class="theme === 'light' ? 'text-indigo-600' : 'text-indigo-400'">
                {{ item.section }}
              </span>
              <span
                v-if="item.category"
                class="px-1.5 py-0.2 rounded text-[10px] font-mono border"
                :class="getCategoryBadgeClass(item.category)"
              >
                {{ item.category }}
              </span>
            </div>

            <div class="flex items-center space-x-2 shrink-0">
              <span v-if="item.chunk_id" class="text-[10px] font-mono px-2 py-0.5 rounded border shrink-0"
                :class="theme === 'light' ? 'bg-slate-50 border-slate-200 text-slate-500' : 'bg-zinc-800 border-white/[0.06] text-zinc-400'"
              >
                {{ item.chunk_id }}
              </span>
              <button
                @click="askAIAboutSearchResult(item)"
                class="px-2.5 py-1 rounded-lg text-xs font-medium transition-all flex items-center space-x-1 border active:scale-95 shadow-sm shrink-0 whitespace-nowrap"
                :class="[
                  theme === 'light'
                    ? 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border-indigo-200'
                    : 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border-indigo-500/30'
                ]"
                title="以此条款向 AI 运维管家提问"
              >
                <svg class="w-3 h-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span class="whitespace-nowrap">向 AI 咨询此条</span>
              </button>
            </div>
          </div>

          <!-- 条款正文高亮渲染 -->
          <div
            class="text-xs leading-relaxed font-sans"
            :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
            v-html="renderHighlightedText(item.content)"
          ></div>

          <div class="text-[11px] font-mono text-zinc-500 pt-1 border-t border-white/[0.04] flex items-center justify-between">
            <span>{{ item.source }}</span>
            <span class="text-[10px] text-zinc-400">匹配度: {{ (item.score * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. 规程全景卡片流 (规程沉浸式阅读卡片流) -->
    <div v-else class="space-y-4">
      <!-- 加载状态 -->
      <div v-if="loading && documents.length === 0" class="p-8 text-center rounded-xl border" :class="theme === 'light' ? 'bg-white border-slate-200' : 'bg-zinc-900/40 border-white/[0.08]'">
        <div class="inline-flex items-center justify-center p-3 rounded-xl bg-indigo-500/10 text-indigo-400 mb-2 animate-pulse">
          <svg class="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        <div class="text-xs" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">
          正在加载机房安全规约库与规约细则...
        </div>
      </div>

      <!-- 规程卡片循环 -->
      <div
        v-for="doc in filteredDocuments"
        :key="doc.doc_id"
        class="rounded-xl border glass-card transition-all shadow-sm overflow-hidden"
        :class="theme === 'light' ? 'border-slate-200/90 shadow-slate-100' : ''"
      >
        <!-- 规程卡片顶栏 Header -->
        <div
          class="p-4 border-b glass-card-sub flex flex-col md:flex-row md:items-center justify-between gap-3"
        >
          <div class="space-y-1.5">
            <div class="flex items-center space-x-2 flex-wrap gap-y-1">
              <!-- 分类徽章 -->
              <span
                class="px-2 py-0.5 rounded text-[10px] font-mono font-medium border"
                :class="getCategoryBadgeClass(doc.category)"
              >
                {{ doc.category }}
              </span>

              <!-- 规程标题 -->
              <h4 class="text-sm font-semibold tracking-wide" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'">
                {{ doc.title }}
              </h4>

              <!-- 版本号 -->
              <span
                class="px-1.5 py-0.2 rounded text-[10px] font-mono border"
                :class="theme === 'light' ? 'bg-slate-100 border-slate-200 text-slate-600' : 'bg-zinc-800 border-white/[0.08] text-zinc-400'"
              >
                {{ doc.version }}
              </span>
            </div>

            <!-- 元数据行 -->
            <div class="flex items-center space-x-3 text-[11px] text-zinc-400 flex-wrap gap-y-1">
              <span class="font-mono font-medium whitespace-nowrap">{{ doc.doc_id }}</span>
              <span>·</span>
              <span class="whitespace-nowrap">生效日期: {{ doc.effective_date }}</span>
              <span>·</span>
              <span class="whitespace-nowrap">总字数: {{ doc.char_count }} 字</span>
              <span>·</span>
              <span class="whitespace-nowrap" :class="theme === 'light' ? 'text-indigo-600 font-medium' : 'text-indigo-400 font-medium'">
                {{ doc.chunk_count }} 条规约细则
              </span>
            </div>
          </div>

          <!-- 右侧操作栏 (收敛为主按钮【向 AI 咨询此规程】与【更多】下拉菜单) -->
          <div class="flex items-center space-x-2 shrink-0">
            <!-- 向 AI 咨询此规程 (高频主操作) -->
            <button
              @click="askAIAboutDoc(doc)"
              class="px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center space-x-1.5 border active:scale-95 shadow-sm"
              :class="[
                theme === 'light'
                  ? 'bg-indigo-600 hover:bg-indigo-500 text-white border-indigo-500 shadow-indigo-100'
                  : 'bg-indigo-600/90 hover:bg-indigo-500 text-white border-indigo-400/30 shadow-indigo-500/20'
              ]"
              title="将针对该规程的深度解读诉求带入左侧 AI 运维管家对话流"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span>向 AI 咨询此规程</span>
            </button>

            <!-- 【更多】下拉操作菜单 (收敛：查验规约条目细目 / 编辑规程 / 废止规程) -->
            <div class="relative inline-block text-left">
              <button
                @click.stop="toggleMoreMenu(doc.doc_id)"
                class="px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all flex items-center space-x-1 active:scale-95 shadow-sm"
                :class="[
                  activeMoreMenuDocId === doc.doc_id
                    ? (theme === 'light' ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300')
                    : (theme === 'light' ? 'bg-white hover:bg-slate-100 border-slate-200 text-slate-700' : 'bg-zinc-800/80 hover:bg-zinc-700 border-white/[0.08] text-zinc-300')
                ]"
                title="更多操作 (查验细目 / 编辑 / 废止)"
              >
                <span>更多</span>
                <svg
                  class="w-3 h-3 transition-transform duration-200"
                  :class="{ 'rotate-180': activeMoreMenuDocId === doc.doc_id }"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <div
                v-if="activeMoreMenuDocId === doc.doc_id"
                @click.stop
                class="glass-acrylic-popover absolute right-0 w-44 py-1 rounded-xl border z-30 text-xs font-sans text-left mt-1.5 select-none"
              >
                <!-- 1. 查验规约条目细目 (保留原功能，点击展开/收起) -->
                <button
                  @click="toggleDocChunks(doc.doc_id); closeMoreMenu()"
                  class="w-full px-3 py-2 flex items-center space-x-2 transition-colors text-left"
                  :class="theme === 'light' ? 'hover:bg-slate-100 text-slate-700 hover:text-indigo-600' : 'hover:bg-white/[0.08] text-zinc-300 hover:text-indigo-300'"
                >
                  <svg class="w-3.5 h-3.5 text-cyan-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <span>{{ expandedDocs[doc.doc_id] ? '收起规约细目' : '查验规约条目细目' }}</span>
                </button>

                <!-- 管理员专属操作：编辑与废止 -->
                <template v-if="canAddRegulation">
                  <div class="my-1 border-t" :class="theme === 'light' ? 'border-slate-100' : 'border-white/[0.08]'"></div>

                  <!-- 2. 编辑规程 -->
                  <button
                    @click="openEditRegulation(doc); closeMoreMenu()"
                    class="w-full px-3 py-2 flex items-center space-x-2 transition-colors text-left"
                    :class="theme === 'light' ? 'hover:bg-slate-100 text-slate-700 hover:text-indigo-600' : 'hover:bg-white/[0.08] text-zinc-300 hover:text-indigo-300'"
                  >
                    <svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <span>编辑规程</span>
                  </button>

                  <!-- 3. 废止规程 -->
                  <button
                    @click="openDeleteRegulation(doc); closeMoreMenu()"
                    class="w-full px-3 py-2 flex items-center space-x-2 transition-colors text-left text-rose-400 hover:text-rose-300"
                    :class="theme === 'light' ? 'hover:bg-rose-50 text-rose-600' : 'hover:bg-rose-500/10'"
                  >
                    <svg class="w-3.5 h-3.5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    <span>废止此规程</span>
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- 规程条款沉浸式预览 (按章节语义聚合，结构化展现，杜绝碎片化拆分与标题正文重复) -->
        <div class="p-4 space-y-3">
          <div
            v-if="!docDetailMap[doc.doc_id]"
            class="py-4 text-center text-xs text-zinc-400 animate-pulse"
          >
            正在加载《{{ doc.title }}》条款详情...
          </div>
          <div
            v-else-if="getAggregatedSections(doc.doc_id).length === 0"
            class="py-4 text-center text-xs text-zinc-400"
          >
            该规程暂无可用条款内容
          </div>
          <div
            v-else
            v-for="sec in getAggregatedSections(doc.doc_id)"
            :key="sec.key"
            class="p-3.5 rounded-xl border glass-card-sub transition-all space-y-2.5"
            :class="theme === 'light' ? 'hover:border-indigo-300 shadow-xs' : 'hover:border-white/[0.12]'"
          >
            <!-- 章节标题栏与整条问询入口 -->
            <div class="flex items-center justify-between gap-3">
              <div class="text-xs font-bold flex items-center gap-2 min-w-0" :class="theme === 'light' ? 'text-indigo-900' : 'text-indigo-300'">
                <span class="w-2 h-2 rounded-full bg-indigo-500 shrink-0"></span>
                <span class="truncate tracking-wide">{{ sec.section_title }}</span>
              </div>

              <button
                @click="askAIAboutSection(doc, sec)"
                class="shrink-0 text-[11px] text-zinc-400 hover:text-indigo-400 flex items-center space-x-1 transition-colors whitespace-nowrap select-none"
                title="针对此章节条款专项解读"
              >
                <svg class="w-3 h-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="whitespace-nowrap">咨询此条</span>
              </button>
            </div>

            <!-- 下属条款列表 -->
            <div class="space-y-2 pl-3.5 border-l-2 border-indigo-500/25">
              <div
                v-for="clause in sec.clauses"
                :key="clause.id"
                class="text-xs leading-relaxed font-sans"
                :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                v-html="renderHighlightedText(clause.content)"
              ></div>
            </div>
          </div>
        </div>

        <!-- 5. RAG 向量切块折叠抽屉 (答辩亮点探针) -->
        <div
          v-if="expandedDocs[doc.doc_id]"
          class="border-t p-4 space-y-3 animate-fade-in"
          :class="theme === 'light' ? 'bg-indigo-50/40 border-indigo-100' : 'bg-black/30 border-white/[0.06]'"
        >
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="font-mono text-cyan-400 flex items-center gap-1 font-medium">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                <span>查验规约条目细目</span>
              </span>
              <span class="text-zinc-400">（底层规约条款细目与向量标识查验）</span>
            </div>
            <span class="text-[11px] font-mono text-zinc-500">
              安全规约库集合: regulations
            </span>
          </div>

          <!-- 切块表格/网格流 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            <div
              v-for="chunk in docDetailMap[doc.doc_id]?.chunks || []"
              :key="chunk.chunk_id"
              class="p-3 rounded-lg border glass-card-sub font-mono text-xs space-y-1.5"
              :class="theme === 'light' ? 'border-slate-200/90 shadow-xs' : ''"
            >
              <div class="flex items-center justify-between">
                <span class="font-semibold text-[11px] text-cyan-400">
                  #{{ chunk.chunk_index }} · {{ chunk.chunk_id }}
                </span>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-white/[0.04] text-zinc-400 border border-white/[0.04]">
                  预估 {{ chunk.token_count }} Tokens
                </span>
              </div>
              <div class="text-[11px] font-sans font-medium text-zinc-300 truncate" :title="chunk.section_title">
                {{ chunk.section_title }}
              </div>
              <div class="text-[11px] font-mono text-zinc-500 truncate" :title="chunk.chroma_id || '未登记'">
                Vector ID: {{ chunk.chroma_id || 'N/A' }}
              </div>
              <div
                class="p-2 rounded bg-black/20 text-[11px] font-sans text-zinc-400 max-h-20 overflow-y-auto leading-relaxed"
              >
                {{ chunk.chunk_content }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 规程废止删除二次确认弹窗 -->
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
          v-if="showDeleteConfirmModal"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 backdrop-blur-md overflow-hidden"
          :class="theme === 'light' ? 'bg-slate-900/40' : 'bg-black/75'"
          v-backdrop-dismiss="() => showDeleteConfirmModal = false"
        >
          <div
            class="w-full max-w-sm rounded-3xl border p-5 space-y-4 shadow-2xl backdrop-blur-2xl transition-all"
            :class="theme === 'light' ? 'bg-white border-slate-200 text-slate-800' : 'bg-zinc-900 border-white/[0.12] text-zinc-100'"
          >
            <div class="flex items-center space-x-3">
              <span class="p-2.5 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-400">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </span>
              <div>
                <h4 class="text-sm font-semibold tracking-tight">废止规章规程确认</h4>
                <p class="text-xs text-zinc-400 mt-0.5">此操作将级联清理所有底层语义切块与向量索引</p>
              </div>
            </div>

            <div class="p-3 rounded-2xl border text-xs space-y-1" :class="theme === 'light' ? 'bg-slate-50 border-slate-200' : 'bg-zinc-950/60 border-white/[0.04]'">
              <div>待废止规程：<span class="font-medium text-rose-400 font-mono">《{{ docToDelete?.title }}》</span></div>
              <div>文档编号：<span class="font-mono text-zinc-400">{{ docToDelete?.doc_id }}</span></div>
              <div class="text-[11px] text-zinc-500 pt-1 border-t border-white/[0.04]">下属 {{ docToDelete?.chunk_count || 0 }} 条规约细则将从安全规约库中同步移除。</div>
            </div>

            <div v-if="deleteDocError" class="p-2 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {{ deleteDocError }}
            </div>

            <div class="flex items-center justify-end space-x-2 pt-2 border-t" :class="theme === 'light' ? 'border-slate-200' : 'border-white/[0.06]'">
              <button
                @click="showDeleteConfirmModal = false"
                class="px-3.5 py-1.5 rounded-xl border text-xs transition-colors"
                :class="theme === 'light' ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200' : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border-white/[0.06]'"
              >
                取消
              </button>
              <button
                @click="confirmDeleteRegulation"
                :disabled="isDeletingDoc"
                class="px-4 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md transition-all active:scale-95 disabled:opacity-50 flex items-center space-x-1.5"
              >
                <span v-if="isDeletingDoc" class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>{{ isDeletingDoc ? '正在下线废止...' : '确认废止并删除' }}</span>
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { api } from '../../api/client'
import RegulationFormModal from './RegulationFormModal.vue'

const props = defineProps({
  theme: {
    type: String,
    default: 'dark',
  },
  currentUser: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['askAI', 'refresh'])

// 更多操作下拉菜单控制
const activeMoreMenuDocId = ref(null)

function toggleMoreMenu(docId) {
  if (activeMoreMenuDocId.value === docId) {
    activeMoreMenuDocId.value = null
  } else {
    activeMoreMenuDocId.value = docId
  }
}

function closeMoreMenu() {
  activeMoreMenuDocId.value = null
}

// 权限控制：规章规程录入、编辑与废止下线工作仅限系统超级管理员(ADMIN)操作
const canAddRegulation = computed(() => {
  return props.currentUser?.role === 'ADMIN'
})

// 规程录入与编辑模态框控制
const showCreateModal = ref(false)
const editingDoc = ref(null)

function openCreateModal() {
  editingDoc.value = null
  showCreateModal.value = true
}

async function openEditRegulation(doc) {
  let detail = docDetailMap.value[doc.doc_id]
  if (!detail || !detail.chunks || detail.chunks.length === 0) {
    try {
      detail = await api.getRegulationDetail(doc.doc_id)
      docDetailMap.value[doc.doc_id] = detail
    } catch {
      detail = doc
    }
  }
  editingDoc.value = detail
  showCreateModal.value = true
}

// 废止删除确认模态框状态与处理
const showDeleteConfirmModal = ref(false)
const docToDelete = ref(null)
const isDeletingDoc = ref(false)
const deleteDocError = ref('')

function openDeleteRegulation(doc) {
  docToDelete.value = doc
  deleteDocError.value = ''
  showDeleteConfirmModal.value = true
}

async function confirmDeleteRegulation() {
  if (!docToDelete.value) return
  isDeletingDoc.value = true
  deleteDocError.value = ''
  try {
    await api.deleteRegulation(docToDelete.value.doc_id, {
      operator: props.currentUser?.real_name || props.currentUser?.username || '管理员',
      operator_role: props.currentUser?.role || 'ADMIN',
    })
    showDeleteConfirmModal.value = false
    docToDelete.value = null
    await loadAll()
    emit('refresh')
  } catch (err) {
    deleteDocError.value = err.message || '废止删除规程失败，请重试'
  } finally {
    isDeletingDoc.value = false
  }
}

async function handleRegulationSaved() {
  await loadAll()
  emit('refresh')
}


// 数据状态
const loading = ref(false)
const documents = ref([])
const summary = ref({})
const docDetailMap = ref({}) // doc_id -> RegulationDetailResponse
const expandedDocs = ref({}) // doc_id -> boolean

// 过滤与搜索
const activeCategory = ref('ALL')
const searchQuery = ref('')
const lastSearchedQuery = ref('')
const isSearchMode = ref(false)
const isSearching = ref(false)
const searchResults = ref([])

// 分类选项及各分类计数 (支持新增分类动态扩展)
const categoryOptions = computed(() => {
  const cats = summary.value.categories || {}
  const total = documents.value.length || summary.value.total_documents || 0
  const base = [
    { label: '全部规程', value: 'ALL', count: total },
    { label: '用电规范', value: '用电规范', count: cats['用电规范'] || 0 },
    { label: '应急条例', value: '应急条例', count: cats['应急条例'] || 0 },
    { label: '维保规程', value: '维保规程', count: cats['维保规程'] || 0 },
  ]
  Object.keys(cats).forEach((k) => {
    if (!['用电规范', '应急条例', '维保规程'].includes(k)) {
      base.push({ label: k, value: k, count: cats[k] || 0 })
    }
  })
  return base
})

// 按分类过滤的文档列表
const filteredDocuments = computed(() => {
  if (activeCategory.value === 'ALL') {
    return documents.value
  }
  return documents.value.filter((d) => d.category === activeCategory.value)
})

const totalChunksCount = computed(() => {
  return documents.value.reduce((acc, d) => acc + (d.chunk_count || 0), 0)
})

const totalCharsCount = computed(() => {
  return documents.value.reduce((acc, d) => acc + (d.char_count || 0), 0)
})

// 分类徽章样式
function getCategoryBadgeClass(category) {
  switch (category) {
    case '用电规范':
      return props.theme === 'light'
        ? 'bg-amber-50 border-amber-300 text-amber-800'
        : 'bg-amber-500/10 border-amber-500/30 text-amber-300'
    case '应急条例':
      return props.theme === 'light'
        ? 'bg-rose-50 border-rose-300 text-rose-800'
        : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
    case '维保规程':
      return props.theme === 'light'
        ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
        : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
    case '安全制度':
      return props.theme === 'light'
        ? 'bg-cyan-50 border-cyan-300 text-cyan-800'
        : 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
    default:
      return props.theme === 'light'
        ? 'bg-slate-100 border-slate-300 text-slate-700'
        : 'bg-zinc-800 border-white/[0.08] text-zinc-300'
  }
}

// 相似度评分胶囊样式
function getScoreBadgeClass(score) {
  if (score >= 0.7) {
    return props.theme === 'light'
      ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
      : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
  } else if (score >= 0.4) {
    return props.theme === 'light'
      ? 'bg-indigo-50 border-indigo-300 text-indigo-800'
      : 'bg-indigo-500/15 border-indigo-500/30 text-indigo-300'
  } else {
    return props.theme === 'light'
      ? 'bg-amber-50 border-amber-300 text-amber-800'
      : 'bg-amber-500/15 border-amber-500/30 text-amber-300'
  }
}

// 安全红线核心数值高亮渲染 (安全 HTML 转义 + 宽容空白正则匹配)
function renderHighlightedText(text) {
  if (!text) return ''
  // 基础 HTML 特殊字符转义以防 XSS 与格式错乱 (如 >40℃)
  const escaped = String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 匹配核心安全数字与关键红线关键词 (支持灵活空白与大小写)
  const regex = /(4\.5\s*kW|40\s*℃|35~38\s*℃|38~40\s*℃|15\s*分钟|15\s*min|30\s*分钟|防重复借出|不良设备出借限制|双路\s*PDU|09:00\s*与\s*16:00|每周一检|3\s*个工作日|熔断降级|OVERHEAT)/gi

  const isLight = props.theme === 'light'
  return escaped.replace(regex, (match) => {
    let colorClass = ''
    const upper = match.toUpperCase()
    if (upper.includes('40℃') || upper.includes('OVERHEAT') || upper.includes('熔断')) {
      colorClass = isLight
        ? 'bg-rose-100 border-rose-300 text-rose-800 font-semibold shadow-xs'
        : 'bg-rose-500/20 border-rose-500/40 text-rose-300 font-semibold'
    } else if (upper.includes('4.5') || upper.includes('15') || upper.includes('30')) {
      colorClass = isLight
        ? 'bg-amber-100 border-amber-300 text-amber-800 font-semibold shadow-xs'
        : 'bg-amber-500/20 border-amber-500/40 text-amber-300 font-semibold'
    } else {
      colorClass = isLight
        ? 'bg-indigo-100 border-indigo-300 text-indigo-800 font-semibold shadow-xs'
        : 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300 font-semibold'
    }
    return `<span class="inline-flex items-center px-1.5 py-0.2 mx-0.5 rounded font-mono text-[11px] border ${colorClass}">${match}</span>`
  })
}

// 获取规程按章节语义聚合后的条款列表 (避免切块导致同一规则分裂为多条卡片和标题正文重复)
function getAggregatedSections(docId) {
  const detail = docDetailMap.value[docId]
  if (!detail || !detail.chunks || detail.chunks.length === 0) {
    return []
  }

  const sections = []
  let currentSec = null
  let currentObj = null

  for (let i = 0; i < detail.chunks.length; i++) {
    const ck = detail.chunks[i]
    const rawTitle = (ck.section_title || '').trim()
    // 匹配章节名，剥离附带在 section_title 后面的条款序号与内容（如 "第二条 功耗上限 1. 单机架..." -> "第二条 功耗上限"）
    const match = rawTitle.match(/^(.*?)\s+\d+\..*$/)
    const cleanSec = match ? match[1].trim() : (rawTitle || '条款正文')

    if (cleanSec !== currentSec) {
      if (currentObj) {
        sections.push(currentObj)
      }
      currentSec = cleanSec
      currentObj = {
        key: `${docId}-${cleanSec}-${i}`,
        section_title: cleanSec,
        clauses: [],
      }
    }

    const content = (ck.chunk_content || '').trim()
    if (content) {
      currentObj.clauses.push({
        id: ck.id || ck.chunk_id || `${currentObj.key}-${i}`,
        content: content,
        rawChunk: ck,
      })
    }
  }

  if (currentObj) {
    sections.push(currentObj)
  }

  return sections
}

function askAIAboutSection(doc, sec) {
  const clausesText = sec.clauses.map((c) => c.content).join('\n')
  const prompt = `在《${doc.title}》中关于“${sec.section_title}”有如下规定：\n“${clausesText}”\n请结合高校实验室机房日常运维实践，详细说明运维人员在此规程下应当如何合规执行？`
  emit('askAI', prompt)
}

// 获取规程在主卡片中沉浸式预览的切块列表
function getPreviewChunks(docId) {
  const detail = docDetailMap.value[docId]
  if (detail && detail.chunks && detail.chunks.length > 0) {
    return detail.chunks
  }
  return []
}

// 展开/收起底层切块抽屉
async function toggleDocChunks(docId) {
  if (expandedDocs.value[docId]) {
    expandedDocs.value = { ...expandedDocs.value, [docId]: false }
    return
  }
  expandedDocs.value = { ...expandedDocs.value, [docId]: true }
  if (!docDetailMap.value[docId]) {
    await loadDocDetail(docId)
  }
}

// 加载单篇详情及切块
async function loadDocDetail(docId) {
  try {
    const detail = await api.getRegulationDetail(docId)
    docDetailMap.value = { ...docDetailMap.value, [docId]: detail }
  } catch (err) {
    console.error(`加载规程 ${docId} 详情失败:`, err)
  }
}

// 分类切换
function selectCategory(cat) {
  activeCategory.value = cat
  if (isSearchMode.value) {
    clearSearch()
  }
}

// 执行语义检索
async function handleSearch() {
  const q = searchQuery.value.trim()
  if (!q) {
    clearSearch()
    return
  }
  isSearchMode.value = true
  isSearching.value = true
  lastSearchedQuery.value = q

  try {
    const results = await api.searchRegulations({ query: q, top_k: 5 })
    searchResults.value = results || []
  } catch (err) {
    console.error('检索规程异常:', err)
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

// 清除检索
function clearSearch() {
  searchQuery.value = ''
  lastSearchedQuery.value = ''
  isSearchMode.value = false
  searchResults.value = []
}

// AI 联动操作
function askAIGeneral() {
  const prompt = '请帮我梳理机房安全规章规程的核心要点，包括用电功耗上限、超温应急预案与巡检出借制度。'
  emit('askAI', prompt)
}

function askAIAboutDoc(doc) {
  const prompt = `请根据《${doc.title}》（版本：${doc.version}），详细解读该规范的核心红线指标与具体运维执行步骤。`
  emit('askAI', prompt)
}

function askAIAboutClause(doc, chunk) {
  const prompt = `在《${doc.title}》中关于“${chunk.section_title}”有如下规定：\n“${chunk.chunk_content}”\n请结合高校实验室机房日常运维实践，详细说明运维人员在此条款下应当如何合规执行？`
  emit('askAI', prompt)
}

function askAIAboutSearchResult(result) {
  const prompt = `请针对机房规程中的此项条款进行答疑分析：\n${result.source}\n${result.content}\n请告诉我该条款背后的安全原理与遇到异常时的处置流程。`
  emit('askAI', prompt)
}

// 加载全部数据
async function loadAll() {
  loading.value = true
  try {
    const [docs, sum] = await Promise.all([
      api.getRegulations(),
      api.getRegulationsSummary(),
    ])
    documents.value = docs || []
    summary.value = sum || {}

    // 预加载所有文档的切块详情，用于沉浸式阅读卡片
    await Promise.allSettled(documents.value.map((doc) => loadDocDetail(doc.doc_id)))
  } catch (err) {
    console.error('加载规章规程中心数据失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAll()
  window.addEventListener('click', closeMoreMenu)
})

onUnmounted(() => {
  window.removeEventListener('click', closeMoreMenu)
})
</script>
