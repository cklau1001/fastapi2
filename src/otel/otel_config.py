import functools
import inspect
import logging
from contextlib import contextmanager
from opentelemetry import trace, baggage, context
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# must use http submodule
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter  # Optional for debugging

# MUST use the .http submodule
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from watchfiles import awatch

SERVICE_NAME = "fastapi2"
OTLP_COLLECTOR_ENDPOINT = "" # empty or http://localhost:4318

OTEL_RESOURCE = Resource.create(
    {
        "service.name": SERVICE_NAME,
        "service.version": "1.0.0",
        "deployment.environment": "dev"
    }
)

# global variable to hold the provider for shutdown
_LOGGER_PROVIDER = None

class StringifiedOTelHandler(LoggingHandler):
    def emit(self, record):
        # This force-calls the formatter (turning your dict into a string)
        # before the OTel SDK tries to encode the raw dictionary.
        record.msg = self.format(record)

        # Clear arguments to prevent OTel from trying to re-format
        # or process the original dictionary values.
        record.args = None

        super().emit(record)

def initialize_tracer():

    tracer_provider = TracerProvider(resource=OTEL_RESOURCE, sampler=ALWAYS_ON)

    # Configure the OTLP Exporter to send traces to the OpenTelemetry Collector
    otlp_exporter = OTLPSpanExporter(endpoint=OTLP_COLLECTOR_ENDPOINT)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Optional: Add a ConsoleSpanExporter for local debugging
    console_processor = BatchSpanProcessor(ConsoleSpanExporter())
    tracer_provider.add_span_processor(console_processor)

    # Set the global TracerProvider
    trace.set_tracer_provider(tracer_provider)

def initialize_logger():

    logger_provider = LoggerProvider(resource=OTEL_RESOURCE)

    log_exporter = OTLPLogExporter()
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    handler = StringifiedOTelHandler(logger_provider=logger_provider)
    logging.getLogger().setLevel(logging.NOTSET)
    # handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    return logger_provider

@contextmanager
def set_baggage_context(**kwargs):
    """Sets baggage and automatically handles attach/detach."""
    ctx = context.get_current()
    for key, value in kwargs.items():
        ctx = baggage.set_baggage(key, value, context=ctx)

    token = context.attach(ctx)
    try:
        yield
    finally:
        context.detach(token)

# Create a custom decorator to start a span and attach a context for baggage to work
def otelspan(span_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name):
                token = context.attach(context.get_current())
                try:
                    if inspect.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    return func(*args, **kwargs)
                finally:
                    context.detach(token)
        return wrapper
    return decorator

# Function to get the global OpenTelemetry Tracer
def get_tracer():
    return trace.get_tracer(SERVICE_NAME)


tracer = get_tracer()
fastapi_instrumentor = FastAPIInstrumentor()