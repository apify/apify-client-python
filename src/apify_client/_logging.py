import functools
import inspect
import json
import logging
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, Type, cast

# Conditional import only executed when type checking, otherwise we'd get circular dependency issues
if TYPE_CHECKING:
    from .clients.base.base_client import _BaseBaseClient

# Name of the logger used throughout the library
logger_name = __name__.split('.')[0]

# Logger used throughout the library
logger = logging.getLogger(logger_name)


# Context variables containing the current resource client running in that context
# Used during logging to inject the resource client context to the log
ctx_client_method = ContextVar[Optional[str]]('client_method', default=None)
ctx_resource_id = ContextVar[Optional[str]]('resource_id', default=None)
ctx_url = ContextVar[Optional[str]]('url', default=None)


# Metaclass for resource clients which wraps all their public methods
# With injection of their details to the log context vars
class _WithLogDetailsClient(type):
    def __new__(cls: Type[type], name: str, bases: Tuple, attrs: Dict) -> '_WithLogDetailsClient':
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith('_'):
                if inspect.isfunction(attr_value):
                    attrs[attr_name] = _injects_client_details_to_log_context(attr_value)

        return cast(_WithLogDetailsClient, type.__new__(cls, name, bases, attrs))


# Wraps an unbound method so that its call will inject the details
# of the resource client (which is the `self` argument of the method)
# to the log context vars
def _injects_client_details_to_log_context(fun: Callable) -> Callable:
    if inspect.iscoroutinefunction(fun):
        @functools.wraps(fun)
        async def async_wrapper(resource_client: '_BaseBaseClient', *args: Any, **kwargs: Any) -> Any:
            ctx_client_method.set(fun.__qualname__)
            ctx_resource_id.set(resource_client.resource_id)
            ctx_url.set(resource_client.url)

            return await fun(resource_client, *args, **kwargs)
        return async_wrapper
    elif inspect.isasyncgenfunction(fun):
        @functools.wraps(fun)
        async def async_generator_wrapper(resource_client: '_BaseBaseClient', *args: Any, **kwargs: Any) -> Any:
            ctx_client_method.set(fun.__qualname__)
            ctx_resource_id.set(resource_client.resource_id)
            ctx_url.set(resource_client.url)

            async for item in fun(resource_client, *args, **kwargs):
                yield item
        return async_generator_wrapper
    else:
        @functools.wraps(fun)
        def wrapper(resource_client: '_BaseBaseClient', *args: Any, **kwargs: Any) -> Any:
            ctx_client_method.set(fun.__qualname__)
            ctx_resource_id.set(resource_client.resource_id)
            ctx_url.set(resource_client.url)

            return fun(resource_client, *args, **kwargs)
        return wrapper


# A filter which lets every log record through,
# but adds the current logging context to the record
class _ContextInjectingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.client_method = ctx_client_method.get()
        record.resource_id = ctx_resource_id.get()
        record.url = ctx_url.get()
        return True


logger.addFilter(_ContextInjectingFilter())


# Log formatter useful for debugging of the client
# Will print out all the extra fields added to the log record
class _DebugLogFormatter(logging.Formatter):
    empty_record = logging.LogRecord('dummy', 0, 'dummy', 0, 'dummy', None, None)

    def _get_extra_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        extra_fields: Dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key not in self.empty_record.__dict__:
                extra_fields[key] = value

        return extra_fields

    def format(self, record: logging.LogRecord) -> str:
        extra = self._get_extra_fields(record)

        log_string = super().format(record)
        if extra:
            log_string = f'{log_string} ({json.dumps(extra)})'
        return log_string
