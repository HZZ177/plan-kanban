from pydantic import BaseModel


class AcceptanceSubstateSchema(BaseModel):
    acceptance_substate: str | None = None
