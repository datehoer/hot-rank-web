<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  ArrowLeftIcon,
  ArrowPathIcon,
  CheckIcon,
  ChevronDownIcon,
  HandThumbDownIcon,
  HandThumbUpIcon,
  MagnifyingGlassIcon,
  PaperAirplaneIcon,
  PlusIcon,
  RocketLaunchIcon,
  StopIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'
import {
  cancelAgentRun,
  getAgentSourceConfig,
  streamAgentMessage,
  type AgentStreamEvent,
} from '@/api/agent'
import {
  renderSafeMarkdown,
  safeExternalUrl,
} from '@/utils/safeAgentContent'
import { lengthBucket, trackAgentEvent } from '@/utils/agentAnalytics'

interface TopicContext {
  title: string
  source: string
  rank: number
  url?: string
}

interface Citation {
  source_id?: string
  title?: string
  url?: string
  platform?: string
  number?: number
}

interface ConversationTurn {
  id: string
  question: string
  answer: string
  askedAt: Date
  citations: Citation[]
  executionItems: ExecutionItem[]
  executionExpanded: boolean
  error?: string
  errorCode?: string
  warning?: string
  incomplete?: boolean
  rating?: 'up' | 'down'
}

interface ProcessStep {
  stage: string
  label: string
}

interface ExecutionItem {
  kind: 'reasoning' | 'tool'
  id: string
  label: string
  text?: string
  detail?: string
  summary?: string
  status: 'running' | 'completed' | 'failed' | 'skipped'
  durationMs?: number
}

type AgentStage =
  | 'idle'
  | 'connecting'
  | 'planning'
  | 'searching'
  | 'fetching'
  | 'comparing'
  | 'generating'
  | 'completed'
  | 'stopped'
  | 'error'

const isOpen = ref(false)
const draft = ref('')
const topicContext = ref<TopicContext | null>(null)
const turns = ref<ConversationTurn[]>([])
const stage = ref<AgentStage>('idle')
const processSteps = ref<ProcessStep[]>([])
const sources = ref<string[]>([])
const selectedSources = ref<string[]>([])
const sourceLabels = ref<Record<string, string>>({})
const sourcePickerOpen = ref(false)
const sourceSearch = ref('')
const sourceError = ref('')
const loadingSources = ref(false)
const streamEnded = ref(false)
const inputElement = ref<HTMLTextAreaElement | null>(null)
const conversationElement = ref<HTMLElement | null>(null)
const sourcePickerElement = ref<HTMLElement | null>(null)
const sourceButtonElement = ref<HTMLButtonElement | null>(null)
const sourceSearchElement = ref<HTMLInputElement | null>(null)
const controller = ref<AbortController | null>(null)
let runStartedAt = 0
let firstDeltaSent = false

const SESSION_KEY = 'hotday-agent-session-id'

const createSessionId = () => {
  if (window.crypto?.randomUUID) return window.crypto.randomUUID()
  return `agent-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

const getSessionId = () => {
  let id = sessionStorage.getItem(SESSION_KEY)
  if (!id) {
    id = createSessionId()
    sessionStorage.setItem(SESSION_KEY, id)
  }
  return id
}

const activeTurn = computed<ConversationTurn | null>(() =>
  turns.value.length ? turns.value[turns.value.length - 1] : null,
)
const safeTopicUrl = computed(() => safeExternalUrl(topicContext.value?.url))
const isRunning = computed(() =>
  ['connecting', 'planning', 'searching', 'fetching', 'comparing', 'generating'].includes(
    stage.value,
  ),
)
const canSend = computed(
  () => draft.value.trim().length > 0 && selectedSources.value.length > 0 && !isRunning.value,
)
const sourceSummary = computed(() => {
  if (!sources.value.length) return loadingSources.value ? '加载来源' : '暂无来源'
  if (selectedSources.value.length === sources.value.length) {
    return `全部来源 ${sources.value.length}`
  }
  return `已选 ${selectedSources.value.length}/${sources.value.length}`
})
const filteredSources = computed(() => {
  const query = sourceSearch.value.trim().toLocaleLowerCase()
  if (!query) return sources.value

  return sources.value.filter((source) => {
    const label = sourceLabels.value[source] || source
    return (
      source.toLocaleLowerCase().includes(query) ||
      label.toLocaleLowerCase().includes(query)
    )
  })
})

const stageLabels: Record<AgentStage, string> = {
  idle: '等待提问',
  connecting: '正在连接热点助手',
  planning: '正在理解问题',
  searching: '正在检索相关热点',
  fetching: '正在读取新闻来源',
  comparing: '正在比较不同报道',
  generating: '正在生成回答',
  completed: '回答已完成',
  stopped: '已停止生成',
  error: '生成失败',
}

const visibleSteps = computed(() => {
  return processSteps.value.map((step, index) => ({
    ...step,
    state:
      index === processSteps.value.length - 1 && step.stage === stage.value && isRunning.value
        ? 'active'
        : 'complete',
  }))
})

const scrollToLatest = async () => {
  await nextTick()
  if (conversationElement.value) {
    conversationElement.value.scrollTop = conversationElement.value.scrollHeight
  }
}

const focusInput = async () => {
  await nextTick()
  inputElement.value?.focus()
}

const open = (entrySource: 'global' | 'rank_card' = 'global') => {
  isOpen.value = true
  void loadSources()
  void focusInput()
  trackAgentEvent('agent_panel_open', { entry_source: entrySource })
}

const close = () => {
  isOpen.value = false
  sourcePickerOpen.value = false
  trackAgentEvent('agent_panel_close', {
    run_active: isRunning.value,
    conversation_turns: turns.value.length,
  })
}

const openForTopic = (topic: TopicContext) => {
  topicContext.value = topic
  draft.value = '帮我看看这件事的最新进展'
  open('rank_card')
  trackAgentEvent('agent_topic_context_add', {
    platform: topic.source,
    context_count: 1,
  })
}

const newConversation = () => {
  const previousTurns = turns.value.length
  if (isRunning.value) stopGeneration()
  turns.value = []
  topicContext.value = null
  draft.value = ''
  stage.value = 'idle'
  processSteps.value = []
  sessionStorage.setItem(SESSION_KEY, createSessionId())
  void focusInput()
  if (previousTurns > 0) {
    trackAgentEvent('agent_session_clear', { conversation_turns: previousTurns })
  }
}

const loadSources = async () => {
  if (sources.value.length || loadingSources.value) return
  loadingSources.value = true
  sourceError.value = ''
  try {
    const config = await getAgentSourceConfig()
    sources.value = Array.isArray(config.sources) ? config.sources : []
    sourceLabels.value = config.labels || {}
    const defaults = Array.isArray(config.default_selected)
      ? config.default_selected
      : sources.value
    selectedSources.value = defaults.filter((source) => sources.value.includes(source))
  } catch (error) {
    sourceError.value = error instanceof Error ? error.message : '无法加载来源'
  } finally {
    loadingSources.value = false
  }
}

const toggleSource = (source: string) => {
  selectedSources.value = selectedSources.value.includes(source)
    ? selectedSources.value.filter((item) => item !== source)
    : [...selectedSources.value, source]
}

const selectAllSources = () => {
  selectedSources.value = [...sources.value]
}

const toggleSourcePicker = async () => {
  sourcePickerOpen.value = !sourcePickerOpen.value
  if (sourcePickerOpen.value) {
    await nextTick()
    sourceSearchElement.value?.focus()
  }
}

const closeSourcePicker = () => {
  sourcePickerOpen.value = false
}

const handleDocumentPointerDown = (event: PointerEvent) => {
  if (!sourcePickerOpen.value) return
  const target = event.target as Node
  if (
    sourcePickerElement.value?.contains(target) ||
    sourceButtonElement.value?.contains(target)
  ) {
    return
  }
  closeSourcePicker()
}

const handleDocumentKeydown = (event: KeyboardEvent) => {
  if (event.key !== 'Escape' || !sourcePickerOpen.value) return
  closeSourcePicker()
  sourceButtonElement.value?.focus()
}

const setStage = (nextStage: AgentStage) => {
  stage.value = nextStage
}

const recordProcessStep = (nextStage: string, message?: unknown) => {
  if (nextStage === 'generating') return

  const label =
    typeof message === 'string' && message.trim()
      ? message.trim()
      : stageLabels[nextStage as AgentStage] || nextStage
  const previous = processSteps.value[processSteps.value.length - 1]
  if (previous?.stage === nextStage && previous.label === label) return
  processSteps.value.push({ stage: nextStage, label })
}

const upsertReasoning = (data: Record<string, unknown>) => {
  const turn = activeTurn.value
  if (!turn) return

  const id = String(data.id || `reasoning-${data.round || 1}`)
  let item = turn.executionItems.find(
    (candidate) => candidate.kind === 'reasoning' && candidate.id === id,
  )
  if (!item) {
    item = {
      kind: 'reasoning',
      id,
      label: data.round ? `第 ${data.round} 轮分析` : '执行思路',
      text: '',
      status: 'running',
    }
    turn.executionItems.push(item)
  }

  if (typeof data.delta === 'string') item.text = `${item.text || ''}${data.delta}`
  if (typeof data.text === 'string' && data.text) item.text = data.text
  item.status = data.status === 'completed' ? 'completed' : 'running'
}

const addToolCall = (data: Record<string, unknown>) => {
  const turn = activeTurn.value
  if (!turn) return

  const id = String(data.call_id || `tool-${turn.executionItems.length}`)
  const existing = turn.executionItems.find(
    (candidate) => candidate.kind === 'tool' && candidate.id === id,
  )
  if (existing) return

  turn.executionItems.push({
    kind: 'tool',
    id,
    label: String(data.label || '调用热点工具'),
    detail: typeof data.detail === 'string' ? data.detail : '',
    status: 'running',
  })
}

const completeToolCall = (data: Record<string, unknown>) => {
  const turn = activeTurn.value
  if (!turn) return

  const id = String(data.call_id || '')
  let item = turn.executionItems.find(
    (candidate) => candidate.kind === 'tool' && candidate.id === id,
  )
  if (!item) {
    item = {
      kind: 'tool',
      id: id || `tool-result-${turn.executionItems.length}`,
      label: '热点工具',
      status: 'running',
    }
    turn.executionItems.push(item)
  }

  const nextStatus = String(data.status || 'completed')
  item.status = ['completed', 'failed', 'skipped'].includes(nextStatus)
    ? (nextStatus as ExecutionItem['status'])
    : 'completed'
  item.summary = typeof data.summary === 'string' ? data.summary : ''
  item.durationMs = Number.isFinite(Number(data.duration_ms))
    ? Number(data.duration_ms)
    : undefined
}

const executionSummary = (turn: ConversationTurn) => {
  const running = [...turn.executionItems].reverse().find((item) => item.status === 'running')
  if (running) return running.label
  return `${turn.executionItems.length} 项执行记录`
}

const handleStreamEvent = (event: AgentStreamEvent) => {
  if (event.event === 'meta') {
    setStage('planning')
    recordProcessStep('planning')
    if (runStartedAt) {
      trackAgentEvent('agent_run_connected', {
        connect_ms: Math.round(performance.now() - runStartedAt),
      })
    }
  } else if (event.event === 'status') {
    const nextStage = String(event.data.stage || '') as AgentStage
    if (nextStage in stageLabels) {
      setStage(nextStage)
      recordProcessStep(nextStage, event.data.message)
    }
  } else if (event.event === 'reasoning') {
    upsertReasoning(event.data)
    void scrollToLatest()
  } else if (event.event === 'tool_call') {
    addToolCall(event.data)
    void scrollToLatest()
  } else if (event.event === 'tool_result') {
    completeToolCall(event.data)
    void scrollToLatest()
  } else if (event.event === 'delta') {
    setStage('generating')
    if (activeTurn.value) activeTurn.value.answer += String(event.data.text || '')
    if (!firstDeltaSent) {
      firstDeltaSent = true
      const turn = activeTurn.value
      const toolStageSeen = turn
        ? turn.executionItems.some((item) => item.kind === 'tool')
        : false
      trackAgentEvent('agent_first_delta', {
        first_delta_ms: runStartedAt
          ? Math.round(performance.now() - runStartedAt)
          : 0,
        tool_stage_seen: toolStageSeen,
      })
    }
    void scrollToLatest()
  } else if (event.event === 'citation') {
    const citation = (event.data.citation || event.data) as Citation
    if (activeTurn.value) {
      const key = citation.source_id || citation.url || citation.title
      const exists = activeTurn.value.citations.some(
        (item: Citation) => (item.source_id || item.url || item.title) === key,
      )
      if (!exists) activeTurn.value.citations.push(citation)
    }
  } else if (event.event === 'warning') {
    if (activeTurn.value) {
      activeTurn.value.warning = String(event.data.message || '')
    }
  } else if (event.event === 'done') {
    streamEnded.value = true
    setStage('completed')
    const turn = activeTurn.value
    trackAgentEvent('agent_run_complete', {
      duration_ms: runStartedAt
        ? Math.round(performance.now() - runStartedAt)
        : 0,
      citation_count: turn ? turn.citations.length : 0,
      finish_reason: 'complete',
      output_length_bucket: lengthBucket(turn ? turn.answer.length : 0),
    })
  } else if (event.event === 'error') {
    streamEnded.value = true
    const message = String(event.data.message || '热点助手暂时无法回答，请重试')
    const errorCode = String(event.data.code || 'UNKNOWN')
    if (activeTurn.value) {
      activeTurn.value.error = message
      activeTurn.value.errorCode = errorCode
      activeTurn.value.incomplete = Boolean(activeTurn.value.answer)
    }
    trackAgentEvent('agent_run_error', {
      error_code: errorCode,
      retryable: Boolean(event.data.retryable),
      partial_content: Boolean(activeTurn.value?.answer),
    })
    setStage(errorCode === 'RUN_CANCELLED' ? 'stopped' : 'error')
  }
}

const buildQuestion = (question: string) => {
  if (!topicContext.value) return question
  return `${question}\n\n当前热点：${topicContext.value.title}`
}

const send = async () => {
  if (!canSend.value) return

  const question = draft.value.trim()
  const sessionId = getSessionId()
  runStartedAt = performance.now()
  firstDeltaSent = false
  trackAgentEvent('agent_message_submit', {
    input_length_bucket: lengthBucket(question.length),
    context_count: topicContext.value ? 1 : 0,
    turn_index: turns.value.length + 1,
  })
  const turn: ConversationTurn = {
    id: `${Date.now()}`,
    question,
    answer: '',
    askedAt: new Date(),
    citations: [],
    executionItems: [],
    executionExpanded: false,
  }

  turns.value.push(turn)
  draft.value = ''
  processSteps.value = []
  setStage('connecting')
  streamEnded.value = false
  controller.value = new AbortController()
  sourcePickerOpen.value = false
  await scrollToLatest()

  try {
    await streamAgentMessage(
      sessionId,
      {
        role: 'user',
        content: buildQuestion(question),
        platform: selectedSources.value,
        timestamp: Math.floor(Date.now() / 1000),
        session_id: sessionId,
      },
      controller.value.signal,
      handleStreamEvent,
    )

    if (!streamEnded.value) {
      turn.error = '连接提前结束，请重新尝试'
      turn.incomplete = Boolean(turn.answer)
      setStage('error')
    }
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      turn.incomplete = Boolean(turn.answer)
      setStage('stopped')
    } else {
      turn.error = error instanceof Error ? error.message : '请求失败，请重试'
      turn.incomplete = Boolean(turn.answer)
      setStage('error')
    }
  } finally {
    controller.value = null
    await scrollToLatest()
  }
}

const stopGeneration = () => {
  const sessionId = getSessionId()
  trackAgentEvent('agent_run_cancel', {
    elapsed_ms: runStartedAt ? Math.round(performance.now() - runStartedAt) : 0,
    stage: stage.value,
  })
  controller.value?.abort()
  controller.value = null
  if (activeTurn.value) activeTurn.value.incomplete = Boolean(activeTurn.value.answer)
  setStage('stopped')
  void cancelAgentRun(sessionId).catch(() => undefined)
}

const retry = () => {
  const previousQuestion = activeTurn.value?.question
  if (!previousQuestion) return
  trackAgentEvent('agent_run_retry', {
    previous_error_code: activeTurn.value?.errorCode || 'unknown',
  })
  draft.value = previousQuestion
  void send()
}

const pickSuggestion = (suggestionId: string, text: string) => {
  draft.value = text
  void focusInput()
  trackAgentEvent('agent_suggestion_click', { suggestion_id: suggestionId })
}

const trackCitationClick = (citation: Citation, index: number) => {
  trackAgentEvent('agent_citation_click', {
    citation_position: index + 1,
    platform: citation.platform || 'unknown',
  })
}

const submitFeedback = (turn: ConversationTurn, rating: 'up' | 'down') => {
  if (turn.rating === rating) return
  turn.rating = rating
  trackAgentEvent('agent_feedback_submit', { rating })
}

const removeTopicContext = () => {
  if (!topicContext.value) return
  const platform = topicContext.value.source
  topicContext.value = null
  trackAgentEvent('agent_topic_context_remove', {
    platform,
    context_count: 0,
  })
}

const openLauncher = () => {
  trackAgentEvent('agent_launcher_click', { panel_was_open: false })
  open('global')
}

const isTurnFinalized = (turn: ConversationTurn) =>
  turn !== activeTurn.value ||
  ['completed', 'stopped', 'error'].includes(stage.value)

const handleComposerKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void send()
  }
}

const formatTime = (date: Date) =>
  new Intl.DateTimeFormat('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }).format(
    date,
  )

const renderAnswer = (answer: string) => renderSafeMarkdown(answer)
const visibleCitations = (turn: ConversationTurn) =>
  turn.citations.filter((citation) => safeExternalUrl(citation.url))

onMounted(() => {
  void loadSources()
  document.addEventListener('pointerdown', handleDocumentPointerDown)
  document.addEventListener('keydown', handleDocumentKeydown)

  trackAgentEvent('agent_entry_impression', { entry_source: 'global' })

  const existingSession = sessionStorage.getItem(SESSION_KEY)
  if (existingSession) {
    trackAgentEvent('agent_session_restore', { result: 'restored' })
  } else {
    getSessionId()
    trackAgentEvent('agent_session_create', { result: 'created' })
  }
})
onBeforeUnmount(() => {
  controller.value?.abort()
  document.removeEventListener('pointerdown', handleDocumentPointerDown)
  document.removeEventListener('keydown', handleDocumentKeydown)
})

defineExpose({ open, openForTopic })
</script>

<template>
  <button
    v-if="!isOpen"
    type="button"
    class="agent-launcher"
    aria-label="打开热点助手"
    @click="openLauncher"
  >
    <RocketLaunchIcon aria-hidden="true" />
    <span>热点助手</span>
  </button>

  <Transition name="agent-panel">
    <aside v-if="isOpen" class="agent-panel" aria-label="热点助手" aria-live="polite">
      <header class="agent-header">
        <button type="button" class="agent-mobile-back" aria-label="返回" @click="close">
          <ArrowLeftIcon />
        </button>
        <h2>热点助手</h2>
        <button type="button" class="agent-new-conversation" @click="newConversation">
          <PlusIcon />
          <span>新对话</span>
        </button>
        <button type="button" class="agent-close" aria-label="关闭热点助手" @click="close">
          <XMarkIcon />
        </button>
      </header>

      <section v-if="topicContext" class="agent-context" aria-label="当前热点">
        <div class="agent-context-body">
          <span>来自：{{ topicContext.source }} #{{ topicContext.rank }}</span>
          <a
            v-if="safeTopicUrl"
            :href="safeTopicUrl"
            target="_blank"
            rel="noopener noreferrer nofollow"
          >
            {{ topicContext.title }}
          </a>
          <strong v-else>{{ topicContext.title }}</strong>
        </div>
        <button
          type="button"
          class="agent-context-remove"
          aria-label="移除热点上下文"
          @click="removeTopicContext"
        >
          <XMarkIcon />
        </button>
      </section>

      <section ref="conversationElement" class="agent-conversation">
        <div v-if="!turns.length" class="agent-empty">
          <MagnifyingGlassIcon />
          <h3>从热点开始提问</h3>
          <p>我会从已收录的热点和新闻来源中检索、阅读并整理回答。</p>
          <button type="button" @click="pickSuggestion('today_hot', '今天有哪些值得关注的热点？')">
            今天有哪些值得关注的热点？
          </button>
          <button type="button" @click="pickSuggestion('compare_platforms', '对比一下今天不同平台的热门话题')">
            对比不同平台的热门话题
          </button>
        </div>

        <article v-for="turn in turns" :key="turn.id" class="agent-turn">
          <div class="agent-user-row">
            <p>{{ turn.question }}</p>
            <time>{{ formatTime(turn.askedAt) }}</time>
          </div>

          <ol v-if="turn === activeTurn && visibleSteps.length" class="agent-steps">
            <li
              v-for="(step, stepIndex) in visibleSteps"
              :key="`${step.stage}-${stepIndex}`"
              :data-state="step.state"
            >
              <span class="agent-step-marker">
                <CheckIcon v-if="step.state === 'complete'" />
                <span v-else-if="step.state === 'active'" class="agent-spinner"></span>
              </span>
              <span>{{ step.label }}</span>
            </li>
          </ol>

          <section v-if="turn.executionItems.length" class="agent-execution">
            <button
              type="button"
              class="agent-execution-toggle"
              :aria-expanded="turn.executionExpanded"
              @click="turn.executionExpanded = !turn.executionExpanded"
            >
              <span class="agent-execution-symbol">&gt;_</span>
              <span class="agent-execution-title">
                <strong>执行详情</strong>
                <small>{{ executionSummary(turn) }}</small>
              </span>
              <ChevronDownIcon :data-open="turn.executionExpanded" />
            </button>

            <div v-if="turn.executionExpanded" class="agent-execution-list">
              <article
                v-for="item in turn.executionItems"
                :key="`${item.kind}-${item.id}`"
                class="agent-execution-item"
                :data-status="item.status"
              >
                <span class="agent-execution-marker">
                  <span v-if="item.status === 'running'" class="agent-spinner"></span>
                  <CheckIcon v-else-if="item.status === 'completed'" />
                  <span v-else>—</span>
                </span>
                <div>
                  <strong>{{ item.label }}</strong>
                  <p v-if="item.kind === 'reasoning' && item.text">{{ item.text }}</p>
                  <p v-else-if="item.detail">{{ item.detail }}</p>
                  <small v-if="item.summary">
                    {{ item.summary }}
                    <template v-if="item.durationMs !== undefined">
                      · {{ item.durationMs }}ms
                    </template>
                  </small>
                </div>
              </article>
            </div>
          </section>

          <div v-if="turn.answer" class="agent-answer">
            <div class="agent-answer-markdown" v-html="renderAnswer(turn.answer)"></div>
            <span v-if="turn === activeTurn && stage === 'generating'" class="agent-cursor"></span>
          </div>

          <div
            v-if="turn.answer && isTurnFinalized(turn)"
            class="agent-feedback"
            role="group"
            aria-label="回答反馈"
          >
            <button
              type="button"
              :aria-pressed="turn.rating === 'up'"
              aria-label="回答有帮助"
              @click="submitFeedback(turn, 'up')"
            >
              <HandThumbUpIcon />
            </button>
            <button
              type="button"
              :aria-pressed="turn.rating === 'down'"
              aria-label="回答没有帮助"
              @click="submitFeedback(turn, 'down')"
            >
              <HandThumbDownIcon />
            </button>
          </div>

          <p v-if="turn.warning" class="agent-warning" role="status">
            {{ turn.warning }}
          </p>

          <div
            v-if="turn === activeTurn && (stage === 'connecting' || stage === 'generating')"
            class="agent-live-status"
          >
            <span class="agent-spinner"></span>
            <span>{{ stageLabels[stage] }}</span>
          </div>

          <section v-if="visibleCitations(turn).length" class="agent-citations">
            <div class="agent-citation-heading">
              <strong>参考热点 {{ visibleCitations(turn).length }}</strong>
              <span></span>
            </div>
            <a
              v-for="(citation, index) in visibleCitations(turn)"
              :key="citation.source_id || citation.url || citation.title"
              :href="safeExternalUrl(citation.url) || undefined"
              target="_blank"
              rel="noopener noreferrer nofollow"
              class="agent-citation"
              @click="trackCitationClick(citation, index)"
            >
              <strong>{{ citation.platform || '热点来源' }}</strong>
              <span>{{ citation.title || citation.url }}</span>
            </a>
          </section>

          <div v-if="turn.error" class="agent-error" role="alert">
            <strong>没有完成这次回答</strong>
            <span>{{ turn.error }}</span>
            <button v-if="stage === 'error'" type="button" @click="retry">
              <ArrowPathIcon />
              重新尝试
            </button>
          </div>

          <p v-else-if="turn.incomplete && stage === 'stopped'" class="agent-stopped">
            已停止生成，已收到的内容会保留。
          </p>
        </article>
      </section>

      <footer class="agent-composer-wrap">
        <div
          v-if="sourcePickerOpen"
          ref="sourcePickerElement"
          class="agent-source-picker"
          role="dialog"
          aria-label="选择查询来源"
        >
          <header>
            <strong>查询来源</strong>
            <button type="button" @click="selectAllSources">全部选择</button>
          </header>
          <div class="agent-source-search">
            <MagnifyingGlassIcon aria-hidden="true" />
            <input
              ref="sourceSearchElement"
              v-model="sourceSearch"
              type="search"
              placeholder="搜索来源"
              aria-label="搜索查询来源"
            />
          </div>
          <p v-if="sourceError" class="agent-source-error">{{ sourceError }}</p>
          <div v-else class="agent-source-list">
            <label v-for="source in filteredSources" :key="source">
              <input
                type="checkbox"
                :checked="selectedSources.includes(source)"
                @change="toggleSource(source)"
              />
              <span>{{ sourceLabels[source] || source }}</span>
            </label>
            <p v-if="!filteredSources.length" class="agent-source-empty">没有匹配的来源</p>
          </div>
        </div>

        <div class="agent-composer" :data-running="isRunning">
          <textarea
            ref="inputElement"
            v-model="draft"
            rows="1"
            :placeholder="isRunning ? stageLabels[stage] : '继续追问…'"
            :disabled="isRunning"
            aria-label="向热点助手提问"
            @keydown="handleComposerKeydown"
          ></textarea>
          <div class="agent-composer-actions">
            <button
              ref="sourceButtonElement"
              type="button"
              class="agent-source-button"
              :aria-expanded="sourcePickerOpen"
              @click="toggleSourcePicker"
            >
              <MagnifyingGlassIcon />
              <span>{{ sourceSummary }}</span>
              <ChevronDownIcon />
            </button>
            <button
              v-if="isRunning"
              type="button"
              class="agent-primary-action agent-stop"
              @click="stopGeneration"
            >
              <StopIcon />
              <span>停止</span>
            </button>
            <button
              v-else
              type="button"
              class="agent-primary-action"
              :disabled="!canSend"
              aria-label="发送"
              @click="send"
            >
              <PaperAirplaneIcon />
            </button>
          </div>
        </div>
      </footer>
    </aside>
  </Transition>
</template>

<style scoped>
.agent-launcher {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 70;
  display: flex;
  align-items: center;
  gap: 10px;
  height: 58px;
  border: 1px solid #111;
  border-radius: 30px;
  background: #050505;
  color: #fff;
  padding: 0 20px 0 17px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 8px 28px rgb(0 0 0 / 18%);
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.agent-launcher:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 34px rgb(0 0 0 / 22%);
}

.agent-launcher svg {
  width: 24px;
  height: 24px;
}

.agent-panel {
  position: fixed;
  top: 24px;
  right: 24px;
  bottom: 24px;
  z-index: 80;
  display: flex;
  width: min(460px, calc(100vw - 48px));
  min-width: 420px;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #cfcfcf;
  border-radius: 10px;
  background: #fff;
  color: #111;
  box-shadow:
    0 22px 60px rgb(0 0 0 / 13%),
    0 3px 12px rgb(0 0 0 / 7%);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.agent-header {
  display: flex;
  min-height: 78px;
  align-items: center;
  gap: 12px;
  padding: 0 30px;
}

.agent-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
}

.agent-header button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  background: transparent;
  color: inherit;
}

.agent-new-conversation {
  margin-left: auto;
  gap: 5px;
  padding: 8px;
  font-size: 13px;
}

.agent-new-conversation svg,
.agent-close svg,
.agent-mobile-back svg {
  width: 22px;
  height: 22px;
}

.agent-close {
  padding: 8px;
}

.agent-mobile-back {
  display: none !important;
}

.agent-context {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 0 28px 4px;
  border: 1px solid #dedede;
  border-radius: 7px;
  background: #fafafa;
  padding: 13px 15px;
}

.agent-context-body {
  min-width: 0;
  flex: 1;
}

.agent-context-remove {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  color: #888;
  padding: 2px;
  cursor: pointer;
}

.agent-context-remove svg {
  width: 16px;
  height: 16px;
}

.agent-context span {
  display: block;
  margin-bottom: 5px;
  color: #5d5d5d;
  font-size: 12px;
}

.agent-context a,
.agent-context strong {
  color: inherit;
  font-size: 16px;
  font-weight: 750;
  text-decoration: none;
}

.agent-conversation {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
  padding: 18px 28px 32px;
  scroll-behavior: smooth;
}

.agent-empty {
  display: flex;
  min-height: 70%;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  color: #202020;
}

.agent-empty > svg {
  width: 34px;
  height: 34px;
  margin-bottom: 20px;
}

.agent-empty h3 {
  margin: 0 0 8px;
  font-size: 21px;
  font-weight: 800;
}

.agent-empty p {
  max-width: 360px;
  margin: 0 0 24px;
  color: #666;
  font-size: 14px;
  line-height: 1.7;
}

.agent-empty button {
  width: 100%;
  border: 0;
  border-top: 1px solid #ddd;
  background: transparent;
  padding: 13px 0;
  color: #222;
  text-align: left;
  font: inherit;
  font-size: 13px;
}

.agent-empty button:last-child {
  border-bottom: 1px solid #ddd;
}

.agent-turn + .agent-turn {
  margin-top: 38px;
  padding-top: 30px;
  border-top: 1px solid #ddd;
}

.agent-user-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
}

.agent-user-row p {
  margin: 0;
  border-radius: 18px;
  background: #f1f1f1;
  padding: 11px 15px;
  font-size: 14px;
  line-height: 1.5;
}

.agent-user-row time {
  color: #999;
  font-size: 11px;
}

.agent-steps {
  margin: 27px 0 24px;
  padding: 0;
  list-style: none;
}

.agent-steps li {
  position: relative;
  display: grid;
  grid-template-columns: 28px 1fr;
  align-items: center;
  gap: 9px;
  min-height: 48px;
  color: #a1a1a1;
  font-size: 14px;
}

.agent-steps li:not(:last-child)::after {
  position: absolute;
  top: 36px;
  bottom: -12px;
  left: 13px;
  border-left: 1px dashed #bbb;
  content: '';
}

.agent-steps li[data-state='active'],
.agent-steps li[data-state='complete'] {
  color: #111;
}

.agent-step-marker {
  display: flex;
  width: 24px;
  height: 24px;
  align-items: center;
  justify-content: center;
  border: 1px solid #c9c9c9;
  border-radius: 50%;
  background: #fff;
}

.agent-steps li[data-state='complete'] .agent-step-marker {
  border-color: #111;
  background: #111;
  color: #fff;
}

.agent-step-marker svg {
  width: 15px;
  height: 15px;
  stroke-width: 2.5;
}

.agent-spinner {
  width: 16px;
  height: 16px;
  border: 2px dotted #111;
  border-radius: 50%;
  animation: agent-spin 1s linear infinite;
}

.agent-execution {
  margin: -7px 0 24px 37px;
  border: 1px solid #dedede;
  border-radius: 7px;
  background: #fafafa;
}

.agent-execution-toggle {
  display: grid;
  width: 100%;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  border: 0;
  background: transparent;
  padding: 10px 12px;
  color: #222;
  text-align: left;
  font: inherit;
}

.agent-execution-symbol {
  font-size: 11px;
  font-weight: 800;
}

.agent-execution-title {
  display: flex;
  min-width: 0;
  align-items: baseline;
  gap: 9px;
}

.agent-execution-title strong {
  flex: 0 0 auto;
  font-size: 12px;
}

.agent-execution-title small {
  overflow: hidden;
  color: #777;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-execution-toggle > svg {
  width: 16px;
  height: 16px;
  transition: transform 160ms ease;
}

.agent-execution-toggle > svg[data-open='true'] {
  transform: rotate(180deg);
}

.agent-execution-list {
  border-top: 1px solid #dedede;
  padding: 5px 12px 10px;
}

.agent-execution-item {
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  gap: 8px;
  padding: 9px 0;
}

.agent-execution-item + .agent-execution-item {
  border-top: 1px dashed #ddd;
}

.agent-execution-marker {
  display: flex;
  width: 18px;
  height: 18px;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
  border: 1px solid #bbb;
  border-radius: 50%;
  color: #555;
  font-size: 11px;
}

.agent-execution-marker svg {
  width: 12px;
  height: 12px;
  stroke-width: 2.5;
}

.agent-execution-marker .agent-spinner {
  width: 11px;
  height: 11px;
  border-width: 1.5px;
}

.agent-execution-item > div {
  min-width: 0;
}

.agent-execution-item strong {
  display: block;
  font-size: 12px;
  line-height: 1.5;
}

.agent-execution-item p {
  margin: 4px 0 0;
  color: #555;
  font-family: inherit;
  font-size: 11px;
  line-height: 1.55;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}

.agent-execution-item small {
  display: block;
  margin-top: 4px;
  color: #777;
  font-size: 10px;
}

.agent-execution-item[data-status='failed'] .agent-execution-marker {
  border-color: #b42318;
  color: #b42318;
}

.agent-answer {
  position: relative;
  margin-top: 24px;
  padding: 0 4px;
}

.agent-answer-markdown {
  overflow-wrap: anywhere;
  font-size: 15px;
  line-height: 1.88;
}

.agent-answer-markdown :deep(p) {
  margin: 0 0 14px;
}

.agent-answer-markdown :deep(p:last-child) {
  margin-bottom: 0;
}

.agent-answer-markdown :deep(h1),
.agent-answer-markdown :deep(h2),
.agent-answer-markdown :deep(h3) {
  margin: 24px 0 9px;
  font-weight: 800;
  line-height: 1.4;
}

.agent-answer-markdown :deep(h1) {
  font-size: 19px;
}

.agent-answer-markdown :deep(h2) {
  font-size: 17px;
}

.agent-answer-markdown :deep(h3) {
  font-size: 15px;
}

.agent-answer-markdown :deep(ul),
.agent-answer-markdown :deep(ol) {
  margin: 10px 0 16px;
  padding-left: 22px;
}

.agent-answer-markdown :deep(li) {
  margin: 5px 0;
}

.agent-answer-markdown :deep(blockquote) {
  margin: 14px 0;
  border-left: 2px solid #111;
  padding-left: 12px;
  color: #444;
}

.agent-answer-markdown :deep(a) {
  color: inherit;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.agent-answer-markdown :deep(table) {
  display: block;
  width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
  font-size: 12px;
}

.agent-answer-markdown :deep(th),
.agent-answer-markdown :deep(td) {
  border-bottom: 1px solid #d8d8d8;
  padding: 7px 8px;
  text-align: left;
}

.agent-answer-markdown :deep(hr) {
  margin: 22px 0;
  border: 0;
  border-top: 1px solid #ddd;
}

.agent-cursor {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  margin-left: 3px;
  background: currentColor;
  vertical-align: -2px;
  animation: agent-blink 850ms steps(1) infinite;
}

.agent-feedback {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

.agent-feedback button {
  display: inline-flex;
  width: 30px;
  height: 30px;
  align-items: center;
  justify-content: center;
  border: 1px solid #d1d1d1;
  border-radius: 6px;
  background: #fff;
  color: #777;
  cursor: pointer;
}

.agent-feedback button[aria-pressed='true'] {
  border-color: #111;
  background: #111;
  color: #fff;
}

.agent-feedback svg {
  width: 15px;
  height: 15px;
}

.agent-live-status {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 18px;
  color: #555;
  font-size: 12px;
}

.agent-live-status .agent-spinner {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
}

.agent-citations {
  margin-top: 35px;
}

.agent-citation-heading {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 9px;
}

.agent-citation-heading strong {
  flex: 0 0 auto;
  font-size: 14px;
}

.agent-citation-heading span {
  height: 1px;
  flex: 1;
  background: #ddd;
}

.agent-citation {
  display: grid;
  grid-template-columns: 98px minmax(0, 1fr);
  gap: 12px;
  border-bottom: 1px solid #ddd;
  padding: 12px 0;
  color: inherit;
  text-decoration: none;
}

.agent-citation strong,
.agent-citation span {
  font-size: 12px;
  line-height: 1.5;
}

.agent-citation span {
  color: #444;
}

.agent-error {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  margin-top: 22px;
  border-left: 2px solid #b42318;
  padding: 2px 0 2px 13px;
  color: #7a201a;
  font-size: 12px;
}

.agent-error button {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 6px;
  border: 1px solid currentColor;
  background: transparent;
  padding: 6px 9px;
  color: inherit;
  font: inherit;
}

.agent-error button svg {
  width: 15px;
  height: 15px;
}

.agent-stopped {
  margin-top: 18px;
  color: #666;
  font-size: 12px;
}

.agent-warning {
  margin-top: 16px;
  border-left: 2px solid #b45309;
  padding: 2px 0 2px 13px;
  color: #92400e;
  font-size: 12px;
}

.agent-composer-wrap {
  position: relative;
  border-top: 1px solid #ddd;
  background: #fff;
  padding: 16px 20px 20px;
}

.agent-composer {
  border: 1px solid #191919;
  border-radius: 8px;
  background: #fff;
  padding: 10px;
  box-shadow: 0 2px 10px rgb(0 0 0 / 4%);
}

.agent-composer textarea {
  display: block;
  width: 100%;
  min-height: 46px;
  max-height: 132px;
  resize: none;
  border: 0;
  outline: 0;
  background: transparent;
  color: #111;
  padding: 2px 3px 8px;
  font: 14px/1.55 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.agent-composer textarea::placeholder {
  color: #aaa;
}

.agent-composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.agent-source-button {
  display: inline-flex;
  min-width: 0;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: #444;
  padding: 7px 4px;
  font: 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.agent-source-button svg {
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
}

.agent-source-button svg:last-child {
  width: 13px;
  height: 13px;
}

.agent-primary-action {
  display: inline-flex;
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border: 1px solid #050505;
  border-radius: 50%;
  background: #050505;
  color: #fff;
}

.agent-primary-action:disabled {
  border-color: #d1d1d1;
  background: #e6e6e6;
  color: #999;
}

.agent-primary-action svg {
  width: 19px;
  height: 19px;
}

.agent-stop {
  width: auto;
  border-radius: 6px;
  padding: 0 13px;
  gap: 6px;
  background: #fff;
  color: #111;
  font: 13px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.agent-stop svg {
  width: 16px;
  height: 16px;
}

.agent-source-picker {
  position: absolute;
  right: 20px;
  bottom: calc(100% + 8px);
  left: 20px;
  border: 1px solid #bbb;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 16px 44px rgb(0 0 0 / 14%);
  padding: 14px;
}

.agent-source-picker header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.agent-source-picker header strong {
  font-size: 13px;
}

.agent-source-picker header button {
  border: 0;
  background: transparent;
  color: #555;
  font: 11px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  text-decoration: underline;
}

.agent-source-search {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  border: 1px solid #d1d1d1;
  border-radius: 6px;
  padding: 0 9px;
}

.agent-source-search svg {
  width: 15px;
  height: 15px;
  flex: 0 0 auto;
  color: #777;
}

.agent-source-search input {
  width: 100%;
  height: 34px;
  border: 0;
  outline: 0;
  background: transparent;
  color: inherit;
  font: 12px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.agent-source-search input::placeholder {
  color: #999;
}

.agent-source-list {
  display: grid;
  max-height: 220px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px 12px;
  overflow-y: auto;
}

.agent-source-list label {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 7px;
  padding: 4px 0;
  font-size: 11px;
}

.agent-source-list input {
  accent-color: #111;
}

.agent-source-list span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-source-empty {
  grid-column: 1 / -1;
  margin: 12px 0;
  color: #777;
  text-align: center;
  font-size: 11px;
}

.agent-source-error {
  margin: 0;
  color: #9b2c24;
  font-size: 12px;
}

.agent-panel-enter-active,
.agent-panel-leave-active {
  transition: transform 220ms ease;
}

.agent-panel-enter-from,
.agent-panel-leave-to {
  transform: translateX(100%);
}

:global(.dark) .agent-panel,
:global(.dark) .agent-composer-wrap,
:global(.dark) .agent-composer,
:global(.dark) .agent-source-picker {
  border-color: #4b5563;
  background: #111827;
  color: #f3f4f6;
}

:global(.dark) .agent-source-search {
  border-color: #4b5563;
}

:global(.dark) .agent-context,
:global(.dark) .agent-user-row p {
  border-color: #4b5563;
  background: #1f2937;
}

:global(.dark) .agent-composer textarea,
:global(.dark) .agent-source-button,
:global(.dark) .agent-citation span {
  color: #e5e7eb;
}

:global(.dark) .agent-step-marker {
  border-color: #6b7280;
  background: #111827;
}

:global(.dark) .agent-steps li[data-state='complete'] .agent-step-marker {
  border-color: #f9fafb;
  background: #f9fafb;
  color: #111827;
}

:global(.dark) .agent-citation,
:global(.dark) .agent-citation-heading span,
:global(.dark) .agent-composer-wrap,
:global(.dark) .agent-empty button {
  border-color: #4b5563;
}

:global(.dark) .agent-context-remove {
  color: #9ca3af;
}

:global(.dark) .agent-feedback button {
  border-color: #4b5563;
  background: #1f2937;
  color: #9ca3af;
}

:global(.dark) .agent-feedback button[aria-pressed='true'] {
  border-color: #f9fafb;
  background: #f9fafb;
  color: #111827;
}

@keyframes agent-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes agent-blink {
  50% {
    opacity: 0;
  }
}

@media (max-width: 760px) {
  .agent-launcher {
    right: 16px;
    bottom: 18px;
    width: 54px;
    height: 54px;
    justify-content: center;
    padding: 0;
  }

  .agent-launcher span {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
  }

  .agent-panel {
    inset: 0;
    width: 100%;
    min-width: 0;
    border: 0;
    border-radius: 0;
    box-shadow: none;
  }

  .agent-header {
    min-height: 74px;
    padding: 0 18px;
  }

  .agent-header h2 {
    flex: 1;
    text-align: center;
  }

  .agent-mobile-back {
    display: inline-flex !important;
  }

  .agent-new-conversation {
    margin-left: 0;
  }

  .agent-new-conversation svg,
  .agent-close {
    display: none !important;
  }

  .agent-context {
    margin: 4px 20px 0;
  }

  .agent-conversation {
    padding: 20px 22px 30px;
  }

  .agent-user-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .agent-user-row time {
    display: none;
  }

  .agent-answer-markdown {
    font-size: 16px;
    line-height: 1.9;
  }

  .agent-composer-wrap {
    padding: 12px 14px max(14px, env(safe-area-inset-bottom));
  }

  .agent-source-picker {
    right: 14px;
    left: 14px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .agent-launcher,
  .agent-panel-enter-active,
  .agent-panel-leave-active {
    transition: none;
  }

  .agent-spinner,
  .agent-cursor {
    animation: none;
  }
}
</style>
