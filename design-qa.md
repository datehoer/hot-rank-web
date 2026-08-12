# Agent UI Design QA

- Source visual truth: `docs/agent/assets/agent-combined-02-searching.png`
- Implementation screenshot: `docs/agent/assets/implementation-desktop-searching.png`
- Reference pixels: 1487 × 1058
- Implementation pixels: 1472 × 1047 (the in-app browser reserves 15 × 11 px for its viewport chrome; comparison used equal-height proportional scaling)
- CSS viewport requested: 1487 × 1058, device scale factor 1
- State: desktop, contextual hotspot selected, Agent searching
- Comparison artifact: `/Users/datehoer/.codex/generated_images/019fdb86-f716-7cf1-8122-80d719b8f7d5/exec-c3ca4b39-5d8c-4d51-bf33-0a613710c5ae.png`

## Full-view comparison evidence

The reference and implementation were placed in one side-by-side comparison input. Both retain the existing monochrome HotDay ranking grid, a right-side panel separated by a single hairline, contextual topic header, user question, vertical run steps, and a persistent bottom composer.

## Focused-region comparison evidence

The right drawer and bottom composer were inspected at their rendered size because those are the fidelity-critical regions. No custom raster artwork exists in the reference; all icons use the project's existing Heroicons family. The implementation uses the same flat surfaces, restrained radius system, fine borders, and monospace type family as the existing product.

## Required fidelity surfaces

- Fonts and typography: passed. Existing HotDay monospace hierarchy is preserved; drawer heading, context title, status copy, answer and metadata use distinct weights and sizes. Markdown headings, tables, quotes and lists now render as UI rather than literal syntax.
- Spacing and layout rhythm: passed. Drawer occupies about one third of the desktop viewport, is full-height, and switches the visible ranking grid from three to two columns so content is not hidden beneath it. Mobile switches to a full-screen panel.
- Colors and tokens: passed. Black, white, neutral gray, hairline borders and the current dark-mode palette are preserved; no new decorative gradient or accent palette was introduced.
- Image quality and assets: passed. The target contains icons but no custom imagery. Icons are from `@heroicons/vue`; no placeholder, emoji, inline SVG, CSS drawing or raster substitute was used.
- Copy and content: passed. Controls use user-facing language: “问 AI”, “新对话”, “停止”, “重新尝试”, “查询来源”. Failures explain the problem and offer a next action instead of exposing only an internal code.

## Interaction and accessibility verification

- Open/close launcher: passed.
- Contextual “问 AI” from a ranking item: passed; title, source, rank and URL are carried into the drawer.
- Source selector: passed; API configuration loaded 75 sources and selected all by default.
- POST + SSE parsing: passed with the live local API.
- Visible planning/searching/generating states: passed.
- Stop control: passed; aborts the browser stream and calls the cancel endpoint.
- Completed response: passed; live model output completed and returned to the enabled composer.
- Desktop and 393 × 852 mobile layouts: passed.
- Keyboard labels/focus: passed for launcher, contextual query, close/back, input, send, stop and source controls.
- Browser console: no application error during the successful open, contextual-query and live-stream runs. A later ranking reload exceeded the existing Axios 60-second path while backend rank cache regeneration was busy; this is outside the new Agent UI and did not affect its endpoints.

## Comparison history

### Iteration 1

- P1: opening a fixed drawer covered the third ranking column instead of reflowing the content.
- P2: completed model Markdown was displayed as literal `**`, headings and table pipes.
- Fixes: emit drawer open state to the page, constrain the page to the remaining width, reduce the open desktop grid to two columns, and render model Markdown with the project's existing `markdown-it` dependency.

### Iteration 2

- Post-fix evidence: `docs/agent/assets/implementation-desktop-open.png`, successful production build, desktop/mobile browser checks, live SSE run and completed response.
- Remaining differences: the reference is a concept render with curated ranking data and extra source logos; the implementation intentionally uses live ranking data and only renders citation cards when the server emits citation events. These do not block the implemented interaction.

## Follow-up polish

- P3: add server-side `citation` emission so completed answers can always show structured source rows instead of relying only on links in model text.
- P3: add a backend `fetching` status around detail tools for finer-grained progress copy.

## Floating-window revision

- User-directed change: the desktop assistant must float above the page instead of occupying a dedicated right-side layout column.
- Visual target: `/Users/datehoer/.codex/generated_images/019fdb86-f716-7cf1-8122-80d719b8f7d5/exec-8136a625-690e-46ca-a8f9-03b119f3b373.png`.
- Implementation evidence: browser inspection measured a fixed 460px-wide panel with 24px top/right/bottom offsets and 10px radius. The original ranking grid remains unchanged behind the overlay.
- Responsive evidence: at 393 × 852 the assistant remains a full-screen surface with the mobile back action and fixed composer.
- Regression checks: production build and type check passed; desktop browser console contained no application warnings or errors.

final result: passed
