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
        errorDetail = '机房运维后台服务未连接 (HTTP 500)。请确认机房运维后台服务已正常启动'
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

  // 1. 大盘监控指标与主动自治巡检
  getMetricsSummary: () => request('/metrics/summary'),
  runAutonomousPatrol: () => request('/metrics/patrol', { method: 'POST' }),

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
  getTicketTimeline: (ticketNoOrId) => request(`/tickets/${ticketNoOrId}/timeline`),

  // 3. 资产台账与设备硬件详细参数
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
  getAsset: (assetId) => request(`/assets/${assetId}`),
  getAssetTimeline: (assetNo) => request(`/assets/${assetNo}/timeline`),
  createAsset: (payload) =>
    request('/assets/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateAsset: (assetId, payload) =>
    request(`/assets/${assetId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  deleteAsset: (assetId) =>
    request(`/assets/${assetId}`, {
      method: 'DELETE',
    }),
  getTopology: (roomCode) =>
    request(`/assets/topology${roomCode ? `?room_code=${encodeURIComponent(roomCode)}` : ''}`),
  getOverdueAssets: () => request('/assets/overdue'),
  getOverdueNotice: (assetNo) => request(`/assets/${encodeURIComponent(assetNo)}/overdue-notice`),

  // 4. 会话与历史
  getChatHistory: (sessionId) =>
    request(`/chat/history${sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : ''}`),
  listChatSessions: () => request('/chat/sessions'),

  // 5. 用户认证与典型账号
  login: (credentials) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
  register: (payload) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getDemoUsers: () => request('/auth/demo-users'),
  getUserProfile: (identifier) => request(`/auth/profile/${encodeURIComponent(identifier)}`),
  updateUserProfile: (username, data) =>
    request(`/auth/profile/${encodeURIComponent(username)}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  changePassword: (data) =>
    request('/auth/change-password', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // 6. 规章规程知识中心与 RAG 检索
  getRegulations: (params = {}) => {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        query.append(k, v)
      }
    })
    const qs = query.toString()
    return request(`/regulations${qs ? `?${qs}` : ''}`)
  },
  getRegulationDetail: (docId) => request(`/regulations/${encodeURIComponent(docId)}`),
  createRegulation: (payload) =>
    request('/regulations', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateRegulation: (docId, payload) =>
    request(`/regulations/${encodeURIComponent(docId)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  deleteRegulation: (docId) =>
    request(`/regulations/${encodeURIComponent(docId)}`, {
      method: 'DELETE',
    }),
  searchRegulations: (payload) =>
    request('/regulations/search', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getRegulationsSummary: () => request('/regulations/summary'),

  // 7. 站内待办与超期催还通知
  getNotifications: (username) => {
    const qs = username ? `?username=${encodeURIComponent(username)}` : ''
    return request(`/notifications${qs}`)
  },
  markNotificationRead: (id) =>
    request(`/notifications/${id}/read`, {
      method: 'POST',
    }),
  sendOverdueUrge: (assetNo, remark) =>
    request('/notifications/urge', {
      method: 'POST',
      body: JSON.stringify({ asset_no: assetNo, remark }),
    }),

  // 8. 机房与机柜全生命周期动态管理
  getRooms: () => request('/rooms'),
  getRoom: (roomCode) => request(`/rooms/${encodeURIComponent(roomCode)}`),
  createRoom: (payload) =>
    request('/rooms', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateRoom: (roomCode, payload) =>
    request(`/rooms/${encodeURIComponent(roomCode)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  deleteRoom: (roomCode) =>
    request(`/rooms/${encodeURIComponent(roomCode)}`, {
      method: 'DELETE',
    }),

  getRacks: (roomCode) => {
    const qs = roomCode ? `?room_code=${encodeURIComponent(roomCode)}` : ''
    return request(`/racks${qs}`)
  },
  getRack: (rackId) => request(`/racks/${encodeURIComponent(rackId)}`),
  createRack: (payload) =>
    request('/racks', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateRack: (rackId, payload) =>
    request(`/racks/${encodeURIComponent(rackId)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),
  deleteRack: (rackId) =>
    request(`/racks/${encodeURIComponent(rackId)}`, {
      method: 'DELETE',
    }),
}

