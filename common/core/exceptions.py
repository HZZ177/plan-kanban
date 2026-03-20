class PlanKanbanError(Exception):
    """项目基础异常。"""


class ValidationError(PlanKanbanError):
    """输入或状态校验异常。"""


class NotFoundError(PlanKanbanError):
    """资源不存在异常。"""


class ConflictError(PlanKanbanError):
    """状态冲突异常。"""
