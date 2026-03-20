from pydantic import BaseModel


class ProcessStateSchema(BaseModel):
    active_process_type: str
    active_process_status: str
    active_process_session_id: str | None = None
