<template>
  <div
    class="fixed inset-0 pointer-events-none z-0 w-full h-full overflow-hidden transition-colors duration-500 ease-in-out"
    :class="theme === 'light' ? 'bg-[#f8fafc]' : 'bg-[#08080a]'"
  >
    <canvas
      ref="canvasRef"
      class="w-full h-full block transition-opacity duration-700 ease-in-out"
      :class="isPaused ? 'opacity-0' : 'opacity-100'"
      aria-hidden="true"
    ></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  isPaused: {
    type: Boolean,
    default: false,
  },
  theme: {
    type: String,
    default: 'dark',
  },
})

const canvasRef = ref(null)
let ctx = null
let animationFrameId = null
let isVisible = true

// 尺寸与渲染比例
let width = 0
let height = 0
let dpr = 1

// 鼠标/触控位置与动力学插值
let targetX = -1000
let targetY = -1000
let currentX = -1000
let currentY = -1000
let prevX = -1000
let prevY = -1000
let smoothSpeed = 0
let isPositionInitialized = false
let userInteracted = false

// 波纹涟漪池
const ripples = []

// 极光有机流体光斑定义 (Codex 专属流光)
const orbs = [
  {
    baseXRatio: 0.35,
    baseYRatio: 0.3,
    r: 99,
    g: 102,
    b: 241, // #6366F1 紫罗兰
    radiusRatio: 0.44,
    speedX: 0.0007,
    speedY: 0.0009,
    phase: 0,
    ampX: 0.15,
    ampY: 0.12,
  },
  {
    baseXRatio: 0.65,
    baseYRatio: 0.45,
    r: 139,
    g: 92,
    b: 246, // #8B5CF6 薰衣草紫
    radiusRatio: 0.4,
    speedX: 0.0009,
    speedY: 0.0006,
    phase: 1.8,
    ampX: 0.18,
    ampY: 0.14,
  },
  {
    baseXRatio: 0.5,
    baseYRatio: 0.75,
    r: 59,
    g: 130,
    b: 246, // #3B82F6 雾蓝
    radiusRatio: 0.46,
    speedX: 0.0006,
    speedY: 0.0008,
    phase: 3.4,
    ampX: 0.2,
    ampY: 0.15,
  },
  {
    baseXRatio: 0.8,
    baseYRatio: 0.25,
    r: 6,
    g: 182,
    b: 212, // #06B6D4 浅青光幕
    radiusRatio: 0.35,
    speedX: 0.0008,
    speedY: 0.0011,
    phase: 4.6,
    ampX: 0.12,
    ampY: 0.1,
  },
]

function handleResize() {
  if (!canvasRef.value) return
  const canvas = canvasRef.value
  dpr = Math.min(window.devicePixelRatio || 1, 2)
  width = window.innerWidth
  height = window.innerHeight
  canvas.width = Math.floor(width * dpr)
  canvas.height = Math.floor(height * dpr)
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`
  if (ctx) {
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.scale(dpr, dpr)
  }
  // 暂停状态下窗口尺寸变更时，重绘首帧避免画布变白/透明空白
  if (props.isPaused && ctx) {
    renderFrame(performance.now(), 16)
  }
}

function handleMouseMove(e) {
  targetX = e.clientX
  targetY = e.clientY
  if (!userInteracted) {
    prevX = targetX
    prevY = targetY
    userInteracted = true
  }
}

function handleTouchMove(e) {
  if (e.touches && e.touches.length > 0) {
    const t = e.touches[0]
    targetX = t.clientX
    targetY = t.clientY
    if (!userInteracted) {
      prevX = targetX
      prevY = targetY
      userInteracted = true
    }
  }
}

function handleVisibilityChange() {
  isVisible = !document.hidden
  if (isVisible && !props.isPaused) {
    startAnimation()
  } else {
    stopAnimation()
  }
}

function startAnimation() {
  if (animationFrameId) return
  let lastTime = performance.now()

  function loop(currentTime) {
    if (props.isPaused || !isVisible) {
      animationFrameId = null
      return
    }

    const dt = Math.min(currentTime - lastTime, 50)
    lastTime = currentTime
    renderFrame(currentTime, dt)

    animationFrameId = requestAnimationFrame(loop)
  }

  animationFrameId = requestAnimationFrame(loop)
}

function stopAnimation() {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

function renderFrame(time, dt) {
  if (!ctx || width === 0 || height === 0) return

  const isLight = props.theme === 'light'

  // 1. 清屏与底衬 (明亮模式为柔和清雅冰晶白底，暗黑模式为深空暗黑底)
  ctx.globalCompositeOperation = 'source-over'
  ctx.globalAlpha = 1.0
  ctx.fillStyle = isLight ? '#f8fafc' : '#08080a'
  ctx.fillRect(0, 0, width, height)

  // 2. 绘制底层 Codex 极光色彩流动画布
  const minDim = Math.min(width, height)

  if (isLight) {
    // 明亮模式：清雅明亮的高级极光色相 (珍珠白、淡蓝紫、冰青流彩)
    ctx.globalCompositeOperation = 'source-over'
    const lightOrbs = [
      { ...orbs[0], r: 129, g: 140, b: 248, alpha: 0.22 }, // 淡蓝紫
      { ...orbs[1], r: 196, g: 181, b: 253, alpha: 0.24 }, // 柔薰衣草紫
      { ...orbs[2], r: 147, g: 197, b: 253, alpha: 0.20 }, // 珍珠淡天蓝
      { ...orbs[3], r: 103, g: 232, b: 249, alpha: 0.22 }, // 冰青流彩
    ]

    for (let i = 0; i < lightOrbs.length; i++) {
      const orb = lightOrbs[i]
      const ox = (orb.baseXRatio + Math.sin(time * orb.speedX + orb.phase) * orb.ampX) * width
      const oy = (orb.baseYRatio + Math.cos(time * orb.speedY + orb.phase) * orb.ampY) * height
      const or = orb.radiusRatio * minDim

      const grad = ctx.createRadialGradient(ox, oy, 0, ox, oy, or)
      grad.addColorStop(0, `rgba(${orb.r}, ${orb.g}, ${orb.b}, ${orb.alpha})`)
      grad.addColorStop(0.5, `rgba(${orb.r}, ${orb.g}, ${orb.b}, ${orb.alpha * 0.45})`)
      grad.addColorStop(1, `rgba(${orb.r}, ${orb.g}, ${orb.b}, 0)`)

      ctx.fillStyle = grad
      ctx.beginPath()
      ctx.arc(ox, oy, or, 0, Math.PI * 2)
      ctx.fill()
    }
  } else {
    // 暗黑模式：采用 screen 滤色叠加渲染极光通透质感
    ctx.globalCompositeOperation = 'screen'

    for (let i = 0; i < orbs.length; i++) {
      const orb = orbs[i]
      const ox = (orb.baseXRatio + Math.sin(time * orb.speedX + orb.phase) * orb.ampX) * width
      const oy = (orb.baseYRatio + Math.cos(time * orb.speedY + orb.phase) * orb.ampY) * height
      const or = orb.radiusRatio * minDim

      const grad = ctx.createRadialGradient(ox, oy, 0, ox, oy, or)
      grad.addColorStop(0, `rgba(${orb.r}, ${orb.g}, ${orb.b}, 0.36)`)
      grad.addColorStop(0.45, `rgba(${orb.r}, ${orb.g}, ${orb.b}, 0.15)`)
      grad.addColorStop(1, `rgba(${orb.r}, ${orb.g}, ${orb.b}, 0)`)

      ctx.fillStyle = grad
      ctx.beginPath()
      ctx.arc(ox, oy, or, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // 恢复标准图层混合模式绘制粒子
  ctx.globalCompositeOperation = 'source-over'

  // 3. 计算鼠标插值与物理动力学
  if (!isPositionInitialized) {
    // 页面初次加载未移动时，鼠标默认停留在中央偏上位置产生待机水滴
    targetX = width * 0.5
    targetY = height * 0.35
    currentX = targetX
    currentY = targetY
    prevX = targetX
    prevY = targetY
    isPositionInitialized = true
  }

  // 阻尼缓动跟踪
  const dx = targetX - currentX
  const dy = targetY - currentY
  currentX += dx * 0.12
  currentY += dy * 0.12

  // 计算瞬时速度与加速度 (防首次跃迁)
  const instSpeed = Math.min(Math.hypot(targetX - prevX, targetY - prevY), 100)
  prevX = targetX
  prevY = targetY
  smoothSpeed += (instSpeed - smoothSpeed) * 0.1

  // 高速移动产生水滴涟漪波纹 (带有距离空间步长过滤，避免同一处过度密集重叠)
  const lastRip = ripples[ripples.length - 1]
  const distFromLastRip = lastRip ? Math.hypot(currentX - lastRip.x, currentY - lastRip.y) : 999
  if (instSpeed > 4 && ripples.length < 10 && distFromLastRip > 24) {
    ripples.push({
      x: currentX,
      y: currentY,
      radius: 12,
      maxRadius: Math.min(160, 80 + instSpeed * 2.2),
      alpha: 0.45,
    })
  }

  // 更新涟漪池
  for (let i = ripples.length - 1; i >= 0; i--) {
    const r = ripples[i]
    r.radius += 2.5
    r.alpha *= 0.94
    if (r.alpha < 0.02 || r.radius >= r.maxRadius) {
      ripples.splice(i, 1)
    }
  }

  // 4. 绘制上层 Codex 鼠标动力学 ASCII 字符水滴粒子
  const cellW = 16
  const cellH = 18
  const baseInfluenceRadius = 140
  const influenceRadius = baseInfluenceRadius + Math.min(smoothSpeed * 1.8, 80)
  const influenceRadiusSq = influenceRadius * influenceRadius

  // 网格范围截取 (仅遍历水滴影响区及涟漪周围，保证 60FPS 极速计算)
  const minCol = Math.max(0, Math.floor((currentX - influenceRadius) / cellW))
  const maxCol = Math.min(Math.floor(width / cellW), Math.ceil((currentX + influenceRadius) / cellW))
  const minRow = Math.max(0, Math.floor((currentY - influenceRadius) / cellH))
  const maxRow = Math.min(Math.floor(height / cellH), Math.ceil((currentY + influenceRadius) / cellH))

  ctx.font = '12px "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  // 水滴形变运动矢量 (沿移动方向拉伸)
  const moveAngle = Math.atan2(dy, dx)
  const moveLen = Math.hypot(dx, dy)

  // 逐层演进字符色彩配置 (明亮模式采用高对比科技靛青，暗黑模式采用纯白/紫蓝)
  for (let c = minCol; c <= maxCol; c++) {
    for (let r = minRow; r <= maxRow; r++) {
      const cx = c * cellW + cellW * 0.5
      const cy = r * cellH + cellH * 0.5

      const distDx = cx - currentX
      const distDy = cy - currentY
      const distSq = distDx * distDx + distDy * distDy

      if (distSq > influenceRadiusSq) continue

      const dist = Math.sqrt(distSq)

      // 水滴形变：沿移动方向拉伸 (Squash & Stretch)
      let normDist = dist / influenceRadius
      if (moveLen > 1.5) {
        const angleToPoint = Math.atan2(distDy, distDx)
        const cosDiff = Math.cos(angleToPoint - moveAngle)
        normDist = normDist * (1.0 - 0.22 * cosDiff)
      }

      // 根据归一化距离逐层演进字符: o (核心) -> > (内圈) -> - (中圈) -> _ (外轮廓)
      if (normDist < 0.22) {
        const alpha = Math.min(0.9, (1 - normDist / 0.22) * 0.5 + 0.45)
        ctx.fillStyle = isLight ? '#312e81' : '#ffffff'
        ctx.globalAlpha = alpha
        ctx.fillText('o', cx, cy)
      } else if (normDist < 0.48) {
        const alpha = Math.min(0.75, (1 - (normDist - 0.22) / 0.26) * 0.4 + 0.3)
        ctx.fillStyle = isLight ? '#4338ca' : '#c7d2fe'
        ctx.globalAlpha = alpha
        ctx.fillText('>', cx, cy)
      } else if (normDist < 0.76) {
        const alpha = Math.min(0.55, (1 - (normDist - 0.48) / 0.28) * 0.3 + 0.2)
        ctx.fillStyle = isLight ? '#4f46e5' : '#a5b4fc'
        ctx.globalAlpha = alpha
        ctx.fillText('-', cx, cy)
      } else if (normDist <= 1.0) {
        const alpha = Math.min(0.35, (1 - (normDist - 0.76) / 0.24) * 0.25 + 0.08)
        ctx.fillStyle = isLight ? '#6366f1' : '#818cf8'
        ctx.globalAlpha = alpha
        ctx.fillText('_', cx, cy)
      }
    }
  }

  // 5. 渲染扩散的波纹涟漪字符圈 (明亮模式高对比度皇家蓝，暗黑模式浅天蓝)
  ctx.fillStyle = isLight ? '#2563eb' : '#93c5fd'
  for (let i = 0; i < ripples.length; i++) {
    const rip = ripples[i]
    const ripMinCol = Math.max(0, Math.floor((rip.x - rip.radius - 20) / cellW))
    const ripMaxCol = Math.min(Math.floor(width / cellW), Math.ceil((rip.x + rip.radius + 20) / cellW))
    const ripMinRow = Math.max(0, Math.floor((rip.y - rip.radius - 20) / cellH))
    const ripMaxRow = Math.min(Math.floor(height / cellH), Math.ceil((rip.y + rip.radius + 20) / cellH))

    for (let c = ripMinCol; c <= ripMaxCol; c++) {
      for (let r = ripMinRow; r <= ripMaxRow; r++) {
        const cx = c * cellW + cellW * 0.5
        const cy = r * cellH + cellH * 0.5
        const d = Math.hypot(cx - rip.x, cy - rip.y)
        const ringDiff = Math.abs(d - rip.radius)

        if (ringDiff < 14) {
          const ripAlpha = (1 - ringDiff / 14) * rip.alpha
          if (ripAlpha > 0.05) {
            ctx.globalAlpha = Math.max(0, Math.min(1, ripAlpha))
            ctx.fillText(ringDiff < 6 ? '-' : '_', cx, cy)
          }
        }
      }
    }
  }

  // 6. 微光全景稀疏背景字符矩阵 (呼吸微闪)
  const sparseStepX = 6
  const sparseStepY = 4
  const ambientCols = Math.floor(width / (cellW * sparseStepX))
  const ambientRows = Math.floor(height / (cellH * sparseStepY))

  ctx.fillStyle = isLight ? '#4f46e5' : '#6366f1'
  for (let ac = 0; ac <= ambientCols; ac++) {
    for (let ar = 0; ar <= ambientRows; ar++) {
      const ax = ac * cellW * sparseStepX + cellW * 0.5
      const ay = ar * cellH * sparseStepY + cellH * 0.5

      // 距离水滴过近时不重复绘制
      const distToMouse = Math.hypot(ax - currentX, ay - currentY)
      if (distToMouse < influenceRadius * 0.9) continue

      const twinkle = Math.sin(time * 0.0015 + ac * 0.7 + ar * 0.5)
      if (twinkle > 0.2) {
        ctx.globalAlpha = (twinkle - 0.2) * (isLight ? 0.16 : 0.12)
        ctx.fillText('-', ax, ay)
      }
    }
  }

  ctx.globalAlpha = 1.0
}

let fadeTimer = null

watch(
  () => props.theme,
  () => {
    if (ctx) {
      renderFrame(performance.now(), 16)
    }
  }
)

watch(
  () => props.isPaused,
  (paused) => {
    if (fadeTimer) {
      clearTimeout(fadeTimer)
      fadeTimer = null
    }
    if (paused) {
      // 保持动画在淡出期间（700ms）持续平滑渲染，过渡完成后再停止 RAF 节约算力
      fadeTimer = setTimeout(() => {
        stopAnimation()
        fadeTimer = null
      }, 750)
    } else {
      // 重新开启时即刻恢复动画，并随 CSS 过渡平滑淡入
      if (isVisible) {
        startAnimation()
      }
    }
  }
)

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d')
    handleResize()
    // 保证首帧即刻渲染，避免冷启动或休眠模式下画布空白
    renderFrame(performance.now(), 16)

    window.addEventListener('resize', handleResize)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('touchstart', handleTouchMove, { passive: true })
    window.addEventListener('touchmove', handleTouchMove, { passive: true })
    document.addEventListener('visibilitychange', handleVisibilityChange)

    if (!props.isPaused) {
      startAnimation()
    }
  }
})

onUnmounted(() => {
  if (fadeTimer) {
    clearTimeout(fadeTimer)
    fadeTimer = null
  }
  stopAnimation()
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('touchstart', handleTouchMove)
  window.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>
