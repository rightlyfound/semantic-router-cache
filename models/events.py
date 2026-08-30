from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class PullRequestEvent(BaseModel):
    event_type: Literal["opened", "closed", "reopened", "synchronize"]
    pr_number: int
    title: str
    description: str | None = None
    author_login: str
    source_branch: str
    target_branch: str
    repo_full_name: str
    draft: bool
    created_at: datetime
    url: HttpUrl
    labels: list[str] = Field(default_factory=list)
    reviewers: list[str] = Field(default_factory=list)
