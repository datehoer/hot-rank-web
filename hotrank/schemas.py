from typing import Any, List, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

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
    role: Literal["user"]
    content: str = Field(min_length=1, max_length=4_000)
    platform: list[str] = Field(
        min_length=1,
        max_length=100,
        description="平台列表",
    )
    timestamp: int = Field(..., description="时间戳")
    session_id: str = Field(
        min_length=1,
        max_length=128,
        description="会话 ID",
    )

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("content must not be blank")
        return normalized

    @field_validator("platform")
    @classmethod
    def validate_unique_platforms(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("platform entries must be unique")
        return value

class ToolError(BaseModel):
    code: str | int = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    retryable: bool = Field(..., description="是否可重试")

class ToolMeta(BaseModel):
    tool_call_id: str = Field(..., description="工具名称")
    duration_ms: int = Field(..., description="工具调用耗时，单位毫秒")
    cached: bool = Field(..., description="是否使用缓存")


class ToolResult(BaseModel):
    ok: bool
    message: str | None = Field(None, description="工具调用的消息")
    data: list[dict[str, Any]] | None = Field(
        None,
        description="工具返回的数据",
    )
    source: list[str] | None = Field(
        None,
        description="工具返回的数据来源",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="工具返回的警告信息",
    )
    error: ToolError | None = Field(None, description="工具返回的错误信息")
    meta: ToolMeta | None = Field(None, description="工具调用的元信息")
