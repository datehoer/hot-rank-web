from typing import List

from pydantic import BaseModel, EmailStr, Field


class HotTopic(BaseModel):
    hot_label: str = Field(..., description="热点标题 / 标签")
    hot_url: str = Field(..., description="热点链接，http/https 开头")
    hot_value: str = Field(..., description="热度值 / 指数，没有设为0")

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
    hot_url: str = Field(..., description="热点链接，使用 str 避免 format:'uri'")
    hot_value: str = Field(..., description="热度值 / 指数，没有设为0")
    hot_content: str = Field(..., description="≤100 字的内容摘要，不带年份")
    hot_tag: str = Field(..., description="4 字类型标签")

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
