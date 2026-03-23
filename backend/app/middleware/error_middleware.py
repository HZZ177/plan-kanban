from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from common.core.exceptions import ConflictError, NotFoundError, ValidationError
from common.core.logger import logger
from common.core.request_context import get_request_id, get_trace_id

TRACE_ID_HEADER = "X-Trace-Id"
REQUEST_ID_HEADER = "X-Request-Id"


# 错误中间件负责统一异常日志与错误响应格式，并回写请求链路标识。
def _build_error_response(status_code: int, detail: str) -> JSONResponse:
    response = JSONResponse(status_code=status_code, content={"detail": detail})
    trace_id = get_trace_id()
    request_id = get_request_id()
    if trace_id:
        response.headers[TRACE_ID_HEADER] = trace_id
    if request_id:
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ValidationError as exc:
            logger.warning(
                "请求校验失败 method={} path={} detail={}",
                request.method,
                request.url.path,
                str(exc),
            )
            return _build_error_response(status_code=400, detail=str(exc))
        except NotFoundError as exc:
            logger.warning(
                "资源不存在 method={} path={} detail={}",
                request.method,
                request.url.path,
                str(exc),
            )
            return _build_error_response(status_code=404, detail=str(exc))
        except ConflictError as exc:
            logger.warning(
                "资源冲突 method={} path={} detail={}",
                request.method,
                request.url.path,
                str(exc),
            )
            return _build_error_response(status_code=409, detail=str(exc))
        except Exception:
            logger.exception(
                "应用出现未处理异常 method={} path={}",
                request.method,
                request.url.path,
            )
            return _build_error_response(status_code=500, detail="Internal Server Error")

