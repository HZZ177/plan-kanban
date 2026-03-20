from __future__ import annotations

from common.core.exceptions import ValidationError

ALLOWED_STAGE_TRANSITIONS: dict[str, set[str]] = {
    "raw": {"raw", "plan"},
    "plan": {"plan", "raw", "contract"},
    "contract": {"contract", "raw", "plan", "developing"},
    "developing": {"developing", "acceptance"},
    "acceptance": {"acceptance", "developing"},
}


def validate_stage_transition(current_stage: str, target_stage: str) -> None:
    allowed_targets = ALLOWED_STAGE_TRANSITIONS.get(current_stage)
    if allowed_targets is None:
        raise ValidationError(f"Unsupported current stage: {current_stage}")
    if target_stage not in allowed_targets:
        raise ValidationError(f"Invalid stage transition: {current_stage} -> {target_stage}")
