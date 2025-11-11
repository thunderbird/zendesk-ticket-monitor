"""Configuration schema."""

import os
import yaml
from pydantic import BaseModel, Field


class ZendeskConfig(BaseModel):
    subdomain: str
    email: str
    api_token: str = ""


class QueryConfig(BaseModel):
    bucket_minutes: int = Field(default=5, ge=1, le=60)
    brands: list = Field(default_factory=list)


class DetectionConfig(BaseModel):
    mode: str = "threshold"
    multiplier: float = 2.0
    min_delta: int = 10


class Config(BaseModel):
    zendesk: ZendeskConfig
    query: QueryConfig
    detection: DetectionConfig

    @classmethod
    def from_yaml(cls, path: str):
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
