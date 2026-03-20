from pydantic import BaseModel, Field


class CardUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, max_length=2000)
    owner: str | None = Field(default=None, max_length=255)
    priority: str | None = Field(default=None, min_length=2, max_length=16)
    raw_requirement: str | None = Field(default=None, min_length=1)
    current_stage: str | None = None
    acceptance_substate: str | None = None
