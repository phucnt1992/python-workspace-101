from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class HtmxSpanMiddleware(BaseHTTPMiddleware):
    """Enriches the current OTel span with HTMX request headers when present.

    HTMX sends HX-* headers on partial page requests. This middleware promotes
    those headers to span attributes so traces clearly distinguish HTMX-driven
    requests from full-page navigations.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.headers.get("hx-request") == "true":
            span = trace.get_current_span()
            span.set_attribute("htmx.request", True)
            if target := request.headers.get("hx-target"):
                span.set_attribute("htmx.target", target)
            if trigger := request.headers.get("hx-trigger"):
                span.set_attribute("htmx.trigger", trigger)
            if trigger_name := request.headers.get("hx-trigger-name"):
                span.set_attribute("htmx.trigger_name", trigger_name)
            if request.headers.get("hx-boosted") == "true":
                span.set_attribute("htmx.boosted", True)
            if current_url := request.headers.get("hx-current-url"):
                span.set_attribute("htmx.current_url", current_url)

        return await call_next(request)
