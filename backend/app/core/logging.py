import json
import logging
import time
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


_correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")


def set_correlation_id(correlation_id: str) -> None:
    _correlation_id_ctx.set(correlation_id)


def get_correlation_id() -> str:
    return _correlation_id_ctx.get()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Response:
        correlation_id = request.headers.get("x-correlation-id") or str(uuid4())
        token = _correlation_id_ctx.set(correlation_id)
        start = time.perf_counter()

        try:
            response = await call_next(request)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            response.headers["x-correlation-id"] = correlation_id
            logging.getLogger("app.request").info(
                "%s %s %s",
                request.method,
                request.url.path,
                elapsed_ms,
            )
            return response
        finally:
            _correlation_id_ctx.reset(token)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())
    root_logger.handlers = [handler]

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers = [handler]
        logger.propagate = False
        logger.setLevel(level.upper())
