from __future__ import annotations

import functools
import inspect
import logging
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, NamedTuple

from colorama import Fore, Style

if TYPE_CHECKING:
    from collections.abc import Callable

    from apify_client._resource_clients._resource_client import ResourceClient

    _BaseClient = ResourceClient


logger_name = __name__.split('.')[0]
"""Name of the logger used throughout the library."""

logger = logging.getLogger(logger_name)
"""Logger used throughout the library."""


class LogContext(NamedTuple):
    """Request context details for logging (attempt, client method, HTTP method, resource ID, URL)."""

    attempt: ContextVar[int | None]
    client_method: ContextVar[str | None]
    method: ContextVar[str | None]
    resource_id: ContextVar[str | None]
    url: ContextVar[str | None]


log_context = LogContext(
    attempt=ContextVar('attempt', default=None),
    client_method=ContextVar('client_method', default=None),
    method=ContextVar('method', default=None),
    resource_id=ContextVar('resource_id', default=None),
    url=ContextVar('url', default=None),
)


class WithLogDetailsClient(type):
    """Metaclass that wraps public methods to inject client details into log context."""

    def __new__(cls, name: str, bases: tuple, attrs: dict) -> WithLogDetailsClient:
        """Wrap all public methods in the class with logging context injection."""
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith('_') and inspect.isfunction(attr_value):
                attrs[attr_name] = _injects_client_details_to_log_context(attr_value)

        return type.__new__(cls, name, bases, attrs)


class RedirectLogFormatter(logging.Formatter):
    """Log formatter that prepends colored logger name to messages."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log by prepending colored logger name.

        Args:
            record: The log record to format.

        Returns:
            Formatted log message with colored logger name prefix.
        """
        formatted_logger_name = f'{Fore.CYAN}[{record.name}]{Style.RESET_ALL}'
        return f'{formatted_logger_name} -> {record.msg}'


def create_redirect_logger(name: str) -> logging.Logger:
    """Create a logger for redirecting logs from another Actor.

    Args:
        name: Logger name. Use dot notation for hierarchy (e.g., "apify.xyz" creates "xyz" under "apify").

    Returns:
        Configured logger with RedirectLogFormatter.
    """
    to_logger = logging.getLogger(name)
    to_logger.propagate = False

    # Remove filters and handlers in case this logger already exists and was set up in some way.
    for handler in to_logger.handlers:
        to_logger.removeHandler(handler)
    for log_filter in to_logger.filters:
        to_logger.removeFilter(log_filter)

    handler = logging.StreamHandler()
    handler.setFormatter(RedirectLogFormatter())
    to_logger.addHandler(handler)
    to_logger.setLevel(logging.DEBUG)
    return to_logger


class _ContextInjectingFilter(logging.Filter):
    """Filter that injects current log context into all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add log context variables to the record."""
        record.client_method = log_context.client_method.get()
        record.resource_id = log_context.resource_id.get()
        record.method = log_context.method.get()
        record.url = log_context.url.get()
        record.attempt = log_context.attempt.get()
        return True


def _injects_client_details_to_log_context(fun: Callable) -> Callable:
    """Wrap a method to inject resource client details into log context before execution."""
    if inspect.iscoroutinefunction(fun):

        @functools.wraps(fun)
        async def async_wrapper(resource_client: _BaseClient, *args: Any, **kwargs: Any) -> Any:
            log_context.client_method.set(fun.__qualname__)  # ty: ignore[unresolved-attribute]
            log_context.resource_id.set(resource_client.resource_id)

            return await fun(resource_client, *args, **kwargs)

        return async_wrapper

    if inspect.isasyncgenfunction(fun):

        @functools.wraps(fun)
        async def async_generator_wrapper(resource_client: _BaseClient, *args: Any, **kwargs: Any) -> Any:
            log_context.client_method.set(fun.__qualname__)  # ty: ignore[unresolved-attribute]
            log_context.resource_id.set(resource_client.resource_id)

            async for item in fun(resource_client, *args, **kwargs):
                yield item

        return async_generator_wrapper

    @functools.wraps(fun)
    def wrapper(resource_client: _BaseClient, *args: Any, **kwargs: Any) -> Any:
        log_context.client_method.set(fun.__qualname__)  # ty: ignore[unresolved-attribute]
        log_context.resource_id.set(resource_client.resource_id)

        return fun(resource_client, *args, **kwargs)

    return wrapper


logger.addFilter(_ContextInjectingFilter())
