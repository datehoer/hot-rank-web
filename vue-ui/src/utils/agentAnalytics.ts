// Privacy-preserving Umami event tracking for the hotspot agent.
//
// Rules (docs/agent/frontend-ux-and-analytics.md §16):
// - never send full user questions, answer text, session tokens, source
//   URLs/titles, or raw IPs;
// - only send bucketed lengths, counts, opaque refs and timings;
// - a tracking failure must never break the agent.

declare global {
  interface Window {
    umami?: {
      track?: (name: string, data?: Record<string, unknown>) => void
    }
  }
}

export const EVENT_VERSION = '1'

export function lengthBucket(length: number): string {
  if (length <= 20) return '1-20'
  if (length <= 100) return '21-100'
  if (length <= 500) return '101-500'
  if (length <= 1000) return '501-1000'
  return '1001-2000'
}

function viewportType(): 'desktop' | 'mobile' {
  return window.matchMedia('(max-width: 760px)').matches ? 'mobile' : 'desktop'
}

function commonProps(): Record<string, unknown> {
  return {
    event_version: EVENT_VERSION,
    locale: navigator.language || 'unknown',
    viewport_type: viewportType(),
  }
}

export function trackAgentEvent(
  name: string,
  data: Record<string, unknown> = {},
): void {
  const track = window.umami?.track
  if (typeof track !== 'function') return
  try {
    track(name, { ...commonProps(), ...data })
  } catch {
    // Tracking must never break the agent.
  }
}
