"""LogTide SDK - Official Python SDK for LogTide."""

from logtide_sdk.client import LogTideClient, serialize_exception
from logtide_sdk.enums import CircuitState, LogLevel
from logtide_sdk.exceptions import BufferFullError, CircuitBreakerOpenError, LogTideError
from logtide_sdk.handler import LogTideHandler
from logtide_sdk.models import (
    AggregatedStatsOptions,
    AggregatedStatsResponse,
    ClientMetrics,
    ClientOptions,
    LogEntry,
    LogsResponse,
    PayloadLimitsOptions,
    QueryOptions,
)

_has_async = False
try:
    from logtide_sdk.async_client import AsyncLogTideClient

    _has_async = True  # type: ignore[assignment]
except ImportError:
    pass

__version__ = "0.8.5"

__all__ = [
    "AggregatedStatsOptions",
    "AggregatedStatsResponse",
    "BufferFullError",
    "CircuitBreakerOpenError",
    "CircuitState",
    "ClientMetrics",
    "ClientOptions",
    "LogEntry",
    "LogLevel",
    "LogTideClient",
    "LogTideError",
    "LogTideHandler",
    "LogsResponse",
    "PayloadLimitsOptions",
    "QueryOptions",
    "serialize_exception",
]

if _has_async:
    __all__.append("AsyncLogTideClient")
