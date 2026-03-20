from pydantic import BaseModel, Field


class CardCreateSchema(BaseModel):
    project_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(default="", max_length=2000)
    owner: str = Field(default="", max_length=255)
    priority: str = Field(default="P1", min_length=2, max_length=16)
    raw_requirement: str = Field(min_length=1)
