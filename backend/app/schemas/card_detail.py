from pydantic import BaseModel


class CardDetailSchema(BaseModel):
    id: str
    project_id: str
    title: str
    summary: str
    owner: str
    priority: str
    raw_requirement: str
    current_stage: str
    acceptance_substate: str | None = None
    plan_path: str | None = None
    issues_path: str | None = None
    active_process_type: str
    active_process_status: str
    active_process_session_id: str | None = None
