from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator

from hotrank.agent.tool_registry import (
    SUPPORTED_DETAIL_PLATFORMS,
    SUPPORTED_SEARCH_PLATFORMS,
)


class StrictToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class GetTodayNewsArguments(StrictToolArguments):
    limit: int = Field(ge=1, le=50)


class GetTopicDetailArguments(StrictToolArguments):
    topic_id: int = Field(gt=0)
    platform: str

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, value: str) -> str:
        if value not in SUPPORTED_DETAIL_PLATFORMS:
            raise ValueError("unsupported detail platform")
        return value


class GetRankDataArguments(StrictToolArguments):
    content: str = Field(min_length=1, max_length=500)
    platform: list[str] = Field(
        min_length=1,
        max_length=len(SUPPORTED_SEARCH_PLATFORMS),
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
    def validate_platforms(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("platform entries must be unique")
        if any(item not in SUPPORTED_SEARCH_PLATFORMS for item in value):
            raise ValueError("unsupported search platform")
        return value


ToolArguments: TypeAlias = (
    GetTodayNewsArguments
    | GetTopicDetailArguments
    | GetRankDataArguments
)

TOOL_ARGUMENT_MODELS: dict[str, type[StrictToolArguments]] = {
    "get_today_news": GetTodayNewsArguments,
    "get_topic_detail": GetTopicDetailArguments,
    "get_rank_data": GetRankDataArguments,
}
