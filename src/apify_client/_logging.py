from __future__ import annotations

import functools
import inspect
import json
import logging
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Callable, NamedTuple

from colorama import Fore, Style

# Conditional import only executed when type checking, otherwise we'd get circular dependency issues
if TYPE_CHECKING:
    from apify_client.clients.base.base_client import _BaseBaseClient

# Name of the logger used throughout the library
logger_name = __name__.split('.')[0]

# Logger used throughout the library
logger = logging.getLogger(logger_name)


# Context containing the details of the request and the resource client making the request
class LogContext(NamedTuple):
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


# Metaclass for resource clients which wraps all their public methods
# With injection of their details to the log context vars
class WithLogDetailsClient(type):
    def __new__(cls, name: str, bases: tuple, attrs: dict) -> WithLogDetailsClient:
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith('_') and inspect.isfunction(attr_value):
                attrs[attr_name] = _injects_client_details_to_log_context(attr_value)

        return type.__new__(cls, name, bases, attrs)


# Wraps an unbound method so that its call will inject the details
# of the resource client (which is the `self` argument of the method)
# to the log context vars
def _injects_client_details_to_log_context(fun: Callable) -> Callable:
    if inspect.iscoroutinefunction(fun):

        @functools.wraps(fun)
        async def async_wrapper(resource_client: _BaseBaseClient, *args: Any, **kwargs: Any) -> Any:
            log_context.client_method.set(fun.__qualname__)
            log_context.resource_id.set(resource_client.resource_id)

            return await fun(resource_client, *args, **kwargs)

        return async_wrapper
    elif inspect.isasyncgenfunction(fun):  # noqa: RET505

        @functools.wraps(fun)
        async def async_generator_wrapper(resource_client: _BaseBaseClient, *args: Any, **kwargs: Any) -> Any:
            log_context.client_method.set(fun.__qualname__)
            log_context.resource_id.set(resource_client.resource_id)

            async for item in fun(resource_client, *args, **kwargs):
                yield item

        return async_generator_wrapper
    else:

        @functools.wraps(fun)
        def wrapper(resource_client: _BaseBaseClient, *args: Any, **kwargs: Any) -> Any:
            log_context.client_method.set(fun.__qualname__)
            log_context.resource_id.set(resource_client.resource_id)

            return fun(resource_client, *args, **kwargs)

        return wrapper


# A filter which lets every log record through,
# but adds the current logging context to the record
class _ContextInjectingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.client_method = log_context.client_method.get()
        record.resource_id = log_context.resource_id.get()
        record.method = log_context.method.get()
        record.url = log_context.url.get()
        record.attempt = log_context.attempt.get()
        return True


logger.addFilter(_ContextInjectingFilter())


# Log formatter useful for debugging of the client
# Will print out all the extra fields added to the log record
class _DebugLogFormatter(logging.Formatter):
    empty_record = logging.LogRecord('dummy', 0, 'dummy', 0, 'dummy', None, None)

    # Gets the extra fields from the log record which are not present on an empty record
    def _get_extra_fields(self, record: logging.LogRecord) -> dict:
        extra_fields: dict = {}
        for key, value in record.__dict__.items():
            if key not in self.empty_record.__dict__:
                extra_fields[key] = value  # noqa: PERF403

        return extra_fields

    def format(self, record: logging.LogRecord) -> str:
        extra = self._get_extra_fields(record)

        log_string = super().format(record)
        if extra:
            log_string = f'{log_string} ({json.dumps(extra)})'
        return log_string


def create_redirect_logger(
    name: str,
) -> logging.Logger:
    """Create a logger for redirecting logs from another Actor.

    Args:
        name: The name of the logger. It can be used to inherit from other loggers. Example: `apify.xyz` will use logger
         named `xyz` and make it a children of `apify` logger.

    Returns:
        The created logger.
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


class RedirectLogFormatter(logging.Formatter):
    """Formater applied to default redirect logger."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log by prepending logger name to the original message.

        Args:
            record: Log record to be formated.

        Returns:
            Formated log message.
        """
        formated_logger_name = f'{Fore.CYAN}[{record.name}]{Style.RESET_ALL} '
        return f'{formated_logger_name}-> {record.msg}'
