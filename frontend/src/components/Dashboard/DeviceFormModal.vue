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
      <div
        v-if="modelValue"
        @keydown.esc.window="close"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/70 backdrop-blur-md overflow-hidden"
        @mousedown="handleBackdropMouseDown"
        @mouseup="handleBackdropMouseUp"
      >
        <div
          class="w-full max-w-2xl rounded-3xl bg-zinc-900/95 border border-white/[0.12] ring-1 ring-white/[0.05] p-5 sm:p-6 space-y-4 shadow-[0_25px_80px_-15px_rgba(0,0,0,0.85)] flex flex-col max-h-[90vh] overflow-hidden backdrop-blur-2xl transition-all"
        >
          <!-- 移动端顶部抓手装饰条 -->
          <div class="w-10 h-1 rounded-full bg-white/20 mx-auto -mt-1 sm:hidden"></div>

          <!-- 头部 -->
          <div class="flex items-center justify-between border-b border-white/[0.08] pb-3 shrink-0">
            <div class="flex items-center space-x-3">
              <span class="p-2.5 rounded-2xl bg-zinc-950/80 border border-white/[0.1] text-indigo-400 shadow-sm">
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </span>
              <div>
                <h3 class="text-base sm:text-lg font-semibold text-zinc-100 tracking-tight">
                  {{ isEdit ? '编辑机房资产与硬件规格' : '录入新设备与硬件物理参数' }}
                </h3>
                <p class="text-[11px] text-zinc-400">
                  {{ isEdit ? '更新设备的基础流转状态或底座硬件物理参数' : '录入新设备到机房台账，系统将自动分配并持久化硬件档案' }}
                </p>
              </div>
            </div>

            <button
              @click="close"
              class="text-zinc-400 hover:text-zinc-100 p-2 rounded-full hover:bg-white/[0.08] transition-all shrink-0 active:scale-90"
              title="关闭 (Esc)"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

      <!-- 分段切换器 (Tabs) -->
      <div class="flex items-center space-x-1 text-xs bg-zinc-900/80 p-1 rounded-xl border border-white/[0.06] shrink-0">
        <button
          type="button"
          @click="activeTab = 'basic'"
          :class="[
            'flex-1 py-1.5 rounded-lg transition-all font-medium flex items-center justify-center space-x-1.5',
            activeTab === 'basic'
              ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-white/[0.08]'
              : 'text-zinc-400 hover:text-zinc-200'
          ]"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <span>1. 基础台账与位置</span>
        </button>
        <button
          type="button"
          @click="activeTab = 'hardware'"
          :class="[
            'flex-1 py-1.5 rounded-lg transition-all font-medium flex items-center justify-center space-x-1.5',
            activeTab === 'hardware'
              ? 'bg-zinc-800 text-cyan-300 shadow-sm border border-cyan-500/20'
              : 'text-zinc-400 hover:text-zinc-200'
          ]"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          <span>2. 硬件物理规格参数</span>
        </button>
      </div>

      <!-- 表单主体区 -->
      <form @submit.prevent="handleSubmit" class="flex-1 overflow-y-auto pr-1 space-y-4 custom-scrollbar text-xs">
        <!-- TAB 1: 基础台账与位置 -->
        <div v-show="activeTab === 'basic'" class="space-y-3.5">
          <!-- 资产编号与自动生成 -->
          <div class="space-y-1">
            <div class="flex items-center justify-between">
              <label class="font-medium text-zinc-300">资产编号 <span class="text-rose-400">*</span></label>
              <button
                v-if="!isEdit"
                type="button"
                @click="autoGenerateNo"
                class="text-[11px] text-cyan-400 hover:text-cyan-300 hover:underline flex items-center space-x-1"
              >
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>自动生成规整编号</span>
              </button>
            </div>
            <input
              v-model="form.asset_no"
              type="text"
              :disabled="isEdit"
              placeholder="如: DEV-SRV-206"
              required
              class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            />
          </div>

          <!-- 设备名称与分类 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">设备名称 <span class="text-rose-400">*</span></label>
              <input
                v-model="form.name"
                type="text"
                placeholder="如: 2号机房-GPU计算节点06"
                required
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">设备类别 <span class="text-rose-400">*</span></label>
              <select
                v-model="form.category"
                required
                class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none transition-colors"
              >
                <option value="服务器">服务器</option>
                <option value="网络设备">网络设备</option>
                <option value="配电温控">配电温控</option>
                <option value="实验教学">实验教学</option>
              </select>
            </div>
          </div>

          <!-- 机房位置与责任人/借调人：按设备类别区分机架智能配置与周边配套位置 -->
          <div class="p-3 rounded-2xl bg-zinc-950/70 border border-white/[0.08] space-y-3">
            <div class="flex items-center justify-between text-xs">
              <span class="font-medium text-zinc-200 flex items-center space-x-1.5">
                <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>物理位置与机架机位配置 <span class="text-rose-400">*</span></span>
              </span>
              <span class="text-[10px] text-zinc-400 font-mono">
                {{ isRackCategory ? '机架式设备 (智能联动槽位)' : '非机架外设 (周边配套区)' }}
              </span>
            </div>

            <!-- 1. 该上机柜的设备：服务器 / 网络设备 (结构化机架机位选择器) -->
            <div v-if="isRackCategory" class="space-y-2.5">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <!-- 所属机房下拉 -->
                <div class="space-y-1">
                  <label class="text-[11px] text-zinc-400">所属机房</label>
                  <select
                    v-model="rackRoom"
                    @change="onRackRoomChange"
                    class="w-full bg-zinc-900 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-2.5 py-1.5 text-zinc-200 focus:outline-none transition-colors text-xs"
                  >
                    <option
                      v-for="rm in dynamicRooms"
                      :key="rm.room_code"
                      :value="rm.room_code"
                    >
                      {{ rm.room_code }} - {{ rm.room_name }}
                    </option>
                  </select>
                </div>

                <!-- 目标机柜下拉 (联动) -->
                <div class="space-y-1">
                  <label class="text-[11px] text-zinc-400">目标机柜 ({{ currentRackTotalU }}U)</label>
                  <select
                    v-model="rackId"
                    @change="updateRackLocation"
                    class="w-full bg-zinc-900 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-2.5 py-1.5 text-zinc-200 focus:outline-none transition-colors text-xs"
                  >
                    <option
                      v-for="r in availableRacks"
                      :key="r.id || 'none'"
                      :value="r.id"
                      :disabled="r.disabled"
                    >
                      {{ r.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <!-- 占用高度 (U) -->
                <div class="space-y-1">
                  <label class="text-[11px] text-zinc-400">占用高度 (U)</label>
                  <select
                    v-model.number="rackUHeight"
                    @change="onUHeightChange"
                    class="w-full bg-zinc-900 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-2.5 py-1.5 text-zinc-200 focus:outline-none transition-colors text-xs font-mono"
                  >
                    <option :value="1">1U (交换机 / 紧凑节点)</option>
                    <option :value="2">2U (通用计算服务器)</option>
                    <option :value="4">4U (4卡GPU算力 / 存储节点)</option>
                    <option :value="3">3U</option>
                    <option :value="5">5U</option>
                    <option :value="6">6U</option>
                    <option :value="8">8U</option>
                  </select>
                </div>

                <!-- 起始插槽 (Start U) -->
                <div class="space-y-1">
                  <label class="text-[11px] text-zinc-400">起始插槽 (Start U)</label>
                  <select
                    v-model.number="rackStartU"
                    @change="updateRackLocation"
                    class="w-full bg-zinc-900 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-2.5 py-1.5 text-zinc-200 focus:outline-none transition-colors text-xs font-mono"
                  >
                    <option
                      v-for="u in maxAllowedStartU"
                      :key="'u-' + u"
                      :value="u"
                    >
                      U{{ u }} (占用 U{{ u }} ~ U{{ u + rackUHeight - 1 }})
                    </option>
                  </select>
                </div>
              </div>

              <!-- 联动拼接规范位置展示 -->
              <div class="flex items-center justify-between px-3 py-2 rounded-lg bg-zinc-900/90 border border-cyan-500/20 text-[11px] font-mono">
                <span class="text-zinc-400">联动规范位置:</span>
                <span class="text-cyan-300 font-bold tracking-wide">{{ form.location }}</span>
              </div>
            </div>

            <!-- 2. 不该上机柜的设备：配电温控 / 实验教学 (彻底隐藏机柜与U位) -->
            <div v-else class="space-y-2.5">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <!-- 所属机房/库房 -->
                <div class="space-y-1">
                  <label class="text-[11px] text-zinc-400">所属机房/库房</label>
                  <select
                    v-model="unrackedRoom"
                    @change="updateUnrackedLocation"
                    class="w-full bg-zinc-900 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-2.5 py-1.5 text-zinc-200 focus:outline-none transition-colors text-xs"
                  >
                    <option
                      v-for="rm in dynamicRooms"
                      :key="rm.room_code"
                      :value="rm.room_code"
                    >
                      {{ rm.room_code }} - {{ rm.room_name }}
                    </option>
                  </select>
                </div>

                <!-- 具体摆放位置文本 -->
                <div class="space-y-1">
                  <label class="text-[11px] text-zinc-400">具体摆放位置区域</label>
                  <input
                    v-model="unrackedArea"
                    @input="updateUnrackedLocation"
                    type="text"
                    list="unracked-area-list"
                    placeholder="如: 动力配电区 / 精密空调区 / 实验台01"
                    required
                    class="w-full bg-zinc-900 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-2.5 py-1.5 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors text-xs font-mono"
                  />
                  <datalist id="unracked-area-list">
                    <option value="动力配电区" />
                    <option value="列间精密空调区" />
                    <option value="动环监控机柜旁" />
                    <option value="实验教学台01" />
                    <option value="实验教学台02" />
                    <option value="仪器测试操作台" />
                    <option value="备用仓储货架A-01" />
                  </datalist>
                </div>
              </div>

              <!-- 联动拼接位置展示 -->
              <div class="flex items-center justify-between px-3 py-2 rounded-lg bg-zinc-900/90 border border-purple-500/20 text-[11px] font-mono">
                <span class="text-zinc-400">周边配套登记位置:</span>
                <span class="text-purple-300 font-bold tracking-wide">{{ form.location }}</span>
              </div>
            </div>

            <!-- 仅在编辑模式下呈现借用人；录入模式下设备必然在库可借，无需填写 -->
            <div v-if="isEdit" class="space-y-1 pt-1 border-t border-white/[0.06]">
              <label class="font-medium text-zinc-300">借用人 / 使用团队</label>
              <input
                v-model="form.borrower"
                type="text"
                placeholder="留空表示库房空闲在册"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <!-- 健康状态与借还状态 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">初始健康状态</label>
              <select
                v-model="form.health_status"
                class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
              >
                <option value="HEALTHY">HEALTHY (良好)</option>
                <option value="WARNING">WARNING (预警)</option>
                <option value="OVERHEAT">OVERHEAT (高温超温)</option>
                <option value="OFFLINE">OFFLINE (离线脱网)</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">借还流转状态</label>
              <select
                v-if="isEdit"
                v-model="form.borrow_status"
                class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
              >
                <option value="AVAILABLE">AVAILABLE (空闲可借)</option>
                <option value="IN_USE">IN_USE (借调占用)</option>
                <option value="MAINTENANCE">MAINTENANCE (故障维护)</option>
              </select>
              <!-- 录入模式下锁定为 AVAILABLE，借还流转交由资产列表借还流程管理 -->
              <div
                v-else
                class="w-full bg-zinc-950/60 border border-white/[0.08] rounded-lg px-3 py-2 text-zinc-400 font-mono flex items-center justify-between select-none cursor-default"
                title="录入模式下默认锁定为在库可借 (AVAILABLE)，借还流转交由资产列表借还流程管理"
              >
                <span class="text-emerald-400 font-medium">AVAILABLE (在库可借)</span>
                <span class="text-[10px] text-zinc-500 bg-white/[0.04] px-1.5 py-0.5 rounded">入库锁定</span>
              </div>
            </div>
          </div>

          <!-- 动环探针遥测注入与核心运行温度设定面板 -->
          <div class="p-3.5 rounded-2xl bg-zinc-950/60 border border-white/[0.08] space-y-2.5 shadow-inner">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2 text-zinc-200">
                <span class="p-1 rounded-lg bg-zinc-900 text-cyan-400 border border-white/[0.06] shadow-sm">
                  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </span>
                <span class="font-medium text-xs">动环探针遥测 / 核心运行温度设定</span>
              </div>
              <span
                :class="[
                  'px-2.5 py-0.5 rounded-full text-[10px] font-mono border font-medium flex items-center space-x-1 shadow-sm transition-all',
                  form.health_status === 'OFFLINE'
                    ? 'bg-zinc-800/80 text-zinc-400 border-white/[0.08]'
                    : form.custom_temperature >= 40.0
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                    : form.custom_temperature >= 38.0
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                ]"
              >
                <span>{{ form.health_status === 'OFFLINE' ? '⚪ 离线脱机' : form.custom_temperature >= 40.0 ? '🔴 超温高危 (联动 OVERHEAT)' : form.custom_temperature >= 38.0 ? '🟡 临界预警 (联动 WARNING)' : '🟢 正常受控 (联动 HEALTHY)' }}</span>
              </span>
            </div>

            <!-- 温度输入框 (无原生箭头，右侧规整展示 °C 单位) -->
            <div class="relative">
              <input
                v-model.number="form.custom_temperature"
                type="number"
                step="0.1"
                min="10"
                max="90"
                placeholder="请输入设备核心运行温度 (如: 31.5)"
                class="w-full bg-zinc-950 border border-white/[0.08] focus:border-cyan-500 rounded-xl pl-3.5 pr-10 py-2.5 text-zinc-100 font-mono text-sm placeholder-zinc-500 focus:outline-none transition-all shadow-inner [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              />
              <span class="absolute right-3.5 top-1/2 -translate-y-1/2 text-xs text-zinc-400 font-mono font-medium pointer-events-none select-none">
                °C
              </span>
            </div>

            <!-- 快速设定预设档位 -->
            <div class="flex items-center space-x-1.5 flex-wrap gap-y-1.5 pt-0.5">
              <span class="text-[10px] text-zinc-400 font-sans mr-0.5">快速预设:</span>
              <button
                type="button"
                @click="setQuickTemperature(24.0)"
                class="px-2.5 py-1 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 text-[11px] text-zinc-300 hover:text-white border border-white/[0.08] hover:border-white/[0.16] active:scale-95 transition-all font-mono"
              >
                标准室温 24℃
              </button>
              <button
                type="button"
                @click="setQuickTemperature(31.5)"
                class="px-2.5 py-1 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-[11px] text-emerald-300 hover:text-emerald-200 border border-emerald-500/30 hover:border-emerald-500/50 active:scale-95 transition-all font-mono"
              >
                健康轻载 31.5℃
              </button>
              <button
                type="button"
                @click="setQuickTemperature(38.5)"
                class="px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-[11px] text-amber-300 hover:text-amber-200 border border-amber-500/30 hover:border-amber-500/50 active:scale-95 transition-all font-mono"
              >
                临界预警 38.5℃
              </button>
              <button
                type="button"
                @click="setQuickTemperature(43.5)"
                class="px-2.5 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-[11px] text-rose-300 hover:text-rose-200 border border-rose-500/30 hover:border-rose-500/50 active:scale-95 transition-all font-mono"
              >
                超温高危 43.5℃
              </button>
            </div>
          </div>

          <!-- 简要硬件规格说明 -->
          <div class="space-y-1">
            <label class="font-medium text-zinc-300">硬件概要标签</label>
            <input
              v-model="form.specs"
              type="text"
              placeholder="如: 2x Xeon Gold 6330, 256GB RAM, 4x RTX 4090"
              class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors font-mono"
            />
          </div>
        </div>

        <!-- TAB 2: 硬件物理规格详细参数 -->
        <div v-show="activeTab === 'hardware'" class="space-y-3.5">
          <!-- ⚡ 常用设备规格 -->
          <div class="p-3 rounded-2xl bg-gradient-to-r from-cyan-950/40 via-zinc-900 to-indigo-950/40 border border-cyan-500/20 space-y-2 shadow-inner">
            <div class="flex items-center justify-between text-xs">
              <span class="font-medium text-cyan-300 flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>常用设备规格</span>
              </span>
              <!-- 清空选框按钮 -->
              <button
                type="button"
                @click="clearHardwareSpecs"
                class="px-2.5 py-1 rounded-lg bg-zinc-800/80 hover:bg-rose-500/20 border border-white/[0.08] hover:border-rose-500/40 text-[11px] text-zinc-300 hover:text-rose-300 transition-all active:scale-95 flex items-center space-x-1 shadow-sm"
                title="清空当前硬件物理参数所有选框内容"
              >
                <svg class="w-3 h-3 text-zinc-400 group-hover:text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>清空选框</span>
              </button>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
              <button
                type="button"
                @click="applyHardwareTemplate('compute_node')"
                class="px-2.5 py-1.5 rounded-xl bg-zinc-900/90 hover:bg-cyan-500/15 border border-white/[0.08] hover:border-cyan-500/40 text-[11px] text-zinc-300 hover:text-cyan-200 transition-all active:scale-95 flex items-center justify-center space-x-1 shadow-sm text-center"
              >
                <span>🖥️</span>
                <span class="truncate">2U 通用计算节点</span>
              </button>
              <button
                type="button"
                @click="applyHardwareTemplate('gpu_server')"
                class="px-2.5 py-1.5 rounded-xl bg-zinc-900/90 hover:bg-indigo-500/15 border border-white/[0.08] hover:border-indigo-500/40 text-[11px] text-zinc-300 hover:text-indigo-200 transition-all active:scale-95 flex items-center justify-center space-x-1 shadow-sm text-center"
              >
                <span>⚡</span>
                <span class="truncate">4卡 GPU服务器</span>
              </button>
              <button
                type="button"
                @click="applyHardwareTemplate('switch')"
                class="px-2.5 py-1.5 rounded-xl bg-zinc-900/90 hover:bg-emerald-500/15 border border-white/[0.08] hover:border-emerald-500/40 text-[11px] text-zinc-300 hover:text-emerald-200 transition-all active:scale-95 flex items-center justify-center space-x-1 shadow-sm text-center"
              >
                <span>🔀</span>
                <span class="truncate">万兆核心交换机</span>
              </button>
              <button
                type="button"
                @click="applyHardwareTemplate('cooling_pdu')"
                class="px-2.5 py-1.5 rounded-xl bg-zinc-900/90 hover:bg-amber-500/15 border border-white/[0.08] hover:border-amber-500/40 text-[11px] text-zinc-300 hover:text-amber-200 transition-all active:scale-95 flex items-center justify-center space-x-1 shadow-sm text-center"
              >
                <span>❄️</span>
                <span class="truncate">精密空调/智能PDU</span>
              </button>
            </div>
          </div>

          <!-- 品牌型号与SN序列号 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">出厂 SN 序列号</label>
              <input
                v-model="detailForm.serial_number"
                type="text"
                placeholder="如: SN-DELL-2024-998"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">厂商品牌</label>
              <input
                v-model="detailForm.brand"
                type="text"
                list="brand-datalist"
                placeholder="如: Dell / Huawei / Inspur"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
              <datalist id="brand-datalist">
                <option value="Dell" />
                <option value="Huawei" />
                <option value="Inspur" />
                <option value="H3C" />
                <option value="Cisco" />
                <option value="Lenovo" />
              </datalist>
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">具体设备型号</label>
              <input
                v-model="detailForm.model_name"
                type="text"
                placeholder="如: PowerEdge R750xa"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors font-mono"
              />
            </div>
          </div>

          <!-- 管理IP与MAC地址与固件 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">带外/管理 IP</label>
              <input
                v-model="detailForm.management_ip"
                type="text"
                placeholder="如: 192.168.10.206"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-cyan-300 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">物理 MAC 地址</label>
              <input
                v-model="detailForm.mac_address"
                type="text"
                placeholder="如: 00:1A:2B:3C:4D:5E"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">系统 / 固件版本</label>
              <input
                v-model="detailForm.os_firmware"
                type="text"
                list="os-datalist"
                placeholder="如: Ubuntu 22.04 LTS"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
              <datalist id="os-datalist">
                <option value="Ubuntu 22.04 LTS" />
                <option value="CentOS 7.9" />
                <option value="OpenEuler 22.03" />
                <option value="Huawei VRP" />
                <option value="H3C Comware" />
              </datalist>
            </div>
          </div>

          <!-- CPU与内存 (智能灰化联动) -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300 flex items-center justify-between">
                <span>核心处理器 (CPU) 规格</span>
                <span v-if="isComputeDisabled" class="text-[10px] text-amber-400/80">无需配置</span>
              </label>
              <input
                v-model="detailForm.cpu_info"
                type="text"
                :disabled="isComputeDisabled"
                :placeholder="isComputeDisabled ? computePlaceholder : '如: 2x Intel Xeon Gold 6330 (56核/112线程)'"
                class="w-full rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
                :class="isComputeDisabled ? 'opacity-40 cursor-not-allowed bg-zinc-900/30 border border-white/[0.04] text-zinc-500 placeholder-zinc-500' : 'bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 placeholder-zinc-500'"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300 flex items-center justify-between">
                <span>运行内存 (RAM) 规格</span>
                <span v-if="isComputeDisabled" class="text-[10px] text-amber-400/80">无需配置</span>
              </label>
              <input
                v-model="detailForm.memory_info"
                type="text"
                :disabled="isComputeDisabled"
                :placeholder="isComputeDisabled ? computePlaceholder : '如: 256GB (8x 32GB DDR4 3200MHz ECC)'"
                class="w-full rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
                :class="isComputeDisabled ? 'opacity-40 cursor-not-allowed bg-zinc-900/30 border border-white/[0.04] text-zinc-500 placeholder-zinc-500' : 'bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 placeholder-zinc-500'"
              />
            </div>
          </div>

          <!-- 磁盘存储与GPU (智能灰化联动) -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300 flex items-center justify-between">
                <span>磁盘存储配置与阵列</span>
                <span v-if="isComputeDisabled" class="text-[10px] text-amber-400/80">无需配置</span>
              </label>
              <input
                v-model="detailForm.storage_info"
                type="text"
                :disabled="isComputeDisabled"
                :placeholder="isComputeDisabled ? computePlaceholder : '如: 2x 960G NVMe RAID1 + 4x 3.84T U.2 RAID5'"
                class="w-full rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
                :class="isComputeDisabled ? 'opacity-40 cursor-not-allowed bg-zinc-900/30 border border-white/[0.04] text-zinc-500 placeholder-zinc-500' : 'bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 placeholder-zinc-500'"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300 flex items-center justify-between">
                <span>算力加速卡 (GPU)</span>
                <span v-if="isComputeDisabled" class="text-[10px] text-amber-400/80">无需配置</span>
              </label>
              <input
                v-model="detailForm.gpu_info"
                type="text"
                :disabled="isComputeDisabled"
                :placeholder="isComputeDisabled ? computePlaceholder : '如: 4x NVIDIA RTX 4090 24GB GDDR6X'"
                class="w-full rounded-lg px-3 py-2 text-zinc-200 focus:outline-none font-mono transition-colors"
                :class="isComputeDisabled ? 'opacity-40 cursor-not-allowed bg-zinc-900/30 border border-white/[0.04] text-zinc-500 placeholder-zinc-500' : 'bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 placeholder-zinc-500'"
              />
            </div>
          </div>

          <!-- 网络端口与供电规格 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">网络物理接口与速率</label>
              <input
                v-model="detailForm.network_interfaces"
                type="text"
                placeholder="如: 2x 25GE SFP28 双光口 + 2x 10GE 电口"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">动力供电与功耗规格</label>
              <input
                v-model="detailForm.power_supply"
                type="text"
                placeholder="如: 双路冗余 2400W 80Plus 钛金电源 (1+1)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
          </div>

          <!-- 维保信息与供应商 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">投产/采购日期</label>
              <input
                v-model="detailForm.purchase_date"
                type="text"
                placeholder="如: 2024-03-15"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">维保期限与到期日</label>
              <input
                v-model="detailForm.warranty_period"
                type="text"
                placeholder="如: 2027-03-14 (3年金牌维保)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              />
            </div>
            <div class="space-y-1">
              <label class="font-medium text-zinc-300">供应商及技术支持</label>
              <input
                v-model="detailForm.supplier"
                type="text"
                placeholder="如: 戴尔企业服务 (400-881-1852)"
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <!-- 高级技术选项 (可选折叠面板) -->
          <div class="rounded-xl border border-white/[0.06] bg-zinc-950/40 overflow-hidden">
            <button
              type="button"
              @click="isAdvancedOpen = !isAdvancedOpen"
              class="w-full px-3.5 py-2.5 flex items-center justify-between text-left text-xs font-medium text-zinc-400 hover:text-zinc-200 transition-colors bg-white/[0.01] hover:bg-white/[0.03]"
            >
              <span class="flex items-center space-x-1.5">
                <svg class="w-3.5 h-3.5 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>高级技术选项 (扩展定制参数 JSON，可选折叠)</span>
              </span>
              <svg
                class="w-3.5 h-3.5 text-zinc-500 transition-transform duration-200"
                :class="{ 'rotate-180': isAdvancedOpen }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div v-show="isAdvancedOpen" class="p-3.5 border-t border-white/[0.06] space-y-2 animate-fade-in">
              <label class="font-medium text-zinc-300">扩展定制参数 (JSON 键值对格式)</label>
              <textarea
                v-model="detailForm.extra_params"
                rows="2"
                placeholder='如: {"rack_units": "4U", "cooling": "风冷进气加压"}'
                class="w-full bg-zinc-950/60 border border-white/[0.08] focus:border-cyan-500 rounded-lg px-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none font-mono transition-colors"
              ></textarea>
            </div>
          </div>
        </div>

        <div v-if="errorMsg" class="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
          {{ errorMsg }}
        </div>

        <!-- 底部提交与取消 -->
        <div class="pt-3 border-t border-white/[0.08] flex items-center justify-end space-x-2.5 shrink-0">
          <button
            type="button"
            @click="close"
            class="px-4 py-2 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition-all"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-medium text-xs shadow-md active:scale-95 disabled:opacity-50 transition-all flex items-center space-x-1.5"
          >
            <span v-if="isSubmitting" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>{{ isEdit ? '确认更新设备' : '确认录入入库' }}</span>
          </button>
        </div>
      </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { api } from '../../api/client'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  mode: {
    type: String,
    default: 'create', // 'create' | 'edit'
  },
  asset: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const isEdit = computed(() => props.mode === 'edit')
const activeTab = ref('basic')
const isSubmitting = ref(false)
const errorMsg = ref('')
const isAdvancedOpen = ref(false)

// 类别联动智能灰化 (网络设备与配电温控无需配置算力参数)
const isNetworkCategory = computed(() => form.category === '网络设备')
const isPowerCoolingCategory = computed(() => form.category === '配电温控')
const isComputeDisabled = computed(() => isNetworkCategory.value || isPowerCoolingCategory.value)
const computePlaceholder = computed(() => {
  if (isNetworkCategory.value) return '（网络交换/路由设备无需配置服务器处理器与显卡）'
  if (isPowerCoolingCategory.value) return '（动环设施无需配置算力参数）'
  return ''
})

// 机位智能配置与类别区分
const isRackCategory = computed(() => form.category === '服务器' || form.category === '网络设备')

const rackRoom = ref('ROOM-201')
const rackId = ref('机柜A01')
const rackUHeight = ref(2)
const rackStartU = ref(1)

const unrackedRoom = ref('ROOM-101')
const unrackedArea = ref('动力配电区')

// 动态机房与机柜底座数据
const dynamicRooms = ref([
  { room_code: 'ROOM-201', room_name: '实训楼201 人工智能与高密算力实训机房' },
  { room_code: 'ROOM-101', room_name: '实训楼101 综合网络与虚拟化教学机房' },
  { room_code: 'ROOM-301', room_name: '实训楼301 备用与退役实验仪器库房' },
])

const dynamicRacks = ref([
  { rack_id: '机柜A01', rack_name: 'A01 综合算力与网络核心柜', room_code: 'ROOM-201' },
  { rack_id: '机柜A02', rack_name: 'A02 备用算力扩展机柜', room_code: 'ROOM-201' },
  { rack_id: '机柜B01', rack_name: 'B01 教学虚拟化与网络汇聚柜', room_code: 'ROOM-101' },
])

async function fetchDynamicRoomsAndRacks() {
  try {
    const [roomsData, racksData] = await Promise.all([
      api.getRooms(),
      api.getRacks(),
    ])
    if (Array.isArray(roomsData) && roomsData.length > 0) {
      dynamicRooms.value = roomsData
    }
    if (Array.isArray(racksData) && racksData.length > 0) {
      dynamicRacks.value = racksData
    }
  } catch (err) {
    console.warn('动态加载机房机柜数据失败，保留基础预设:', err)
  }
}

onMounted(() => {
  fetchDynamicRoomsAndRacks()
})

const currentRackTotalU = computed(() => {
  const cur = dynamicRacks.value.find(r => r.rack_id === rackId.value)
  return cur?.total_u || 42
})

const availableRacks = computed(() => {
  const filtered = dynamicRacks.value.filter(r => r.room_code === rackRoom.value)
  if (filtered.length > 0) {
    return filtered.map(r => ({
      id: r.rack_id,
      name: `${r.rack_id} (${r.total_u || 42}U ${r.rack_name})`,
      disabled: false,
    }))
  }
  return [
    { id: '', name: '（该机房暂未设立机柜，请先新增机柜）', disabled: true },
  ]
})

const maxAllowedStartU = computed(() => {
  const maxU = currentRackTotalU.value - (rackUHeight.value || 1) + 1
  const list = []
  for (let i = 1; i <= Math.max(1, maxU); i++) {
    list.push(i)
  }
  return list
})

function onRackRoomChange() {
  const validRacks = availableRacks.value.filter(r => !r.disabled && r.id)
  if (!validRacks.some(r => r.id === rackId.value)) {
    rackId.value = validRacks[0]?.id || ''
  }
  updateRackLocation()
}

function onUHeightChange() {
  const maxU = currentRackTotalU.value - (rackUHeight.value || 1) + 1
  if (rackStartU.value > maxU) {
    rackStartU.value = Math.max(1, maxU)
  }
  updateRackLocation()
}

function updateRackLocation() {
  const roomNum = rackRoom.value.replace('ROOM-', '')
  if (rackId.value) {
    form.location = `实训楼${roomNum}-${rackId.value}-U${rackStartU.value}(${rackUHeight.value}U)`
  } else {
    form.location = `实训楼${roomNum}-暂无机柜`
  }
}

function updateUnrackedLocation() {
  const roomNum = unrackedRoom.value.replace('ROOM-', '')
  const area = unrackedArea.value.trim() || '配套设施区'
  form.location = `实训楼${roomNum}-${area}`
}

// 常用设备规格一键模板快捷应用
function applyHardwareTemplate(type) {
  if (type === 'compute_node') {
    form.category = '服务器'
    rackRoom.value = 'ROOM-201'
    rackId.value = '机柜A01'
    rackUHeight.value = 2
    rackStartU.value = 1
    updateRackLocation()
    if (!form.name || form.name.includes('通用') || form.name.includes('GPU') || form.name.includes('交换机') || form.name.includes('空调')) {
      form.name = '2U通用计算节点-R750'
    }
    form.specs = 'Dell PowerEdge R750 / Xeon Gold 6330 / 128G RAM / 2x 960G NVMe RAID1'
    detailForm.brand = 'Dell'
    detailForm.model_name = 'PowerEdge R750'
    detailForm.os_firmware = 'Ubuntu 22.04 LTS'
    detailForm.cpu_info = 'Intel Xeon Gold 6330 (56核/112线程)'
    detailForm.memory_info = '128GB (4x 32GB DDR4 3200MHz ECC)'
    detailForm.storage_info = '2x 960G NVMe SSD RAID1'
    detailForm.gpu_info = ''
    detailForm.network_interfaces = '4x 10GE 电口'
    detailForm.power_supply = '双路钛金冗余电源 (1+1)'
    detailForm.supplier = '戴尔企业级服务 (400-881-1852)'
  } else if (type === 'gpu_server') {
    form.category = '服务器'
    rackRoom.value = 'ROOM-201'
    rackId.value = '机柜A02'
    rackUHeight.value = 4
    rackStartU.value = 18
    updateRackLocation()
    if (!form.name || form.name.includes('通用') || form.name.includes('GPU') || form.name.includes('交换机') || form.name.includes('空调')) {
      form.name = '4卡GPU深度学习服务器-NF5468M6'
    }
    form.specs = 'Inspur NF5468M6 / 4x RTX 4090 24G / 256GB RAM / 2400W 冗余电源'
    detailForm.brand = 'Inspur'
    detailForm.model_name = 'NF5468M6'
    detailForm.os_firmware = 'Ubuntu 22.04 LTS'
    detailForm.cpu_info = '2x Intel Xeon Gold 6330 (56核/112线程)'
    detailForm.memory_info = '256GB (8x 32GB DDR4 3200MHz ECC)'
    detailForm.storage_info = '2x 960G NVMe RAID1 + 4x 3.84T U.2 RAID5'
    detailForm.gpu_info = '4x RTX 4090 24G'
    detailForm.network_interfaces = '2x 25GE SFP28 双光口 + 2x 10GE 电口'
    detailForm.power_supply = '2400W 冗余电源 (1+1)'
    detailForm.supplier = '浪潮信息技术支持 (400-860-0011)'
  } else if (type === 'switch') {
    form.category = '网络设备'
    rackRoom.value = 'ROOM-101'
    rackId.value = '机柜B01'
    rackUHeight.value = 1
    rackStartU.value = 1
    updateRackLocation()
    if (!form.name || form.name.includes('通用') || form.name.includes('GPU') || form.name.includes('交换机') || form.name.includes('空调')) {
      form.name = '万兆核心交换机-CE6800'
    }
    form.specs = 'Huawei CloudEngine 6800 / Huawei VRP 固件 / 48x 10GE + 6x 100GE'
    detailForm.brand = 'Huawei'
    detailForm.model_name = 'CloudEngine 6800'
    detailForm.os_firmware = 'Huawei VRP 固件'
    detailForm.cpu_info = ''
    detailForm.memory_info = ''
    detailForm.storage_info = ''
    detailForm.gpu_info = ''
    detailForm.network_interfaces = '48x 10GE + 6x 100GE'
    detailForm.power_supply = '双路冗余 600W 交流电源 (1+1)'
    detailForm.supplier = '华为企业网络服务 (400-822-9999)'
  } else if (type === 'cooling_pdu') {
    form.category = '配电温控'
    unrackedRoom.value = 'ROOM-101'
    unrackedArea.value = '动力配电与列间温控区'
    updateUnrackedLocation()
    if (!form.name || form.name.includes('通用') || form.name.includes('GPU') || form.name.includes('交换机') || form.name.includes('空调')) {
      form.name = '机房精密空调与智能PDU'
    }
    form.specs = 'Vertiv / Schneider 动环温控设备 / 380V 三相供电'
    detailForm.brand = 'Vertiv / Schneider'
    detailForm.model_name = 'Liebert CRV 模块化列间精密空调'
    detailForm.os_firmware = 'Vertiv iCOM 动环嵌入式微码系统'
    detailForm.cpu_info = ''
    detailForm.memory_info = ''
    detailForm.storage_info = ''
    detailForm.gpu_info = ''
    detailForm.network_interfaces = 'SNMP / Modbus-RTU 动环总线管理接口'
    detailForm.power_supply = '380V 三相供电 32A 双路冗余 / 30kW 额定制冷量'
    detailForm.supplier = '维谛技术 Vertiv 支持 (400-887-6526)'
  }
}

// 清空硬件物理参数所有选框内容 (方便用户撤销模板或手填参数)
function clearHardwareSpecs() {
  detailForm.brand = ''
  detailForm.model_name = ''
  detailForm.os_firmware = ''
  detailForm.mac_address = ''
  detailForm.management_ip = ''
  detailForm.cpu_info = ''
  detailForm.memory_info = ''
  detailForm.storage_info = ''
  detailForm.gpu_info = ''
  detailForm.network_interfaces = ''
  detailForm.power_supply = ''
  detailForm.purchase_date = ''
  detailForm.warranty_period = ''
  detailForm.supplier = ''
  detailForm.extra_params = ''
  form.specs = ''
}

const form = reactive({
  asset_no: '',
  name: '',
  category: '服务器',
  location: '',
  health_status: 'HEALTHY',
  borrow_status: 'AVAILABLE',
  borrower: '',
  specs: '',
  custom_temperature: 31.5,
})

const detailForm = reactive({
  serial_number: '',
  brand: '',
  model_name: '',
  os_firmware: '',
  mac_address: '',
  management_ip: '',
  cpu_info: '',
  memory_info: '',
  storage_info: '',
  gpu_info: '',
  network_interfaces: '',
  power_supply: '',
  purchase_date: '',
  warranty_period: '',
  supplier: '',
  extra_params: '',
  custom_temperature: 31.5,
})

function setQuickTemperature(val) {
  form.custom_temperature = val
}

// 核心温度设定与健康状态双向智能联动
watch(
  () => form.custom_temperature,
  (val) => {
    if (val === null || val === undefined || isNaN(val)) return
    const num = Number(val)
    if (form.health_status === 'OFFLINE') return
    if (num >= 40.0) {
      if (form.health_status !== 'OVERHEAT') form.health_status = 'OVERHEAT'
    } else if (num >= 38.0) {
      if (form.health_status !== 'WARNING') form.health_status = 'WARNING'
    } else {
      if (form.health_status !== 'HEALTHY') form.health_status = 'HEALTHY'
    }
  }
)

watch(
  () => form.health_status,
  (status) => {
    const num = Number(form.custom_temperature) || 30.0
    if (status === 'OVERHEAT' && num < 40.0) {
      form.custom_temperature = 43.5
    } else if (status === 'WARNING' && (num < 38.0 || num >= 40.0)) {
      form.custom_temperature = 38.5
    } else if (status === 'HEALTHY' && num >= 38.0) {
      form.custom_temperature = 31.5
    }
  }
)

watch(
  () => form.category,
  (newCat, oldCat) => {
    if (newCat && newCat !== oldCat) {
      if (isRackCategory.value) {
        if (!form.location || !form.location.includes('机柜')) {
          updateRackLocation()
        }
      } else {
        if (!form.location || form.location.includes('机柜')) {
          updateUnrackedLocation()
        }
      }
      if (!isEdit.value && (!form.asset_no || /^DEV-[A-Z]+-\d+$/i.test(form.asset_no.trim()))) {
        autoGenerateNo()
      }
    }
  }
)

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      fetchDynamicRoomsAndRacks()
      errorMsg.value = ''
      activeTab.value = 'basic'
      if (isEdit.value && props.asset) {
        form.asset_no = props.asset.asset_no || ''
        form.name = props.asset.name || ''
        form.category = props.asset.category || '服务器'
        form.location = props.asset.location || ''
        form.health_status = props.asset.health_status || 'HEALTHY'
        form.borrow_status = props.asset.borrow_status || 'AVAILABLE'
        form.borrower = props.asset.borrower || ''
        form.specs = props.asset.specs || ''

        const loadedTemp =
          props.asset.custom_temperature ??
          props.asset.telemetry_temperature ??
          props.asset.detail?.custom_temperature ??
          (props.asset.health_status === 'OVERHEAT'
            ? 43.5
            : props.asset.health_status === 'WARNING'
            ? 38.0
            : props.asset.health_status === 'OFFLINE'
            ? 22.0
            : 31.5)
        form.custom_temperature = Number(loadedTemp)

        const d = props.asset.detail || {}
        detailForm.serial_number = d.serial_number || ''
        detailForm.brand = d.brand || ''
        detailForm.model_name = d.model_name || ''
        detailForm.os_firmware = d.os_firmware || ''
        detailForm.mac_address = d.mac_address || ''
        detailForm.management_ip = d.management_ip || ''
        detailForm.cpu_info = d.cpu_info || ''
        detailForm.memory_info = d.memory_info || ''
        detailForm.storage_info = d.storage_info || ''
        detailForm.gpu_info = d.gpu_info || ''
        detailForm.network_interfaces = d.network_interfaces || ''
        detailForm.power_supply = d.power_supply || ''
        detailForm.purchase_date = d.purchase_date || ''
        detailForm.warranty_period = d.warranty_period || ''
        detailForm.supplier = d.supplier || ''
        detailForm.extra_params = d.extra_params || ''
        detailForm.custom_temperature = Number(loadedTemp)

        // 解析位置与机架机位插槽
        const loc = props.asset.location || ''
        let ep = {}
        if (d.extra_params) {
          try {
            ep = JSON.parse(d.extra_params)
          } catch (e) {}
        }

        if (form.category === '服务器' || form.category === '网络设备') {
          // 动态长序优先匹配机柜编号与所属机房 (彻底杜绝静态硬编码与错误覆盖)
          const matchedRack = dynamicRacks.value
            .slice()
            .sort((a, b) => b.rack_id.length - a.rack_id.length)
            .find(r => loc.includes(r.rack_id))

          if (matchedRack) {
            rackId.value = matchedRack.rack_id
            rackRoom.value = matchedRack.room_code
          } else {
            const matchedRoom = dynamicRooms.value
              .slice()
              .sort((a, b) => b.room_code.length - a.room_code.length)
              .find(r => loc.includes(r.room_code) || loc.includes(r.room_code.replace('ROOM-', '')) || (r.room_name && loc.includes(r.room_name)))
            if (matchedRoom) {
              rackRoom.value = matchedRoom.room_code
            }
            const curRacks = dynamicRacks.value.filter(r => r.room_code === rackRoom.value)
            rackId.value = curRacks[0]?.rack_id || ''
          }

          if (ep.u_height) {
            rackUHeight.value = Number(ep.u_height) || 1
          } else if (ep.rack_units) {
            const match = String(ep.rack_units).match(/(\d+)/)
            rackUHeight.value = match ? Number(match[1]) : 1
          } else {
            const matchLoc = loc.match(/\((\d+)U\)/i)
            rackUHeight.value = matchLoc ? Number(matchLoc[1]) : (form.category === '网络设备' ? 1 : 2)
          }

          if (ep.start_u !== undefined && ep.start_u !== null) {
            rackStartU.value = Number(ep.start_u) || 1
          } else {
            const matchU = loc.match(/-U(\d+)/i)
            rackStartU.value = matchU ? Number(matchU[1]) : 1
          }

          const maxU = (currentRackTotalU.value || 42) - (rackUHeight.value || 1) + 1
          rackStartU.value = Math.max(1, Math.min(maxU, rackStartU.value))

          // 保持机位联动规范性：若原位置非机柜标准格式或为空，立即自动生成规范物理位置描述
          if (!loc.includes('机柜') || !form.location) {
            updateRackLocation()
          }
        } else {
          // 非机架外设动态长序匹配所属机房
          const matchedRoom = dynamicRooms.value
            .slice()
            .sort((a, b) => b.room_code.length - a.room_code.length)
            .find(r => loc.includes(r.room_code) || loc.includes(r.room_code.replace('ROOM-', '')) || (r.room_name && loc.includes(r.room_name)))
          if (matchedRoom) {
            unrackedRoom.value = matchedRoom.room_code
          } else {
            unrackedRoom.value = dynamicRooms.value[0]?.room_code || 'ROOM-201'
          }

          const parts = loc.split('-')
          if (parts.length > 1) {
            unrackedArea.value = parts.slice(1).join('-')
          } else {
            unrackedArea.value = loc || '动力配电区'
          }
          if (loc.includes('机柜') || !form.location) {
            updateUnrackedLocation()
          }
        }
      } else {
        resetForm()
        autoGenerateNo()
      }
    }
  }
)

function resetForm() {
  form.asset_no = ''
  form.name = ''
  form.category = '服务器'
  rackRoom.value = 'ROOM-201'
  rackId.value = '机柜A01'
  rackUHeight.value = 2
  rackStartU.value = 1
  unrackedRoom.value = 'ROOM-101'
  unrackedArea.value = '动力配电区'
  updateRackLocation()
  form.health_status = 'HEALTHY'
  form.borrow_status = 'AVAILABLE'
  form.borrower = ''
  form.specs = ''
  form.custom_temperature = 31.5

  Object.keys(detailForm).forEach((k) => {
    detailForm[k] = ''
  })
  detailForm.custom_temperature = 31.5
  isAdvancedOpen.value = false
}

function autoGenerateNo() {
  const prefixMap = {
    '服务器': 'DEV-SRV',
    '网络设备': 'DEV-NET',
    '配电温控': 'DEV-PWR',
    '实验教学': 'DEV-LAB',
  }
  const prefix = prefixMap[form.category] || 'DEV-AST'
  const randNum = Math.floor(100 + Math.random() * 900)
  form.asset_no = `${prefix}-${randNum}`
}

let isMouseDownOnBackdrop = false

function handleBackdropMouseDown(e) {
  // 仅当鼠标按下时的实际目标即为外部遮罩层容器本身时才标记
  isMouseDownOnBackdrop = (e.target === e.currentTarget)
}

function handleBackdropMouseUp(e) {
  // 必须满足鼠标按下(mousedown)和鼠标抬起(mouseup)两阶段均发生在遮罩空白处，才触发退出
  // 从而彻底防止在输入框拖选文本时光标划出弹窗边界导致误关
  if (isMouseDownOnBackdrop && e.target === e.currentTarget) {
    close()
  }
  isMouseDownOnBackdrop = false
}

function close() {
  emit('update:modelValue', false)
}

async function handleSubmit() {
  if (!form.asset_no.trim() || !form.name.trim() || !form.location.trim()) {
    errorMsg.value = '请完整填写资产编号、名称与机房物理位置'
    return
  }

  if (isRackCategory.value && !rackId.value) {
    errorMsg.value = '所选机房暂无在册机柜，请先在机柜拓扑大盘中立项设立机柜，或将设备类别切换为非机架外设'
    return
  }

  isSubmitting.value = true
  errorMsg.value = ''

  try {
    const parsedTemp =
      form.custom_temperature !== null &&
      form.custom_temperature !== undefined &&
      !isNaN(form.custom_temperature) &&
      form.custom_temperature !== ''
        ? Number(form.custom_temperature)
        : null

    let extraParamsObj = {}
    if (detailForm.extra_params && detailForm.extra_params.trim()) {
      try {
        extraParamsObj = JSON.parse(detailForm.extra_params)
      } catch (e) {
        errorMsg.value = '高级选项中的扩展定制参数 JSON 格式不合法，请检查闭合括号与双引号'
        isSubmitting.value = false
        return
      }
    }

    if (isRackCategory.value) {
      extraParamsObj.start_u = Number(rackStartU.value) || 1
      extraParamsObj.u_height = Number(rackUHeight.value) || 1
      extraParamsObj.rack_units = `${extraParamsObj.u_height}U`
    } else {
      delete extraParamsObj.start_u
      delete extraParamsObj.u_height
      delete extraParamsObj.rack_units
    }

    const finalExtraParams = Object.keys(extraParamsObj).length > 0 ? JSON.stringify(extraParamsObj) : null

    const payload = {
      name: form.name.trim(),
      category: form.category,
      location: form.location.trim(),
      health_status: form.health_status,
      // 录入模式下锁定为 AVAILABLE，借还流转交由资产列表借还管理
      borrow_status: isEdit.value ? form.borrow_status : 'AVAILABLE',
      borrower: isEdit.value ? (form.borrower.trim() || null) : null,
      specs: form.specs.trim() || null,
      custom_temperature: parsedTemp,
      detail: {
        serial_number: detailForm.serial_number.trim() || null,
        brand: detailForm.brand.trim() || null,
        model_name: detailForm.model_name.trim() || null,
        os_firmware: detailForm.os_firmware.trim() || null,
        mac_address: detailForm.mac_address.trim() || null,
        management_ip: detailForm.management_ip.trim() || null,
        // 网络设备/配电温控不提交算力参数
        cpu_info: isComputeDisabled.value ? null : (detailForm.cpu_info.trim() || null),
        memory_info: isComputeDisabled.value ? null : (detailForm.memory_info.trim() || null),
        storage_info: isComputeDisabled.value ? null : (detailForm.storage_info.trim() || null),
        gpu_info: isComputeDisabled.value ? null : (detailForm.gpu_info.trim() || null),
        network_interfaces: detailForm.network_interfaces.trim() || null,
        power_supply: detailForm.power_supply.trim() || null,
        purchase_date: detailForm.purchase_date.trim() || null,
        warranty_period: detailForm.warranty_period.trim() || null,
        supplier: detailForm.supplier.trim() || null,
        extra_params: finalExtraParams,
        custom_temperature: parsedTemp,
      },
    }

    let savedAsset
    if (isEdit.value) {
      savedAsset = await api.updateAsset(props.asset.id, payload)
    } else {
      payload.asset_no = form.asset_no.trim().toUpperCase()
      savedAsset = await api.createAsset(payload)
    }

    emit('saved', savedAsset)
    close()
  } catch (err) {
    errorMsg.value = err.message || '提交失败，请检查网络或后端连接'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* 彻底清除各类浏览器原生 number 输入框的上下箭头，杜绝与右侧单位重叠 */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
}

/* 提示文字弱化处理：倾斜且微缩字号(11px)，减轻填单心理压力，保持清晰可辨 */
input::placeholder,
textarea::placeholder {
  font-style: italic;
  font-size: 11px;
}
</style>
