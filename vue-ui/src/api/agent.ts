const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export interface AgentSourceConfig {
  sources: string[]
  default_selected: string[]
  labels: Record<string, string>
}

export interface AgentStreamEvent {
  event: string
  data: Record<string, any>
}

export interface AgentMessagePayload {
  role: 'user'
  content: string
  platform: string[]
  timestamp: number
  session_id: string
}

export const getAgentSourceConfig = async (): Promise<AgentSourceConfig> => {
  const response = await fetch(`${API_BASE_URL}/agent/config/sources`, {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new Error(`无法加载来源（HTTP ${response.status}）`)
  }

  return response.json()
}

const parseEventBlock = (block: string): AgentStreamEvent | null => {
  let event = 'message'
  const dataLines: string[] = []

  for (const line of block.split(/\r?\n/)) {
    if (line.startsWith('event:')) {
      event = line.slice(6).trim()
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  }

  if (!dataLines.length) return null

  return {
    event,
    data: JSON.parse(dataLines.join('\n')),
  }
}

export const streamAgentMessage = async (
  sessionId: string,
  payload: AgentMessagePayload,
  signal: AbortSignal,
  onEvent: (event: AgentStreamEvent) => void,
): Promise<void> => {
  const response = await fetch(
    `${API_BASE_URL}/agent/sessions/${encodeURIComponent(sessionId)}/message`,
    {
      method: 'POST',
      headers: {
        Accept: 'text/event-stream',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal,
    },
  )

  if (!response.ok) {
    let message = `请求失败（HTTP ${response.status}）`
    try {
      const body = await response.json()
      message = body?.message || body?.detail || message
    } catch {
      // Keep the HTTP fallback when the upstream response is not JSON.
    }
    throw new Error(message)
  }

  if (!response.body) {
    throw new Error('浏览器无法读取流式响应')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done })

    let boundary = buffer.search(/\r?\n\r?\n/)
    while (boundary !== -1) {
      const block = buffer.slice(0, boundary)
      const separator = buffer.slice(boundary).match(/^\r?\n\r?\n/)?.[0] || '\n\n'
      buffer = buffer.slice(boundary + separator.length)

      if (block.trim()) {
        const parsed = parseEventBlock(block)
        if (parsed) onEvent(parsed)
      }
      boundary = buffer.search(/\r?\n\r?\n/)
    }

    if (done) break
  }

  if (buffer.trim()) {
    const parsed = parseEventBlock(buffer)
    if (parsed) onEvent(parsed)
  }
}

export const cancelAgentRun = async (sessionId: string): Promise<void> => {
  await fetch(`${API_BASE_URL}/agent/sessions/${encodeURIComponent(sessionId)}/cancel`, {
    method: 'POST',
    headers: { Accept: 'application/json' },
  })
}
