import logging
import os

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pythonjsonlogger.json import JsonFormatter

logger = logging.getLogger(__name__)

_telemetry_configured = False
_logging_configured = False

# Fields included in every JSON log line.
_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

# Extra OTEL fields injected by LoggingInstrumentor into LogRecord.
_OTEL_FIELDS = ["otelTraceID", "otelSpanID", "otelServiceName", "otelTraceSampled"]


class _OtelJsonFormatter(JsonFormatter):
    """JSON formatter that promotes OTEL trace-context fields when present."""

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        super().add_fields(log_record, record, message_dict)
        for field in _OTEL_FIELDS:
            value = getattr(record, field, None)
            if value:
                log_record[field] = value


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with JSON structured output.

    Call this once at application startup, before setup_telemetry().
    Idempotent: safe to call multiple times.
    """
    global _logging_configured
    if _logging_configured:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(_OtelJsonFormatter(_LOG_FORMAT, rename_fields={"asctime": "timestamp", "levelname": "level"}))

    root = logging.getLogger()
    root.setLevel(level)
    # Replace any existing handlers to avoid duplicate output.
    root.handlers = [handler]

    _logging_configured = True


def setup_telemetry(service_name: str) -> None:
    """Configure OpenTelemetry SDK with OTLP/gRPC exporters.

    No-op if OTEL_EXPORTER_OTLP_ENDPOINT is not set, so local dev works without Aspire.
    Idempotent: safe to call multiple times (e.g. in tests).
    """
    global _telemetry_configured

    if _telemetry_configured:
        return

    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        logger.debug("OTEL_EXPORTER_OTLP_ENDPOINT not set — OpenTelemetry instrumentation disabled.")
        return

    resource = Resource.create({SERVICE_NAME: service_name})

    # --- Traces ---
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # --- Metrics ---
    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # --- Logs ---
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    set_logger_provider(logger_provider)
    # set_logging_format=False — we own the formatter via setup_logging().
    LoggingInstrumentor().instrument(set_logging_format=False)

    _telemetry_configured = True
    logger.info("OpenTelemetry configured", extra={"service_name": service_name, "otlp_endpoint": endpoint})


def get_tracer(name: str) -> trace.Tracer:
    """Return a tracer for manual span creation."""
    return trace.get_tracer(name)
