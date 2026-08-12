# HotDay Agent 文档索引

本目录包含热点 Agent P0 从产品评审到开发、测试和灰度所需的配套文档。

## 阅读顺序

1. [Agent 功能 PRD](../agent-feature-prd.md)
   - 产品目标、P0/P1 范围、非目标和验收标准。
2. [技术设计](technical-design.md)
   - 模块、会话、编排器、模型网关、引用、安全抓取、部署。
3. [OpenAPI](openapi.yaml)
   - HTTP 路由、请求响应和数据 Schema。
4. [SSE 协议](sse-protocol.md)
   - 流式事件、前后端状态机、取消、恢复和错误。
5. [Prompt 与工具协议](prompts-and-tools.md)
   - System Prompt、四个只读工具、结果与引用格式。
6. [安全威胁模型](threat-model.md)
   - SSRF、Prompt Injection、会话隔离、XSS、费用和上线阻断项。
7. [Docker Compose 测试方案](docker-compose-test-plan.md)
   - 假模型、假来源、fixture、测试矩阵、CI 与远端验收。
8. [pgvector 安装与初始化](pgvector-setup.md)
   - Python 版本兼容、PostgreSQL extension 安装、migration 与验证。
9. [前端交互与埋点](frontend-ux-and-analytics.md)
   - 桌面/移动交互、组件、状态、可访问性和隐私友好埋点。
10. [Agent UI 视觉参考](ui-visual-reference.md)
   - 悬浮入口、右侧抽屉、运行状态、流式回答和移动端的参考图与验收基线。

## 文档状态

| 文档 | 状态 | 开发前是否必须评审 |
| --- | --- | --- |
| PRD | Draft | 是 |
| 技术设计 | Draft | 是 |
| OpenAPI | Draft | 是 |
| SSE 协议 | Draft | 是 |
| Prompt 与工具协议 | Draft | 是 |
| 安全威胁模型 | Draft | 是，安全阻断项必须确认 |
| Docker Compose 测试方案 | Draft | 是 |
| 前端交互与埋点 | Draft | 是 |
| Agent UI 视觉参考 | Draft | 是 |

## P0 默认决策

- 单 Agent、固定四个只读工具；
- 不提供任意互联网搜索或任意 URL 工具；
- 不提供订阅、邮件、发布、Shell、Docker、SSH 等写操作；
- 匿名会话 TTL 24 小时；
- 同会话并发 1；
- 单轮最多 4 次工具调用、5 个正文来源；
- 消息使用 POST + SSE，前端使用 fetch stream；
- 会话 token 只通过 header 传递，服务端只保存哈希；
- 来源 URL 只能通过服务端 topic/source ID 映射获得；
- Agent 默认通过功能开关关闭，测试完成后灰度；
- 自动化测试使用 fake model 和 fake source，不使用真实密钥。

## 契约优先级

如文档出现不一致：

1. 产品范围和是否进入 P0，以 PRD 为准；
2. HTTP 字段，以 `openapi.yaml` 为准；
3. 流事件顺序，以 `sse-protocol.md` 为准；
4. 工具名称、参数和结果，以 `prompts-and-tools.md` 为准；
5. 安全限制，以 `threat-model.md` 中更严格的要求为准；
6. 实现细节，以评审通过后的技术设计版本为准。

发现不一致时应同步修改所有相关文档，不在代码中静默选择一种解释。

## 开发前需要确认

- [ ] 默认模型 provider、model 和每日费用上限；
- [ ] 生产 Nginx SSE 配置；
- [ ] 生产 CORS 允许域名；
- [ ] 功能开关管理方式；
- [ ] 日志、指标和 analytics 的实际接入；
- [ ] Markdown sanitizer 选型；
- [ ] 生产 Uvicorn worker 数；
- [ ] 前端入口位置和移动端形态；
- [ ] 匿名会话 token 使用 sessionStorage；
- [ ] 安全威胁模型中的全部 High/Critical 控制有负责人。

## 变更规则

- Prompt、工具 Schema、SSE 或 API 的破坏性修改必须提升对应版本；
- 新增写工具必须新建安全评审，不能直接加入 P0 注册表；
- 不在文档示例中放生产 IP、密码、API Key 或真实用户数据；
- 每次开发合并前检查代码、测试和文档是否同步；
- 上线后记录最终生效配置，但只记录配置名和非敏感值。
