/**
 * v-backdrop-dismiss 指令
 * 作用：模态框遮罩层外部点击防误触安全关闭
 * 原理：严格要求 mousedown 与 mouseup 两个阶段的触发源 (event.target) 均精确等于当前遮罩层元素本身 (el)，
 *       从而彻底解决用户在输入框/表单中拖选文本划出弹窗边界导致弹窗被意外误关的问题。
 */
export const backdropDismiss = {
  mounted(el, binding) {
    let isDownOnBackdrop = false

    el._backdropCallback = binding.value

    el._backdropMousedownHandler = (e) => {
      isDownOnBackdrop = (e.target === el)
    }

    el._backdropMouseupHandler = (e) => {
      if (isDownOnBackdrop && e.target === el) {
        const cb = el._backdropCallback || binding.value
        if (typeof cb === 'function') {
          cb(e)
        }
      }
      isDownOnBackdrop = false
    }

    el.addEventListener('mousedown', el._backdropMousedownHandler)
    el.addEventListener('mouseup', el._backdropMouseupHandler)
  },
  updated(el, binding) {
    el._backdropCallback = binding.value
  },
  unmounted(el) {
    if (el._backdropMousedownHandler) {
      el.removeEventListener('mousedown', el._backdropMousedownHandler)
      delete el._backdropMousedownHandler
    }
    if (el._backdropMouseupHandler) {
      el.removeEventListener('mouseup', el._backdropMouseupHandler)
      delete el._backdropMouseupHandler
    }
    delete el._backdropCallback
  },
}
