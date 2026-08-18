import DOMPurify from 'dompurify'
import MarkdownIt from 'markdown-it'

const SAFE_HTTP_URL = /^https?:\/\//i

export const safeExternalUrl = (value?: string | null): string | null => {
  if (typeof value !== 'string' || !SAFE_HTTP_URL.test(value.trim())) return null

  try {
    const url = new URL(value.trim())
    if (!['http:', 'https:'].includes(url.protocol)) return null
    if (url.username || url.password) return null
    return url.href
  } catch {
    return null
  }
}

const markdown = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: false,
})

markdown.disable(['link', 'autolink'])

export const renderSafeMarkdown = (answer: string): string =>
  DOMPurify.sanitize(markdown.render(answer), {
    ALLOWED_TAGS: [
      'blockquote',
      'br',
      'code',
      'del',
      'em',
      'h1',
      'h2',
      'h3',
      'hr',
      'li',
      'ol',
      'p',
      'pre',
      'strong',
      'table',
      'tbody',
      'td',
      'th',
      'thead',
      'tr',
      'ul',
    ],
    ALLOWED_ATTR: [],
    ALLOW_DATA_ATTR: false,
  })
