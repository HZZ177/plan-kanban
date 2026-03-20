from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from common.core.exceptions import ConflictError, NotFoundError, ValidationError
from common.core.logger import logger


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ValidationError as exc:
            return JSONResponse(status_code=400, content={"detail": str(exc)})
        except NotFoundError as exc:
            return JSONResponse(status_code=404, content={"detail": str(exc)})
        except ConflictError as exc:
            return JSONResponse(status_code=409, content={"detail": str(exc)})
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unhandled application error: %s", exc)
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
