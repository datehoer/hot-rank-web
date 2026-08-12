from typing import List, Optional
from dns import message
from pydantic import BaseModel, EmailStr, Field

class HotTopic(BaseModel):
    hot_label: str = Field(..., description="热点标题 / 标签")
    hot_url: str = Field(..., description="热点链接，http/https 开头")
    hot_value: str = Field(..., description="热度值 / 指数，没有设为0")
    hot_source: str = Field(..., description="来源网站")

    class Config:
        extra = "forbid"
        title = "HotTopic"

class HotTopics(BaseModel):
    hot_topics: List[HotTopic] = Field(..., description="热点列表")

    class Config:
        extra = "forbid"
        title = "HotTopics"
class HotTopicDetail(BaseModel):
    hot_label: str = Field(..., description="热点标题")
    hot_url: str = Field(..., description="热点链接, 使用 str 避免 format:'uri'")
    hot_value: str = Field(..., description="热度值 / 指数, 没有设为0")
    hot_content: str = Field(..., description="≤100 字的内容摘要, 不带年份")
    hot_tag: str = Field(..., description="4 字类型标签")
    hot_summary: str = Field(..., description="热点摘要, 最多 100 字")

    class Config:
        extra = "forbid"
        title = "hot_topic_detail"

class Feedback(BaseModel):
    subject: str
    content: str
    username: str

class SubscriberRequest(BaseModel):
    email: EmailStr

class UnsubscribeRequest(BaseModel):
    email: EmailStr
    uuid: str

class AgentMessage(BaseModel):
    role: str
    content: str
    platform: list[str] = Field(..., description="平台列表")
    timestamp: int = Field(..., description="时间戳")
    session_id: str = Field(..., description="会话 ID")

class ToolError(BaseModel):
    code: int = Field(None, description="错误码")
    message: str = Field(None, description="错误信息")
    retryable: bool = Field(None, description="是否可重试")

class ToolMeta(BaseModel):
    tool_call_id: str = Field(None, description="工具名称")
    duration_ms: int = Field(None, description="工具调用耗时，单位毫秒")
    cached: bool = Field(None, description="是否使用缓存")


class ToolResult(BaseModel):
    ok: bool
    message: str = Field(None, description="工具调用的消息")
    data: list = Field(None, description="工具返回的数据")
    source: list[str] = Field(None, description="工具返回的数据来源")
    warnings: list[str] = Field([], description="工具返回的警告信息")
    error: ToolError = Field(None, description="工具返回的错误信息")
    meta: ToolMeta = Field(None, description="工具调用的元信息")
