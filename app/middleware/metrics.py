"""Prometheus metrics middleware: request count and duration."""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.scope.get("path", "")
        method = request.method
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        status = response.status_code
        REQUEST_COUNT.labels(method=method, path=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
        return response
