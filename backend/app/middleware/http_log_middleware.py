from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from common.core.logger import logger
from common.core.request_context import clear_request_context, set_request_context

TRACE_ID_HEADER = "X-Trace-Id"
REQUEST_ID_HEADER = "X-Request-Id"


# HTTP 日志中间件负责生成/透传链路标识，并记录请求开始与结束信息。
class HttpLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get(TRACE_ID_HEADER) or uuid.uuid4().hex
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        client_ip = request.client.host if request.client else "unknown"
        query_string = request.url.query or ""

        set_request_context(
            trace_id=trace_id,
            request_id=request_id,
            transport="http",
        )
        request.state.trace_id = trace_id
        request.state.request_id = request_id

        start = time.perf_counter()
        logger.info(
            "HTTP 请求开始 method={} path={} query={} client_ip={}",
            request.method,
            request.url.path,
            query_string,
            client_ip,
        )

        try:
            response = await call_next(request)
        except Exception:
            raise
        else:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            response.headers[TRACE_ID_HEADER] = trace_id
            response.headers[REQUEST_ID_HEADER] = request_id
            logger.info(
                "HTTP 请求完成 method={} path={} status_code={} duration_ms={}",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
            return response
        finally:
            clear_request_context()
