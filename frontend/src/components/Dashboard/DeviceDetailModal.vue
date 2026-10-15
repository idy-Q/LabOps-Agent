<template>
  <Transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 scale-95"
    enter-to-class="opacity-100 scale-100"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100 scale-100"
    leave-to-class="opacity-0 scale-95"
  >
    <!-- 悬浮挂载容器 (纯净透明无黑色遮罩阴影底，点击卡片外部区域即可关闭) -->
    <div
      v-if="modelValue"
      @keydown.esc.window="close"
      class="absolute inset-0 z-40 flex items-center justify-center p-3 sm:p-5 bg-transparent overflow-hidden"
      @mousedown="handleBackdropMouseDown"
      @mouseup="handleBackdropMouseUp"
    >
      <!-- 核心浮窗玻璃卡片 (悬浮在右侧控制面板上方，四周留白，带高不透明度防护与周围柔和阴影) -->
      <div
        class="device-detail-glass-card w-[95%] max-w-xl rounded-2xl sm:rounded-3xl border p-4 sm:p-5 space-y-3.5 flex flex-col max-h-[92%] overflow-hidden transition-all"
      >
        <!-- 头部：设备身份徽章与关闭按钮 -->
        <div class="flex items-start justify-between border-b border-white/[0.08] pb-3 shrink-0">
          <div class="flex items-center space-x-3 min-w-0">
            <!-- 分类专属立体玻璃图标 -->
            <div class="p-2.5 rounded-2xl bg-zinc-950/80 border border-white/[0.1] text-cyan-400 shrink-0 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]">
              <!-- 服务器 -->
              <svg v-if="asset?.category === '服务器'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
              <!-- 网络设备 -->
              <svg v-else-if="asset?.category === '网络设备'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
              </svg>
              <!-- 配电温控 -->
              <svg v-else-if="asset?.category === '配电温控'" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <!-- 实验教学及其他 -->
              <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>

            <div class="min-w-0">
              <div class="flex items-center space-x-2 flex-wrap gap-y-1">
                <h3 class="text-sm sm:text-base font-semibold text-zinc-100 truncate tracking-tight glass-text">
                  {{ asset?.name || '设备全景参数档案' }}
                </h3>
                <!-- 圆角胶囊状态药丸 -->
                <span :class="['px-2.5 py-0.5 rounded-full text-[10px] font-sans border font-medium shadow-sm', healthClass(effectiveHealthStatus)]">
                  {{ getHealthLabel(effectiveHealthStatus) }}
                </span>
                <span :class="['px-2.5 py-0.5 rounded-full text-[10px] font-sans border font-medium shadow-sm', borrowClass(asset?.borrow_status)]">
                  {{ asset?.borrow_status === 'AVAILABLE' ? '空闲可用' : asset?.borrow_status === 'IN_USE' ? '借调在用' : '检修维护' }}
                </span>
              </div>

              <div class="flex items-center space-x-2 mt-0.5 text-xs text-zinc-400 font-mono">
                <span>编号: <strong class="text-cyan-400 select-all font-semibold">{{ asset?.asset_no }}</strong></span>
                <button
                  @click="copyText(asset?.asset_no)"
                  class="text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors inline-flex items-center"
                  title="点击复制设备编号"
                >
                  <svg v-if="!copiedNo" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span v-else class="text-[10px] text-emerald-400 font-sans">已复制</span>
                </button>
                <span class="text-zinc-600">|</span>
                <span class="truncate">{{ asset?.category }}</span>
                <span class="text-zinc-600">|</span>
                <span class="truncate">{{ asset?.location }}</span>
              </div>
            </div>
          </div>

          <!-- 圆形关闭按钮 -->
          <button
            @click="close"
            class="text-zinc-400 hover:text-zinc-100 p-1.5 rounded-full hover:bg-white/[0.08] transition-all shrink-0 active:scale-90"
            title="关闭详情 (Esc)"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 中间可滚动区域：分层圆角卡片面板 -->
        <div class="flex-1 overflow-y-auto pr-1 space-y-3 custom-scrollbar text-xs font-sans">
          <!-- 0. 动环传感与探针实时遥测卡片 -->
          <div class="p-3.5 rounded-2xl bg-black/25 border border-white/[0.06] space-y-2.5 shadow-sm">
            <div class="flex items-center justify-between text-zinc-300 font-medium pb-1.5 border-b border-white/[0.05]">
              <span class="flex items-center space-x-1.5 text-rose-400">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span class="font-medium text-zinc-200">动环传感与探针实时遥测</span>
              </span>
              <span
                :class="[
                  'px-2 py-0.5 rounded-lg text-[10px] font-mono border font-medium flex items-center space-x-1',
                  asset?.health_status === 'OFFLINE'
                    ? 'bg-zinc-800 text-zinc-400 border-white/[0.06]'
                    : currentTemp >= 40.0
                    ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse'
                    : currentTemp >= 38.0
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                ]"
              >
                <span>{{ asset?.health_status === 'OFFLINE' ? '⚪ 离线脱网' : currentTemp >= 40.0 ? '🔴 超温告警' : currentTemp >= 38.0 ? '🟡 临界预警' : '🟢 动环受控正常' }}</span>
              </span>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-[11px]">
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">核心遥测温度</div>
                <div
                  :class="[
                    'text-base font-bold font-mono',
                    asset?.health_status === 'OFFLINE'
                      ? 'text-zinc-400'
                      : currentTemp >= 40.0
                      ? 'text-rose-400 animate-pulse'
                      : currentTemp >= 38.0
                      ? 'text-amber-400'
                      : 'text-emerald-400'
                  ]"
                >
                  {{ currentTemp }} °C
                </div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">散热风扇转速</div>
                <div class="text-zinc-200 font-medium truncate">{{ estimatedFanSpeed }}</div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">实时功耗负荷</div>
                <div class="text-cyan-400 font-medium">{{ estimatedPower }}</div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">探针遥测模式</div>
                <div class="text-indigo-300 font-sans truncate font-medium">
                  {{ isCustomTelemetry ? '自定义注入' : '动环基准推导' }}
                </div>
              </div>
            </div>
          </div>

          <!-- 1. 出厂标识与网络通信卡片 -->
          <div class="p-3.5 rounded-2xl bg-black/25 border border-white/[0.06] space-y-2.5 shadow-sm">
            <div class="flex items-center justify-between text-zinc-300 font-medium pb-1.5 border-b border-white/[0.05]">
              <span class="flex items-center space-x-1.5 text-cyan-400">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span class="font-medium text-zinc-200">出厂标识与网络通信</span>
              </span>
              <span v-if="detail?.serial_number" class="font-mono text-[10px] text-zinc-400 bg-zinc-900/80 px-2 py-0.5 rounded-lg border border-white/[0.06]">
                SN: <span class="text-zinc-200 select-all font-semibold">{{ detail.serial_number }}</span>
              </span>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px]">
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">厂商品牌</div>
                <div class="text-zinc-200 font-sans font-medium truncate">{{ detail?.brand || '机房自采/通用定制' }}</div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">具体产品型号</div>
                <div class="text-zinc-200 truncate font-sans font-medium" :title="detail?.model_name">{{ detail?.model_name || '标准规格' }}</div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">带外 / 管理 IP</div>
                <div class="text-cyan-400 font-medium select-all">{{ detail?.management_ip || '未配置管理IP' }}</div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">物理 MAC 地址</div>
                <div class="text-zinc-300 select-all truncate">{{ detail?.mac_address || '00:00:00:00:00:00' }}</div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">系统 / 固件版本</div>
                <div class="text-zinc-300 truncate" :title="detail?.os_firmware">{{ detail?.os_firmware || '内置通用固件' }}</div>
              </div>
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                <div class="text-zinc-500 text-[10px] font-sans">当前借调使用人</div>
                <div class="text-amber-300 font-sans font-medium truncate">{{ asset?.borrower || '暂无借出 (库房在册)' }}</div>
              </div>
            </div>
          </div>

          <!-- 2. 核心计算与硬件规格矩阵卡片 -->
          <div class="p-3.5 rounded-2xl bg-black/25 border border-white/[0.06] space-y-2.5 shadow-sm">
            <div class="flex items-center justify-between text-zinc-300 font-medium pb-1.5 border-b border-white/[0.05]">
              <span class="flex items-center space-x-1.5 text-indigo-400">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
                <span class="font-medium text-zinc-200">计算, 存储与动力硬件参数</span>
              </span>
              <span class="text-[10px] text-zinc-500 font-mono">硬件规格台账</span>
            </div>

            <div class="space-y-1.5 font-mono text-[11px]">
              <!-- CPU -->
              <div class="flex items-start justify-between gap-2 p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03]">
                <span class="text-zinc-400 shrink-0 font-sans flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                  <span class="text-zinc-300">核心处理器 (CPU)</span>
                </span>
                <span class="text-zinc-100 text-right font-medium break-all">
                  {{ detail?.cpu_info || asset?.specs || '标准核心处理架构' }}
                </span>
              </div>

              <!-- 内存 -->
              <div class="flex items-start justify-between gap-2 p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03]">
                <span class="text-zinc-400 shrink-0 font-sans flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                  <span class="text-zinc-300">运行内存 (RAM)</span>
                </span>
                <span class="text-zinc-100 text-right font-medium break-all">
                  {{ detail?.memory_info || '规格未详述' }}
                </span>
              </div>

              <!-- 存储 -->
              <div class="flex items-start justify-between gap-2 p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03]">
                <span class="text-zinc-400 shrink-0 font-sans flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span class="text-zinc-300">磁盘存储与阵列</span>
                </span>
                <span class="text-zinc-100 text-right font-medium break-all">
                  {{ detail?.storage_info || '标准存储介质' }}
                </span>
              </div>

              <!-- GPU -->
              <div v-if="detail?.gpu_info" class="flex items-start justify-between gap-2 p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03]">
                <span class="text-zinc-400 shrink-0 font-sans flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                  <span class="text-zinc-300">算力加速卡 (GPU)</span>
                </span>
                <span class="text-emerald-400 text-right font-medium break-all">
                  {{ detail.gpu_info }}
                </span>
              </div>

              <!-- 网络端口与供电 -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-0.5">
                <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                  <div class="text-zinc-500 text-[10px] font-sans">网络物理接口</div>
                  <div class="text-zinc-200 break-all">{{ detail?.network_interfaces || 'RJ45 千兆双口' }}</div>
                </div>
                <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03] space-y-0.5">
                  <div class="text-zinc-500 text-[10px] font-sans">动力供电规格</div>
                  <div class="text-zinc-200 break-all">{{ detail?.power_supply || '单相 220V 50Hz' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. 商务采购与技术维保支持 -->
          <div class="p-3.5 rounded-2xl bg-black/25 border border-white/[0.06] space-y-2 shadow-sm">
            <div class="flex items-center justify-between text-zinc-300 font-medium pb-1.5 border-b border-white/[0.05]">
              <span class="flex items-center space-x-1.5 text-amber-400">
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <span class="font-medium text-zinc-200">采购台账与技术维保</span>
              </span>
              <span class="text-[10px] text-zinc-500 font-mono">录入: {{ asset?.created_at?.slice(0, 10) || '2026' }}</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 font-mono text-[11px]">
              <div class="p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03]">
                <span class="text-zinc-500 text-[10px] block font-sans">投产入库:</span>
                <span class="text-zinc-200 font-medium">{{ detail?.purchase_date || '2024年' }}</span>
              </div>
              <div class="sm:col-span-2 p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03]">
                <span class="text-zinc-500 text-[10px] block font-sans">维保服务期限:</span>
                <span class="text-zinc-200 font-medium">{{ detail?.warranty_period || '标准原厂质保 3年' }}</span>
              </div>
              <div class="sm:col-span-3 p-2 rounded-xl bg-zinc-900/40 border border-white/[0.03]">
                <span class="text-zinc-500 text-[10px] block font-sans">技术支持供应商:</span>
                <span class="text-zinc-200 font-sans font-medium truncate block">{{ detail?.supplier || '高校资产运维设备集成商 (技术支持部)' }}</span>
              </div>
            </div>
          </div>

          <!-- 4. 专属定制参数 (若有) -->
          <div v-if="parsedExtraParams && Object.keys(parsedExtraParams).length > 0" class="p-3.5 rounded-2xl bg-black/25 border border-white/[0.06] space-y-2 shadow-sm">
            <div class="text-zinc-300 font-medium text-xs flex items-center space-x-1.5">
              <svg class="w-3.5 h-3.5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <span class="font-medium text-zinc-200">专属定制参数与扩展属性</span>
            </div>
            <div class="flex flex-wrap gap-1.5 font-mono text-[11px]">
              <div
                v-for="(val, key) in parsedExtraParams"
                :key="key"
                class="px-2.5 py-1 rounded-xl bg-zinc-900/60 border border-white/[0.06] flex items-center space-x-1.5 shadow-inner"
              >
                <span class="text-zinc-500">{{ key }}:</span>
                <span class="text-cyan-300 font-medium">{{ val }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部操作按钮栏 -->
        <div class="pt-3 border-t border-white/[0.08] flex items-center justify-between gap-2 shrink-0 flex-wrap">
          <div class="flex items-center space-x-2">
            <!-- 资产流转履历按钮 (全时序时间轴) -->
            <button
              @click="emit('viewTimeline', asset?.asset_no)"
              class="px-3 py-1.5 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-medium flex items-center space-x-1.5 transition-all shadow-sm active:scale-95"
              title="查看该资产从采购投产到借调维保的全生命周期时序履历"
            >
              <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>资产流转履历</span>
            </button>

            <!-- 巡检按钮 -->
            <button
              @click="emit('inspect', asset?.asset_no)"
              class="px-3 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-medium flex items-center space-x-1.5 transition-all shadow-sm active:scale-95"
              title="在左侧智能助理中发起此设备的健康指标深度巡检"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>智能巡检此设备</span>
            </button>

            <!-- 借还按钮 -->
            <button
              v-if="asset?.borrow_status === 'AVAILABLE'"
              :disabled="isStudent"
              @click="emit('borrow', asset)"
              :class="[
                'px-3 py-1.5 rounded-xl text-xs font-medium transition-all shadow-sm border',
                isStudent
                  ? 'bg-zinc-800/40 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-50'
                  : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-white/[0.08] active:scale-95'
              ]"
            >
              借用登记
            </button>
            <button
              v-else-if="asset?.borrow_status === 'IN_USE'"
              :disabled="!canReturn"
              @click="emit('return', asset?.asset_no)"
              :class="[
                'px-3 py-1.5 rounded-xl text-xs font-medium transition-all shadow-sm border',
                canReturn
                  ? 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border-emerald-500/30 active:scale-95'
                  : 'bg-zinc-800/40 text-zinc-500 border-white/[0.04] cursor-not-allowed opacity-50'
              ]"
            >
              办理归还
            </button>
          </div>

          <div class="flex items-center space-x-2">
            <!-- 编辑设备入口 (受角色控制，非学生可编辑) -->
            <button
              v-if="!isStudent"
              @click="emit('edit', asset)"
              class="px-3 py-1.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-white/[0.08] hover:border-white/[0.2] text-xs font-medium transition-all active:scale-95 shadow-sm flex items-center space-x-1.5"
            >
              <svg class="w-3.5 h-3.5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              <span>修改参数</span>
            </button>

            <!-- 删除设备 (仅管理员) -->
            <button
              v-if="isAdmin"
              @click="emit('delete', asset)"
              class="px-2.5 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 hover:text-rose-300 border border-rose-500/20 text-xs font-medium transition-all active:scale-95 shadow-sm"
              title="从机房台账中彻底移除此设备"
            >
              删除
            </button>

            <button
              @click="close"
              class="px-3.5 py-1.5 rounded-xl bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-xs transition-all shadow-md active:scale-95"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  asset: {
    type: Object,
    default: null,
  },
  currentUser: {
    type: Object,
    default: () => ({ role: 'ADMIN' }),
  },
})

const emit = defineEmits(['update:modelValue', 'inspect', 'borrow', 'return', 'edit', 'delete', 'viewTimeline'])

const detail = computed(() => props.asset?.detail || null)

const currentTemp = computed(() => {
  if (!props.asset) return 31.5
  if (props.asset.health_status === 'OFFLINE') return 22.0
  const t =
    props.asset.custom_temperature ??
    props.asset.telemetry_temperature ??
    detail.value?.custom_temperature
  if (t !== undefined && t !== null) return Number(t)
  if (props.asset.health_status === 'OVERHEAT') return 43.5
  if (props.asset.health_status === 'WARNING') return 38.0
  return 31.5
})

const effectiveHealthStatus = computed(() => {
  if (!props.asset) return 'HEALTHY'
  if (props.asset.health_status === 'OFFLINE') return 'OFFLINE'
  const temp = currentTemp.value
  if (temp >= 40.0) return 'OVERHEAT'
  if (temp >= 38.0) return 'WARNING'
  return 'HEALTHY'
})

function getHealthLabel(status) {
  const map = {
    HEALTHY: '正常',
    WARNING: '预警',
    OVERHEAT: '超温',
    OFFLINE: '离线',
  }
  return map[status] || status || '-'
}

const isCustomTelemetry = computed(() => {
  return (
    props.asset?.custom_temperature !== undefined &&
    props.asset?.custom_temperature !== null
  ) || (
    detail.value?.custom_temperature !== undefined &&
    detail.value?.custom_temperature !== null
  )
})

const estimatedFanSpeed = computed(() => {
  if (props.asset?.health_status === 'OFFLINE') return '0 RPM (停转)'
  const temp = currentTemp.value
  if (temp >= 40.0) return `${Math.min(6000, Math.max(4500, Math.round(4500 + (temp - 40) * 150)))} RPM (超负荷)`
  if (temp >= 38.0) return `${Math.round(3200 + (temp - 38) * 200)} RPM (中高转速)`
  return `${Math.round(2000 + Math.max(0, temp - 25) * 30)} RPM (静音巡航)`
})

const estimatedPower = computed(() => {
  if (props.asset?.health_status === 'OFFLINE') return '0 W (断电待机)'
  const temp = currentTemp.value
  if (temp >= 40.0) return `${Math.min(650, Math.max(400, Math.round(420 + (temp - 40) * 15)))} W`
  if (temp >= 38.0) return `${Math.round(300 + (temp - 38) * 10)} W`
  return `${Math.round(180 + Math.max(0, temp - 25) * 3)} W`
})

const userRole = computed(() => (props.currentUser?.role || 'STUDENT').toUpperCase())
const isStudent = computed(() => userRole.value === 'STUDENT')
const isAdmin = computed(() => userRole.value === 'ADMIN')
const isTeacher = computed(() => userRole.value === 'TEACHER')

const canReturn = computed(() => {
  if (isStudent.value) return false
  if (isAdmin.value) return true
  if (isTeacher.value) {
    if (!props.asset?.borrower) return false
    const teacherName = props.currentUser?.real_name || ''
    const teacherUser = props.currentUser?.username || ''
    return (
      (teacherName && props.asset.borrower.includes(teacherName)) ||
      (teacherUser && props.asset.borrower.includes(teacherUser))
    )
  }
  return false
})

const copiedNo = ref(false)

function copyText(txt) {
  if (!txt) return
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(txt).then(() => {
      copiedNo.value = true
      setTimeout(() => {
        copiedNo.value = false
      }, 1500)
    }).catch(() => {})
  }
}

const parsedExtraParams = computed(() => {
  if (!detail.value?.extra_params) return null
  try {
    return JSON.parse(detail.value.extra_params)
  } catch {
    return null
  }
})

let isMouseDownOnBackdrop = false

function handleBackdropMouseDown(e) {
  isMouseDownOnBackdrop = (e.target === e.currentTarget)
}

function handleBackdropMouseUp(e) {
  if (isMouseDownOnBackdrop && e.target === e.currentTarget) {
    close()
  }
  isMouseDownOnBackdrop = false
}

function close() {
  emit('update:modelValue', false)
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
/*
  固定高不透明度玻璃架构（Protected High-Contrast Glass）：
  1. 悬浮在表格之上，拥有不受全局视效影响的固定高不透明度，维持 94%+ 遮蔽力，
     彻底杜绝下方表格文字穿透导致的重叠阅读障碍。
  2. 周边环境柔和模糊阴影（Ambient Halo）：
     在卡片周边 360 度向外柔和虚化晕开，暗黑模式下为深邃悬浮质感，
     明亮模式下为高质感轻盈冰晶光晕，绝不残留硬边黑斑或黑色外壳。
*/
.device-detail-glass-card {
  background-color: rgba(16, 17, 23, 0.94) !important;
  backdrop-filter: blur(24px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08),
    0 0 28px 4px rgba(0, 0, 0, 0.65),
    0 12px 36px -4px rgba(0, 0, 0, 0.7) !important;
}

/* ========================================================
   明亮模式 (Light Mode) 专属全景自适应样式
   ======================================================== */
html.light .device-detail-glass-card {
  background-color: rgba(255, 255, 255, 0.97) !important;
  backdrop-filter: blur(24px) !important;
  -webkit-backdrop-filter: blur(24px) !important;
  border: 1px solid rgba(203, 213, 225, 0.85) !important;
  box-shadow:
    0 0 0 1px rgba(226, 232, 240, 0.8),
    0 16px 40px -6px rgba(15, 23, 42, 0.12),
    0 4px 16px 0 rgba(15, 23, 42, 0.05) !important;
}

/* 1. 头部大图标容器明亮自适应 */
html.light .device-detail-glass-card .bg-zinc-950\/80 {
  background-color: rgba(241, 245, 249, 0.95) !important;
  border-color: rgba(203, 213, 225, 0.85) !important;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04) !important;
}

/* 2. 标题与层级文字颜色高对比度适配 */
html.light .device-detail-glass-card .text-zinc-100 {
  color: #0f172a !important;
  text-shadow: none !important;
}
html.light .device-detail-glass-card .text-zinc-200 {
  color: #1e293b !important;
}
html.light .device-detail-glass-card .text-zinc-300 {
  color: #334155 !important;
}
html.light .device-detail-glass-card .text-zinc-400 {
  color: #475569 !important;
}
html.light .device-detail-glass-card .text-zinc-500 {
  color: #64748b !important;
}
html.light .device-detail-glass-card .text-zinc-600 {
  color: #cbd5e1 !important;
}

/* 3. 边框分割线明亮自适应 */
html.light .device-detail-glass-card [class*="border-white"] {
  border-color: rgba(226, 232, 240, 0.85) !important;
}

/* 4. 出厂标识、硬件矩阵、维保等子面板明亮底色 */
html.light .device-detail-glass-card [class*="bg-black/25"] {
  background-color: rgba(248, 250, 252, 0.95) !important;
  border-color: rgba(226, 232, 240, 0.9) !important;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04) !important;
}

/* 5. 子卡片内各参数芯片格子（CPU、内存、存储、网口、供电等）自适应为白底柔边卡片 */
html.light .device-detail-glass-card [class*="bg-zinc-900/40"],
html.light .device-detail-glass-card [class*="bg-zinc-900/60"] {
  background-color: #ffffff !important;
  border-color: rgba(226, 232, 240, 0.9) !important;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03) !important;
}

/* 6. SN 码与定制标签徽章明亮自适应 */
html.light .device-detail-glass-card .bg-zinc-900\/80 {
  background-color: rgba(241, 245, 249, 0.95) !important;
  border-color: rgba(203, 213, 225, 0.8) !important;
}

/* 7. 关闭 X 按钮 hover 状态 */
html.light .device-detail-glass-card button.text-zinc-400:hover {
  background-color: rgba(241, 245, 249, 0.9) !important;
  color: #0f172a !important;
}

/* 8. 底部操作按钮明亮自适应 */
html.light .device-detail-glass-card .bg-zinc-800 {
  background-color: #ffffff !important;
  color: #1e293b !important;
  border-color: rgba(203, 213, 225, 0.9) !important;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06) !important;
}
html.light .device-detail-glass-card .bg-zinc-800:hover {
  background-color: rgba(248, 250, 252, 0.95) !important;
  border-color: rgba(99, 102, 241, 0.4) !important;
  color: #4f46e5 !important;
}
html.light .device-detail-glass-card .bg-zinc-100 {
  background-color: rgba(241, 245, 249, 0.95) !important;
  color: #334155 !important;
  border: 1px solid rgba(203, 213, 225, 0.9) !important;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04) !important;
}
html.light .device-detail-glass-card .bg-zinc-100:hover {
  background-color: rgba(226, 232, 240, 0.95) !important;
  color: #0f172a !important;
  border-color: rgba(148, 163, 184, 0.9) !important;
}

/* 9. 智能巡检按钮明亮自适应 */
html.light .device-detail-glass-card .bg-cyan-500\/10 {
  background-color: rgba(207, 250, 254, 0.8) !important;
  color: #0891b2 !important;
  border-color: rgba(6, 182, 212, 0.4) !important;
}
html.light .device-detail-glass-card .bg-cyan-500\/10:hover {
  background-color: rgba(165, 243, 252, 0.8) !important;
}

/* 10. 高亮状态文本加深保障高对比度 */
html.light .device-detail-glass-card .text-cyan-400 {
  color: #0891b2 !important;
}
html.light .device-detail-glass-card .text-indigo-400 {
  color: #4f46e5 !important;
}
html.light .device-detail-glass-card .text-amber-400 {
  color: #d97706 !important;
}
html.light .device-detail-glass-card .text-emerald-400 {
  color: #059669 !important;
}
html.light .device-detail-glass-card .text-rose-400 {
  color: #e11d48 !important;
}
</style>
