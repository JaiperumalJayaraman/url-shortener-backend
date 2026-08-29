from datetime import datetime
from pydantic import AnyHttpUrl, BaseModel, Field, field_validator

class URLCreate(BaseModel):
    original_url: AnyHttpUrl
    custom_alias: str | None = Field(default=None, min_length=3, max_length=32)
    expires_at: datetime | None = None

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value):
        if value is not None and not value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Alias may contain only letters, numbers, hyphens and underscores")
        return value

class URLResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None
    click_count: int

class HealthResponse(BaseModel):
    status: str
