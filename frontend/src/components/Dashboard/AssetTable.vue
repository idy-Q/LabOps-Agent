<template>
  <div class="relative rounded-xl glass-panel border p-4 space-y-3.5 shadow-sm transition-colors flex flex-col min-h-[580px]">
    <!-- 头部与多维分类过滤 -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 pb-2 border-b border-white/[0.06]">
      <div class="flex items-center space-x-2">
        <span class="p-1 rounded-md bg-zinc-900/90 border border-white/[0.08] text-cyan-400">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </span>
        <h3 class="text-xs sm:text-sm font-medium text-zinc-100 glass-text">机房硬件资产与设备台账</h3>
        <span class="px-2 py-0.5 rounded-md bg-zinc-900/80 border border-white/[0.08] text-zinc-400 text-[10px] font-mono">
          共 {{ filteredAssets.length }} 台设备
        </span>
      </div>

      <div class="flex items-center space-x-2 w-full sm:w-auto justify-between sm:justify-end">
        <!-- 分类胶囊 (Linear Segmented Pills) -->
        <div class="flex items-center space-x-1 text-xs bg-zinc-900/60 p-0.5 rounded-lg border border-white/[0.06]">
          <button
            v-for="c in categoryOptions"
            :key="c.value"
            @click="selectedCategory = c.value"
            :class="[
              'px-2.5 py-1 rounded-md text-[11px] transition-all',
              selectedCategory === c.value
                ? 'bg-zinc-800 text-zinc-100 font-medium shadow-sm border border-white/[0.08]'
                : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/50 border border-transparent'
            ]"
          >
            {{ c.label }}
          </button>
        </div>

        <!-- 录入新设备主按钮 (管理员与教师可用，学生禁用) -->
        <button
          :disabled="isStudent"
          @click="!isStudent && openCreateModal()"
          :class="[
            'px-2.5 py-1 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all shadow-sm active:scale-95 shrink-0 border',
            isStudent
              ? 'bg-zinc-800/40 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-50'
              : 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 hover:from-cyan-500/30 hover:to-indigo-500/30 text-cyan-300 hover:text-cyan-200 border-cyan-500/30 hover:border-cyan-500/50'
          ]"
          :title="isStudent ? '学生无权录入设备台账' : '录入新设备与硬件物理参数'"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
          </svg>
          <span class="font-sans">录入新设备</span>
        </button>
      </div>
    </div>

    <!-- 搜索与健康筛选条 -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
      <div class="relative flex-1">
        <div class="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索资产编号 (DEV-*)、设备名称、机架位置..."
          class="w-full bg-black/25 backdrop-blur-sm border border-white/[0.08] focus:border-cyan-500/60 rounded-lg pl-8 pr-8 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
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

      <!-- 健康状态快捷过滤 -->
      <div class="flex items-center space-x-1 shrink-0 text-xs">
        <button
          v-for="h in healthFilterOptions"
          :key="h.value"
          @click="selectedHealth = h.value"
          :class="[
            'px-2 py-1 rounded-md text-[10px] font-mono transition-all border',
            selectedHealth === h.value
              ? 'bg-zinc-800 text-zinc-100 font-medium border-white/[0.15] shadow-sm'
              : 'text-zinc-500 hover:text-zinc-300 border-white/[0.04] hover:bg-zinc-900'
          ]"
        >
          {{ h.label }}
        </button>

        <button
          @click="$emit('refresh')"
          class="px-2.5 py-1.5 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-white/[0.08] hover:border-white/[0.15] text-xs flex items-center space-x-1 transition-all active:scale-95 shadow-sm ml-1"
          title="刷新资产列表"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="hidden sm:inline">刷新</span>
        </button>
      </div>
    </div>

    <!-- 资产表格区域 (Linear Dark Table) -->
    <div ref="tableContainerRef" class="overflow-x-hidden rounded-xl border border-white/[0.08] min-h-[300px] max-h-[580px] overflow-y-auto bg-black/25 backdrop-blur-sm shadow-sm">
      <table class="w-full table-fixed text-left text-xs text-zinc-300 border-separate border-spacing-0">
        <thead class="bg-black/50 text-[11px] text-zinc-300 sticky top-0 uppercase tracking-wider border-b border-white/[0.06] backdrop-blur-md z-10">
          <tr>
            <th class="w-[110px] py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">资产编号</th>
            <th class="w-auto py-2.5 px-3 border-b border-white/[0.06] font-medium glass-text">设备名称 / 型号规格</th>
            <th class="w-[115px] py-2.5 px-2 border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">机房机柜 / IP</th>
            <th class="w-[86px] py-2.5 px-1 text-center border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">健康度调节</th>
            <th class="w-[95px] py-2.5 px-2 border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">借用状态</th>
            <th class="w-[130px] py-2.5 px-3 text-right border-b border-white/[0.06] font-medium glass-text whitespace-nowrap">资产操作</th>
          </tr>
        </thead>
        <tbody class="font-sans">
          <tr v-if="filteredAssets.length === 0">
            <td colspan="6" class="py-12 text-center text-zinc-500 text-xs">
              未检索到符合条件的资产设备
            </td>
          </tr>
          <tr
            v-for="a in filteredAssets"
            :key="a.id"
            :class="[
              'transition-all duration-200 hover:bg-white/[0.06] text-xs border-b border-white/[0.04]',
              a.asset_no === highlightedAssetNo
                ? 'animate-pulse-asset font-medium text-cyan-200 bg-cyan-950/20'
                : ''
            ]"
          >
            <!-- 编号：点击打开设备详情面板 -->
            <td class="py-2.5 px-3 font-mono text-[11px] text-zinc-300 whitespace-nowrap truncate">
              <span
                @click="openDetailModal(a)"
                class="hover:underline hover:text-cyan-400 cursor-pointer inline-flex items-center gap-1.5 transition-colors"
                title="点开查看设备完整硬件参数与运行详情"
              >
                <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="a.health_status === 'HEALTHY' ? 'bg-emerald-400' : a.health_status === 'OVERHEAT' ? 'bg-rose-400 animate-ping' : a.health_status === 'WARNING' ? 'bg-amber-400' : 'bg-zinc-500'"></span>
                <span class="truncate">{{ a.asset_no }}</span>
              </span>
            </td>

            <!-- 名称分类与品牌型号：点击打开详情 -->
            <td class="py-2.5 px-3 overflow-hidden">
              <div
                @click="openDetailModal(a)"
                class="font-medium text-zinc-200 truncate cursor-pointer hover:text-cyan-300 transition-colors"
                :title="`${a.name} (点击查看详情)`"
              >
                {{ a.name }}
              </div>
              <div class="text-[10px] text-zinc-500 font-mono truncate flex items-center space-x-1.5">
                <span class="text-zinc-400 font-sans">{{ a.category }}</span>
                <span v-if="a.detail?.model_name" class="text-zinc-500">| {{ a.detail.model_name }}</span>
                <span v-else-if="a.specs" class="text-zinc-500 truncate max-w-[140px]">| {{ a.specs }}</span>
              </div>
            </td>

            <!-- 位置与IP -->
            <td class="py-2.5 px-2 text-zinc-400 text-[11px] font-mono whitespace-nowrap truncate">
              <div class="truncate" :title="a.location">{{ a.location }}</div>
              <div v-if="a.detail?.management_ip" class="text-[10px] text-cyan-400/80 font-mono truncate select-all">
                IP: {{ a.detail.management_ip }}
              </div>
            </td>

            <!-- 健康状态快速调节 -->
            <td class="py-2.5 px-1 text-center whitespace-nowrap">
              <select
                v-if="isAdmin"
                :value="a.health_status"
                @change="$emit('updateHealth', a.id, $event.target.value)"
                :class="[
                  'px-2 py-0.5 rounded text-[10px] font-medium font-mono border cursor-pointer focus:outline-none transition-colors shadow-sm',
                  healthClass(a.health_status)
                ]"
                title="管理员可切换健康状态"
              >
                <option class="bg-zinc-900 text-zinc-300" value="HEALTHY">HEALTHY</option>
                <option class="bg-zinc-900 text-zinc-300" value="WARNING">WARNING</option>
                <option class="bg-zinc-900 text-zinc-300" value="OVERHEAT">OVERHEAT</option>
                <option class="bg-zinc-900 text-zinc-300" value="OFFLINE">OFFLINE</option>
              </select>
              <span
                v-else
                :class="[
                  'px-2 py-0.5 rounded text-[10px] font-medium font-mono border inline-block shadow-sm select-none',
                  healthClass(a.health_status)
                ]"
                :title="`健康状态: ${a.health_status}`"
              >
                {{ a.health_status }}
              </span>
            </td>

            <!-- 借用状态与借用人 -->
            <td class="py-2.5 px-2 whitespace-nowrap truncate">
              <div class="flex items-center space-x-1.5 truncate">
                <span :class="['px-2 py-0.5 rounded text-[10px] font-mono shrink-0', borrowClass(a.borrow_status)]">
                  {{ a.borrow_status }}
                </span>
                <span v-if="a.borrower" class="text-[10px] text-amber-300 font-medium font-mono truncate" :title="`借调人: ${a.borrower}`">
                  ({{ a.borrower }})
                </span>
              </div>
            </td>

            <!-- 资产多维操作列 (详情 / 编辑 / 借还 / 删除) -->
            <td class="py-2.5 px-3 text-right whitespace-nowrap">
              <div class="flex items-center justify-end space-x-1">
                <!-- 详情按钮 -->
                <button
                  @click="openDetailModal(a)"
                  class="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-cyan-300 transition-colors"
                  title="查看完整硬件参数与详情"
                >
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>

                <!-- 编辑按钮 (非学生可用) -->
                <button
                  v-if="!isStudent"
                  @click="openEditModal(a)"
                  class="p-1 rounded hover:bg-zinc-800 text-zinc-400 hover:text-indigo-300 transition-colors"
                  title="编辑此设备与硬件物理参数"
                >
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>

                <!-- 借用 / 归还快捷动作 -->
                <button
                  v-if="a.borrow_status === 'AVAILABLE'"
                  :disabled="isStudent"
                  @click="!isStudent && openBorrowModal(a)"
                  :class="[
                    'px-2 py-0.5 rounded text-[10px] transition-all font-mono border',
                    isStudent
                      ? 'bg-zinc-800/40 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-50'
                      : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-white/[0.08] active:scale-95 shadow-sm'
                  ]"
                  :title="isStudent ? '学生无权借调机房资产' : '办理设备借调'"
                >
                  借用
                </button>
                <button
                  v-if="a.borrow_status === 'IN_USE'"
                  :disabled="!canReturn(a)"
                  @click="canReturn(a) && $emit('returnAsset', a.asset_no)"
                  :class="[
                    'px-2 py-0.5 rounded text-[10px] transition-all font-mono border',
                    canReturn(a)
                      ? 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border-emerald-500/20 active:scale-95 shadow-sm'
                      : 'bg-zinc-800/40 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-50'
                  ]"
                  :title="returnButtonTitle(a)"
                >
                  归还
                </button>

                <!-- 删除按钮 (仅管理员可用) -->
                <button
                  v-if="isAdmin"
                  @click="openDeleteConfirm(a)"
                  class="p-1 rounded hover:bg-rose-500/20 text-zinc-500 hover:text-rose-400 transition-colors"
                  title="删除设备资产记录"
                >
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 1. 设备全景详情面板 (DeviceDetailModal) -->
    <DeviceDetailModal
      v-model="showDetailModal"
      :asset="selectedAssetForDetail"
      :currentUser="currentUser"
      @inspect="handleInspectFromModal"
      @borrow="handleBorrowFromModal"
      @return="handleReturnFromModal"
      @edit="handleEditFromModal"
      @delete="openDeleteConfirm"
    />

    <!-- 2. 设备录入/编辑模态表单 (DeviceFormModal) -->
    <DeviceFormModal
      v-model="showFormModal"
      :mode="formMode"
      :asset="selectedAssetForEdit"
      @saved="handleAssetSaved"
    />

    <!-- 3. 删除二次确认模态框 -->
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
          v-if="showDeleteModal"
          @keydown.esc.window="showDeleteModal = false"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md overflow-hidden"
          @click.self="showDeleteModal = false"
        >
          <div class="w-full max-w-sm rounded-3xl bg-zinc-900/95 border border-rose-500/30 ring-1 ring-rose-500/10 p-5 space-y-4 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] backdrop-blur-2xl">
            <div class="flex items-center space-x-3 text-rose-400">
              <div class="p-2.5 rounded-2xl bg-rose-500/10 border border-rose-500/20">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-semibold text-zinc-100 tracking-tight">确认彻底删除该设备？</h4>
                <p class="text-[11px] text-zinc-400">此操作不可撤销，硬件档案亦将清理</p>
              </div>
            </div>

            <div class="p-3 rounded-2xl bg-zinc-950/60 border border-white/[0.06] text-xs space-y-1">
              <div>目标编号: <span class="font-mono text-cyan-400 font-semibold select-all">{{ targetAssetForDelete?.asset_no }}</span></div>
              <div class="text-zinc-200 font-medium">{{ targetAssetForDelete?.name }}</div>
              <div class="text-zinc-500 font-mono text-[11px]">{{ targetAssetForDelete?.location }}</div>
              <div v-if="targetAssetForDelete?.borrow_status === 'IN_USE'" class="pt-1 text-rose-400 font-medium">
                ⚠️ 该设备处于借用中 (借用人: {{ targetAssetForDelete?.borrower || '未填写' }})！
              </div>
            </div>

            <div v-if="deleteError" class="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              {{ deleteError }}
            </div>

            <div class="flex items-center justify-end space-x-2 pt-2 border-t border-white/[0.06]">
              <button
                @click="showDeleteModal = false"
                class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition-all"
              >
                取消
              </button>
              <button
                @click="confirmDelete"
                :disabled="isDeleting"
                class="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs shadow-md transition-all active:scale-95 disabled:opacity-50"
              >
                {{ isDeleting ? '正在删除...' : '确认移除设备' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 4. 借用登记快速弹窗 -->
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
          v-if="showBorrowModal"
          @keydown.esc.window="showBorrowModal = false"
          class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md overflow-hidden"
          @click.self="showBorrowModal = false"
        >
          <div class="w-full max-w-sm rounded-3xl bg-zinc-900/95 border border-white/[0.12] ring-1 ring-white/[0.05] p-5 space-y-4 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] backdrop-blur-2xl">
            <div class="flex items-center justify-between border-b border-white/[0.08] pb-2.5">
              <div class="flex items-center space-x-2.5">
                <span class="p-2 rounded-2xl bg-zinc-950/80 border border-white/[0.08] text-cyan-400">
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </span>
                <h4 class="text-sm font-semibold text-zinc-100 tracking-tight">办理设备借出登记</h4>
              </div>
              <button
                @click="showBorrowModal = false"
                class="text-zinc-400 hover:text-zinc-100 p-1.5 rounded-full hover:bg-white/[0.08] transition-colors"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="text-xs text-zinc-400 bg-zinc-950/60 p-3 rounded-2xl border border-white/[0.04] space-y-1">
              <div>目标设备：<span class="font-mono text-cyan-400 font-semibold select-all">{{ targetAsset?.asset_no }}</span></div>
              <div class="text-zinc-200 font-medium">{{ targetAsset?.name }}</div>
              <div class="text-zinc-500 font-mono text-[11px]">{{ targetAsset?.location }}</div>
            </div>

            <div class="space-y-1.5 text-xs">
              <label class="text-zinc-300 font-medium block">借用人 / 科研教学团队 <span class="text-rose-400">*</span></label>
              <input
                v-model="borrowerInput"
                type="text"
                placeholder="填写借用教师姓名与部门..."
                class="w-full bg-zinc-950/80 border border-white/[0.08] focus:border-cyan-500 rounded-xl px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>

            <div class="flex items-center justify-end space-x-2 pt-2 border-t border-white/[0.06]">
              <button
                @click="showBorrowModal = false"
                class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition-all"
              >
                取消
              </button>
              <button
                @click="confirmBorrow"
                :disabled="!borrowerInput.trim() || isStudent"
                class="px-4 py-2 rounded-xl bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs disabled:opacity-40 transition-all shadow-md active:scale-95"
              >
                确认登记借出
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import DeviceDetailModal from './DeviceDetailModal.vue'
import DeviceFormModal from './DeviceFormModal.vue'
import { api } from '../../api/client'

const props = defineProps({
  assets: {
    type: Array,
    default: () => [],
  },
  currentUser: {
    type: Object,
    default: () => ({
      username: 'admin',
      real_name: '王主管',
      role: 'ADMIN',
      department: '网络中心运维部',
    }),
  },
  highlightedAssetNo: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['refresh', 'borrowAsset', 'returnAsset', 'updateHealth', 'inspectAsset'])

const userRole = computed(() => (props.currentUser?.role || 'STUDENT').toUpperCase())
const isStudent = computed(() => userRole.value === 'STUDENT')
const isTeacher = computed(() => userRole.value === 'TEACHER')
const isAdmin = computed(() => userRole.value === 'ADMIN')

function canReturn(asset) {
  if (isStudent.value) return false
  if (isAdmin.value) return true
  if (isTeacher.value) {
    if (!asset.borrower) return false
    const teacherName = props.currentUser?.real_name || ''
    const teacherUser = props.currentUser?.username || ''
    return (
      (teacherName && asset.borrower.includes(teacherName)) ||
      (teacherUser && asset.borrower.includes(teacherUser))
    )
  }
  return false
}

function returnButtonTitle(asset) {
  if (isStudent.value) return '学生无权办理设备归还，请联系教师或管理员'
  if (isAdmin.value) return '管理员办理设备归还入库'
  if (isTeacher.value) {
    return canReturn(asset) ? '归还本人借调设备' : '仅借调教师本人或管理员可办理归还'
  }
  return '办理归还'
}

const tableContainerRef = ref(null)
const selectedCategory = ref('ALL')
const selectedHealth = ref('ALL')
const keyword = ref('')

// 1. 详情面板状态
const showDetailModal = ref(false)
const selectedAssetForDetail = ref(null)

function openDetailModal(asset) {
  selectedAssetForDetail.value = asset
  showDetailModal.value = true
}

function handleInspectFromModal(assetNo) {
  emit('inspectAsset', assetNo)
}

function handleBorrowFromModal(asset) {
  showDetailModal.value = false
  openBorrowModal(asset)
}

function handleReturnFromModal(assetNo) {
  showDetailModal.value = false
  emit('returnAsset', assetNo)
}

function handleEditFromModal(asset) {
  showDetailModal.value = false
  openEditModal(asset)
}

// 2. 表单模态框状态 (新增 / 编辑)
const showFormModal = ref(false)
const formMode = ref('create')
const selectedAssetForEdit = ref(null)

function openCreateModal() {
  if (isStudent.value) return
  formMode.value = 'create'
  selectedAssetForEdit.value = null
  showFormModal.value = true
}

function openEditModal(asset) {
  if (isStudent.value) return
  formMode.value = 'edit'
  selectedAssetForEdit.value = asset
  showFormModal.value = true
}

function handleAssetSaved() {
  emit('refresh')
}

// 3. 删除二次确认弹窗
const showDeleteModal = ref(false)
const targetAssetForDelete = ref(null)
const isDeleting = ref(false)
const deleteError = ref('')

function openDeleteConfirm(asset) {
  if (!isAdmin.value) return
  targetAssetForDelete.value = asset
  deleteError.value = ''
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!targetAssetForDelete.value || !isAdmin.value) return
  isDeleting.value = true
  deleteError.value = ''
  try {
    await api.deleteAsset(targetAssetForDelete.value.id)
    showDeleteModal.value = false
    showDetailModal.value = false
    emit('refresh')
  } catch (err) {
    deleteError.value = err.message || '删除设备失败'
  } finally {
    isDeleting.value = false
  }
}

// 4. 借用弹窗
const showBorrowModal = ref(false)
const targetAsset = ref(null)
const borrowerInput = ref('')

function openBorrowModal(asset) {
  targetAsset.value = asset
  const name = props.currentUser?.real_name || '机房教师'
  const dept = props.currentUser?.department ? ` (${props.currentUser.department})` : ''
  borrowerInput.value = `${name}${dept}`
  showBorrowModal.value = true
}

function confirmBorrow() {
  if (isStudent.value) return
  if (!targetAsset.value || !borrowerInput.value.trim()) return
  emit('borrowAsset', targetAsset.value.asset_no, borrowerInput.value.trim())
  showBorrowModal.value = false
}

watch(
  () => props.highlightedAssetNo,
  (newVal) => {
    if (newVal) {
      selectedCategory.value = 'ALL'
      selectedHealth.value = 'ALL'
      keyword.value = ''
      nextTick(() => {
        if (tableContainerRef.value) {
          tableContainerRef.value.scrollTop = 0
        }
      })
    }
  }
)

watch(
  () => props.currentUser,
  (newUser) => {
    if (newUser?.role === 'STUDENT') {
      showBorrowModal.value = false
      showFormModal.value = false
    } else if (showBorrowModal.value) {
      const name = newUser?.real_name || '机房教师'
      const dept = newUser?.department ? ` (${newUser.department})` : ''
      borrowerInput.value = `${name}${dept}`
    }
  }
)

const categoryOptions = [
  { label: '全部', value: 'ALL' },
  { label: '服务器', value: '服务器' },
  { label: '网络设备', value: '网络设备' },
  { label: '配电温控', value: '配电温控' },
  { label: '实验教学', value: '实验教学' },
]

const healthFilterOptions = [
  { label: '全部健康度', value: 'ALL' },
  { label: '良好', value: 'HEALTHY' },
  { label: '预警', value: 'WARNING' },
  { label: '超温', value: 'OVERHEAT' },
  { label: '离线', value: 'OFFLINE' },
]

const filteredAssets = computed(() => {
  return props.assets.filter((a) => {
    if (selectedCategory.value !== 'ALL' && a.category !== selectedCategory.value) {
      return false
    }
    if (selectedHealth.value !== 'ALL' && a.health_status !== selectedHealth.value) {
      return false
    }
    if (keyword.value.trim()) {
      const kw = keyword.value.trim().toLowerCase()
      const matchNo = (a.asset_no || '').toLowerCase().includes(kw)
      const matchName = (a.name || '').toLowerCase().includes(kw)
      const matchLoc = (a.location || '').toLowerCase().includes(kw)
      const matchIp = (a.detail?.management_ip || '').toLowerCase().includes(kw)
      const matchModel = (a.detail?.model_name || '').toLowerCase().includes(kw)
      return matchNo || matchName || matchLoc || matchIp || matchModel
    }
    return true
  })
})

function healthClass(status) {
  switch (status) {
    case 'HEALTHY':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'WARNING':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20'
    case 'OVERHEAT':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20 font-semibold'
    case 'OFFLINE':
      return 'bg-zinc-800 text-zinc-500 border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border-white/[0.06]'
  }
}

function borrowClass(status) {
  switch (status) {
    case 'AVAILABLE':
      return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
    case 'IN_USE':
      return 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
    case 'MAINTENANCE':
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
    default:
      return 'bg-zinc-800 text-zinc-400 border border-white/[0.06]'
  }
}
</script>
