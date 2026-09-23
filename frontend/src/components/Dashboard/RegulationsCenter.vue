<template>
  <div class="space-y-4">
    <!-- 顶部状态栏与刷新控制 -->
    <div class="flex items-center justify-between">
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
              RAG 知识底座
            </span>
          </h3>
        </div>
      </div>

      <div class="flex items-center space-x-2">
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
          title="刷新知识库台账与切块"
        >
          <svg class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="hidden sm:inline">刷新</span>
        </button>
      </div>
    </div>

    <!-- 1. 顶部宏观 KPI 磁贴 (Bento Metrics) -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <!-- 磁贴 1: 在册规程篇数 -->
      <div
        class="p-3.5 rounded-xl border transition-all shadow-sm flex flex-col justify-between"
        :class="theme === 'light' ? 'bg-white/80 border-slate-200/80 shadow-slate-100' : 'bg-zinc-900/60 border-white/[0.08]'"
      >
        <div class="flex items-center justify-between text-xs text-zinc-400 mb-1">
          <span :class="theme === 'light' ? 'text-slate-500 font-medium' : 'text-zinc-400'">在册安全规程</span>
          <span class="p-1 rounded-md" :class="theme === 'light' ? 'bg-indigo-50 text-indigo-600' : 'bg-indigo-500/10 text-indigo-400'">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </span>
        </div>
        <div class="flex items-baseline space-x-1.5">
          <span class="text-2xl font-bold font-mono" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'">
            {{ summary.total_documents || documents.length || 0 }}
          </span>
          <span class="text-xs" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">篇源文档</span>
        </div>
        <div class="text-[11px] mt-2 flex items-center gap-1.5" :class="theme === 'light' ? 'text-emerald-700' : 'text-emerald-400'">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          <span>100% 覆盖机房核心安全域</span>
        </div>
      </div>

      <!-- 磁贴 2: 核心切块数量 -->
      <div
        class="p-3.5 rounded-xl border transition-all shadow-sm flex flex-col justify-between"
        :class="theme === 'light' ? 'bg-white/80 border-slate-200/80 shadow-slate-100' : 'bg-zinc-900/60 border-white/[0.08]'"
      >
        <div class="flex items-center justify-between text-xs text-zinc-400 mb-1">
          <span :class="theme === 'light' ? 'text-slate-500 font-medium' : 'text-zinc-400'">语义切块台账</span>
          <span class="p-1 rounded-md" :class="theme === 'light' ? 'bg-cyan-50 text-cyan-600' : 'bg-cyan-500/10 text-cyan-400'">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </span>
        </div>
        <div class="flex items-baseline space-x-1.5">
          <span class="text-2xl font-bold font-mono" :class="theme === 'light' ? 'text-cyan-700' : 'text-cyan-400'">
            {{ summary.total_chunks || totalChunksCount || 0 }}
          </span>
          <span class="text-xs" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">个 Chunks</span>
        </div>
        <div class="text-[11px] mt-2 flex items-center gap-1.5" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">
          <span>总计 {{ summary.total_chars || totalCharsCount || 0 }} 字符精细分块</span>
        </div>
      </div>

      <!-- 磁贴 3: 业务覆盖分类 -->
      <div
        class="p-3.5 rounded-xl border transition-all shadow-sm flex flex-col justify-between"
        :class="theme === 'light' ? 'bg-white/80 border-slate-200/80 shadow-slate-100' : 'bg-zinc-900/60 border-white/[0.08]'"
      >
        <div class="flex items-center justify-between text-xs text-zinc-400 mb-1">
          <span :class="theme === 'light' ? 'text-slate-500 font-medium' : 'text-zinc-400'">规程管理域</span>
          <span class="p-1 rounded-md" :class="theme === 'light' ? 'bg-amber-50 text-amber-600' : 'bg-amber-500/10 text-amber-400'">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
            </svg>
          </span>
        </div>
        <div class="flex items-baseline space-x-1.5">
          <span class="text-2xl font-bold font-mono" :class="theme === 'light' ? 'text-amber-700' : 'text-amber-400'">
            {{ Object.keys(summary.categories || {}).length || 3 }}
          </span>
          <span class="text-xs" :class="theme === 'light' ? 'text-slate-500' : 'text-zinc-400'">大核心业务分类</span>
        </div>
        <div class="text-[11px] mt-2 truncate" :class="theme === 'light' ? 'text-slate-600' : 'text-zinc-400'">
          用电规范 · 应急条例 · 维保规程
        </div>
      </div>

      <!-- 磁贴 4: 向量引擎状态 -->
      <div
        class="p-3.5 rounded-xl border transition-all shadow-sm flex flex-col justify-between"
        :class="theme === 'light' ? 'bg-white/80 border-slate-200/80 shadow-slate-100' : 'bg-zinc-900/60 border-white/[0.08]'"
      >
        <div class="flex items-center justify-between text-xs text-zinc-400 mb-1">
          <span :class="theme === 'light' ? 'text-slate-500 font-medium' : 'text-zinc-400'">向量索引引擎</span>
          <span class="p-1 rounded-md" :class="theme === 'light' ? 'bg-emerald-50 text-emerald-600' : 'bg-emerald-500/10 text-emerald-400'">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </span>
        </div>
        <div class="flex items-baseline space-x-2">
          <span class="text-sm font-semibold truncate" :class="theme === 'light' ? 'text-slate-900' : 'text-zinc-100'">
            {{ summary.vector_engine?.engine || 'ChromaDB / 余弦双模' }}
          </span>
        </div>
        <div class="text-[11px] mt-2 flex items-center justify-between">
          <span class="flex items-center gap-1.5" :class="theme === 'light' ? 'text-emerald-700' : 'text-emerald-400'">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>引擎就绪 · 双模高可用</span>
          </span>
          <span class="font-mono text-[10px]" :class="theme === 'light' ? 'text-slate-400' : 'text-zinc-500'">Top-K=5</span>
        </div>
      </div>
    </div>

    <!-- 2. 搜索栏与分类过滤 Controls -->
    <div
      class="p-4 rounded-xl border transition-all shadow-sm space-y-3"
      :class="theme === 'light' ? 'bg-white/80 border-slate-200/80 shadow-slate-100' : 'bg-zinc-900/60 border-white/[0.08]'"
    >
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <!-- 分类选择 Tabs -->
        <div class="flex items-center space-x-1 p-1 rounded-xl border text-xs overflow-x-auto select-none"
          :class="theme === 'light' ? 'bg-slate-100/90 border-slate-200' : 'bg-zinc-950/60 border-white/[0.06]'"
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
            placeholder="语义/关键词检索（如：4.5kW功耗、超温40℃、防重复借出）..."
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

      <!-- 快速检索热词胶囊 (Hot Queries) -->
      <div class="flex items-center gap-1.5 flex-wrap pt-1 text-xs">
        <span class="text-[11px] font-medium" :class="theme === 'light' ? 'text-slate-400' : 'text-zinc-500'">
          常见咨询热词：
        </span>
        <button
          v-for="hot in hotChips"
          :key="hot.query"
          @click="applyHotChip(hot.query)"
          class="px-2.5 py-1 rounded-lg text-[11px] border transition-all active:scale-95 flex items-center space-x-1 shadow-sm"
          :class="[
            theme === 'light'
              ? 'bg-slate-50 hover:bg-indigo-50 border-slate-200 hover:border-indigo-300 text-slate-700 hover:text-indigo-700'
              : 'bg-white/[0.03] hover:bg-indigo-500/10 border-white/[0.06] hover:border-indigo-500/30 text-zinc-300 hover:text-indigo-300'
          ]"
        >
          <span>{{ hot.label }}</span>
        </button>
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
            关键词：“{{ lastSearchedQuery }}” · 共 {{ searchResults.length }} 条语义切块
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
        <div class="text-zinc-400 text-xs">未找到与“{{ lastSearchedQuery }}”相符的规程切块，建议更换关键词重试。</div>
      </div>

      <!-- 结果卡片列表 -->
      <div v-else class="space-y-3">
        <div
          v-for="(item, idx) in searchResults"
          :key="idx"
          class="p-4 rounded-xl border transition-all shadow-sm space-y-2.5 relative overflow-hidden group"
          :class="theme === 'light' ? 'bg-white/90 border-slate-200/90 shadow-slate-100 hover:border-indigo-400/50' : 'bg-zinc-900/80 border-white/[0.08] hover:border-indigo-500/40'"
        >
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center space-x-2">
              <span
                class="px-2 py-0.5 rounded text-[10px] font-mono font-medium border"
                :class="getScoreBadgeClass(item.score)"
              >
                相似度: {{ item.score_percent }}
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
            <span class="text-[10px] text-zinc-400">RAG Cosine: {{ item.score }}</span>
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
          正在加载机房规程知识库与切块详情...
        </div>
      </div>

      <!-- 规程卡片循环 -->
      <div
        v-for="doc in filteredDocuments"
        :key="doc.doc_id"
        class="rounded-xl border transition-all shadow-sm overflow-hidden"
        :class="theme === 'light' ? 'bg-white/90 border-slate-200/90 shadow-slate-100' : 'bg-zinc-900/70 border-white/[0.08]'"
      >
        <!-- 规程卡片顶栏 Header -->
        <div
          class="p-4 border-b flex flex-col md:flex-row md:items-center justify-between gap-3"
          :class="theme === 'light' ? 'bg-slate-50/80 border-slate-200' : 'bg-white/[0.02] border-white/[0.06]'"
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
            <div class="flex items-center space-x-3 text-[11px] text-zinc-400">
              <span class="font-mono">{{ doc.doc_id }}</span>
              <span>·</span>
              <span>生效日期: {{ doc.effective_date }}</span>
              <span>·</span>
              <span>总字数: {{ doc.char_count }} 字</span>
              <span>·</span>
              <span :class="theme === 'light' ? 'text-indigo-600 font-medium' : 'text-indigo-400 font-medium'">
                {{ doc.chunk_count }} 个 RAG 切块
              </span>
            </div>
          </div>

          <!-- 右侧操作栏 -->
          <div class="flex items-center space-x-2 shrink-0">
            <!-- 切换底层切块展开/收起 (答辩亮点探针) -->
            <button
              @click="toggleDocChunks(doc.doc_id)"
              class="px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all flex items-center space-x-1.5 active:scale-95 shadow-sm"
              :class="[
                expandedDocs[doc.doc_id]
                  ? (theme === 'light' ? 'bg-indigo-50 border-indigo-300 text-indigo-700' : 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300')
                  : (theme === 'light' ? 'bg-white hover:bg-slate-100 border-slate-200 text-slate-700' : 'bg-zinc-800/80 hover:bg-zinc-700 border-white/[0.08] text-zinc-300')
              ]"
              title="透明查验该规程的底层 RAG 语义切块与向量 ID 映射"
            >
              <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              <span>{{ expandedDocs[doc.doc_id] ? '收起向量切块' : '查验 RAG 切块' }}</span>
              <svg
                class="w-3 h-3 transition-transform duration-200"
                :class="{ 'rotate-180': expandedDocs[doc.doc_id] }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- 向 AI 咨询此规程 -->
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
          </div>
        </div>

        <!-- 规程条款沉浸式预览 (逐条渲染与红线高亮) -->
        <div class="p-4 space-y-3">
          <div
            v-if="!docDetailMap[doc.doc_id]"
            class="py-4 text-center text-xs text-zinc-400 animate-pulse"
          >
            正在加载《{{ doc.title }}》条款切块详情...
          </div>
          <div
            v-else-if="getPreviewChunks(doc.doc_id).length === 0"
            class="py-4 text-center text-xs text-zinc-400"
          >
            该规程暂未切块或无可用条款内容
          </div>
          <div
            v-else
            v-for="chunk in getPreviewChunks(doc.doc_id)"
            :key="chunk.id || chunk.chunk_id"
            class="p-3 rounded-lg border transition-all"
            :class="theme === 'light' ? 'bg-slate-50/50 border-slate-200/70 hover:border-indigo-300' : 'bg-zinc-950/40 border-white/[0.04] hover:border-white/[0.1]'"
          >
            <div class="flex items-start justify-between gap-3">
              <!-- 左侧内容区：标题与正文垂直对齐，不挤占右侧操作区 -->
              <div class="min-w-0 flex-1 space-y-1.5">
                <div class="text-xs font-semibold flex items-start gap-1.5" :class="theme === 'light' ? 'text-indigo-800' : 'text-indigo-300'">
                  <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 mt-1.5 shrink-0"></span>
                  <span class="break-words leading-relaxed">{{ chunk.section_title }}</span>
                </div>
                <div
                  class="text-xs leading-relaxed font-sans pl-3"
                  :class="theme === 'light' ? 'text-slate-700' : 'text-zinc-300'"
                  v-html="renderHighlightedText(chunk.chunk_content)"
                ></div>
              </div>

              <!-- 右侧操作区：独立咨询此条按钮 -->
              <button
                @click="askAIAboutClause(doc, chunk)"
                class="shrink-0 text-[11px] text-zinc-400 hover:text-indigo-400 flex items-center space-x-1 transition-colors whitespace-nowrap pt-0.5 select-none"
                title="针对此章节条款专项发问"
              >
                <svg class="w-3 h-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="whitespace-nowrap">咨询此条</span>
              </button>
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
                <span>RAG 向量台账透明查验探针</span>
              </span>
              <span class="text-zinc-400">（毕业设计 RAG 检索增强向量化切块展示）</span>
            </div>
            <span class="text-[11px] font-mono text-zinc-500">
              Chroma Collection: regulations
            </span>
          </div>

          <!-- 切块表格/网格流 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            <div
              v-for="chunk in docDetailMap[doc.doc_id]?.chunks || []"
              :key="chunk.chunk_id"
              class="p-3 rounded-lg border font-mono text-xs space-y-1.5"
              :class="theme === 'light' ? 'bg-white border-slate-200/90 shadow-sm' : 'bg-zinc-900/90 border-white/[0.06]'"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  theme: {
    type: String,
    default: 'dark',
  },
})

const emit = defineEmits(['askAI', 'refresh'])

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

// 预设常见咨询热词胶囊
const hotChips = [
  { label: '4.5kW 单机架功耗上限', query: '机房单机架功耗上限是多少，能否超限？' },
  { label: '空调故障超温 40℃ 应急预案', query: '机房空调故障温度超过40度时怎么应急响应？' },
  { label: '15分钟现场干预要求', query: 'OVERHEAT 状态下运维人员须多长时间内到达现场？' },
  { label: '不良设备借用拦截机制', query: '已借出或标注不良的设备系统如何拦截借用？' },
  { label: '每日 09:00 与 16:00 巡检', query: '机房日常人工巡检时间及要求是什么？' },
  { label: 'GPU 卡加装审批流程', query: '服务器加装高功耗 GPU 需提前几天申请与审批？' },
]

// 分类选项及各分类计数
const categoryOptions = computed(() => {
  const cats = summary.value.categories || {}
  const total = documents.value.length || summary.value.total_documents || 0
  return [
    { label: '全部规程', value: 'ALL', count: total },
    { label: '用电规范', value: '用电规范', count: cats['用电规范'] || 0 },
    { label: '应急条例', value: '应急条例', count: cats['应急条例'] || 0 },
    { label: '维保规程', value: '维保规程', count: cats['维保规程'] || 0 },
  ]
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

// 热词胶囊触发
function applyHotChip(query) {
  searchQuery.value = query
  handleSearch()
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
})
</script>
