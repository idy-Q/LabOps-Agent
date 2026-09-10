/**
 * LabOps-Agent 前端 REST API 统一客户端
 */

const BASE_URL = '/api'

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`
  const defaultHeaders = {
    'Content-Type': 'application/json',
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  })

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}: ${response.statusText}`
    try {
      const errJson = await response.json()
      if (typeof errJson.detail === 'string') {
        errorDetail = errJson.detail
      } else if (Array.isArray(errJson.detail)) {
        errorDetail = errJson.detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
      } else if (errJson.message) {
        errorDetail = errJson.message
      }
    } catch {
      if (response.status === 500) {
        errorDetail = '后端服务连接失败 (HTTP 500)。请确认后端 FastAPI 服务已在 8000 端口启动'
      }
    }
    throw new Error(errorDetail)
  }

  // 针对 204 No Content
  if (response.status === 204) {
    return null
  }

  return response.json()
}

export const api = {
  // 0. 健康检查
  getHealth: () => request('/health'),

  // 1. 大盘监控指标
  getMetricsSummary: () => request('/metrics/summary'),

  // 2. 运维工单
  listTickets: (params = {}) => {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        query.append(k, v)
      }
    })
    const qs = query.toString()
    return request(`/tickets/${qs ? `?${qs}` : ''}`)
  },
  createTicket: (payload) =>
    request('/tickets/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateTicket: (ticketId, payload) =>
    request(`/tickets/${ticketId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  deleteTicket: (ticketId) =>
    request(`/tickets/${ticketId}`, {
      method: 'DELETE',
    }),

  // 3. 资产台账
  listAssets: (params = {}) => {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        query.append(k, v)
      }
    })
    const qs = query.toString()
    return request(`/assets/${qs ? `?${qs}` : ''}`)
  },
  updateAsset: (assetId, payload) =>
    request(`/assets/${assetId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  // 4. 会话与历史
  getChatHistory: (sessionId) =>
    request(`/chat/history${sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : ''}`),
  listChatSessions: () => request('/chat/sessions'),
}
