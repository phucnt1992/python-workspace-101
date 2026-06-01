from fastapi import Request
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

_HTMX_HEADERS = [
    "hx-request",
    "hx-target",
    "hx-trigger",
    "hx-trigger-name",
    "hx-boosted",
    "hx-current-url",
]

class HtmxSpanMiddleware(BaseHTTPMiddleware):
    """HTMX sends HX-* headers on partial page requests. This middleware promotes those headers
    to span attributes so traces clearly distinguish HTMX-driven requests from full-page navigations."""

    async def dispatch(self, request: Request, call_next):
        span = trace.get_current_span()
        if span.is_recording():
            for header in _HTMX_HEADERS:
                value = request.headers.get(header)
                if value:
                    span.set_attribute(f"htmx.{header.replace('-', '_')}", value)
        return await call_next(request)
