/**
 * LabOps-Agent SSE 流式协议客户端解析器
 *
 * 处理细粒度结构化事件分发：
 * - think: 仿 DeepSeek-R1 思考过程
 * - tool_start / tool_end: 工具调用入参与执行结果
 * - citation: 机房规程检索溯源标签
 * - ticket_mutation: 工单状态突变（触发右侧高亮新增）
 * - asset_mutation: 资产台账突变（触发右侧同步刷新）
 * - content: 助手回复正文
 * - done: 完成信号
 */

export async function fetchSSE({
  prompt,
  sessionId,
  onEvent,
  onError,
  onFinish,
  signal,
}) {
  let finished = false
  const safeFinish = () => {
    if (!finished) {
      finished = true
      if (onFinish) {
        try {
          onFinish()
        } catch (e) {
          console.error('onFinish 执行异常:', e)
        }
      }
    }
  }

  try {
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt,
        session_id: sessionId || undefined,
      }),
      signal,
    })

    if (!response.ok) {
      let errText = `HTTP ${response.status}: ${response.statusText}`
      try {
        const errJson = await response.json()
        if (typeof errJson.detail === 'string') {
          errText = errJson.detail
        } else if (Array.isArray(errJson.detail)) {
          errText = errJson.detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
        } else if (errJson.message) {
          errText = errJson.message
        }
      } catch {
        if (response.status === 500) {
          errText = '后端服务未连接 (HTTP 500)。请在另一终端窗口启动后端 FastAPI 服务 (端口 8000)'
        }
      }
      throw new Error(errText)
    }

    if (!response.body) {
      throw new Error('当前浏览器环境不支持 ReadableStream 流式响应')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留未成行的末尾残余

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || trimmed.startsWith(':')) {
          // 心跳或注释行
          continue
        }

        if (trimmed.startsWith('data:')) {
          const rawData = trimmed.slice(5).trim()
          if (!rawData) continue
          try {
            const event = JSON.parse(rawData)
            if (onEvent) {
              onEvent(event)
            }
          } catch (e) {
            console.warn('SSE 数据帧解析警告:', e, rawData)
          }
        }
      }
    }

    // 刷新尾部可能遗留的缓冲区
    if (buffer.trim().startsWith('data:')) {
      const rawData = buffer.trim().slice(5).trim()
      if (rawData) {
        try {
          const event = JSON.parse(rawData)
          if (onEvent) onEvent(event)
        } catch {
          // ignore
        }
      }
    }

    safeFinish()
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('SSE 连接由用户主动中止')
    } else {
      console.error('SSE 流式传输异常:', error)
      if (onError) onError(error)
    }
    safeFinish()
  }
}
