import random
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Tuple, TypeVar, cast

from ._errors import ApifyApiError

PARSE_DATE_FIELDS_MAX_DEPTH = 3
PARSE_DATE_FIELDS_KEY_SUFFIX = 'At'

NOT_FOUND_STATUS_CODE = 404
NOT_FOUND_TYPE = 'record-not-found'
NOT_FOUND_ON_S3 = '<Code>NoSuchKey</Code>'


def _to_safe_id(id: str) -> str:
    return id.replace('/', '~')


def _parse_date_fields(data: Dict) -> Dict:
    return cast(Dict, _parse_date_fields_internal(data))


def _parse_date_fields_internal(data: object, max_depth: int = PARSE_DATE_FIELDS_MAX_DEPTH) -> object:
    if max_depth < 0:
        return data

    if isinstance(data, list):
        return list(map(lambda item: _parse_date_fields_internal(item, max_depth - 1), data))

    if isinstance(data, dict):
        def parse(item: Tuple[str, object]) -> Tuple[str, object]:
            (key, value) = item
            parsed_value = value
            if key.endswith(PARSE_DATE_FIELDS_KEY_SUFFIX) and isinstance(value, str):
                try:
                    parsed_value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
                except ValueError:
                    pass
            else:
                parsed_value = _parse_date_fields_internal(value, max_depth - 1)
            return (key, parsed_value)

        return dict(map(parse, data.items()))

    return data


def _pluck_data(parsed_response: Any) -> Dict:
    if isinstance(parsed_response, dict) and 'data' in parsed_response:
        return cast(Dict, parsed_response['data'])

    raise ValueError('The "data" property is missing in the response.')


T = TypeVar('T')
BailType = Callable[[Exception], None]


def _retry_with_exp_backoff(
    func: Callable[[BailType, int], T],
    *,
    max_retries: int = 8,
    backoff_base_millis: int = 500,
    backoff_factor: float = 2,
    random_factor: float = 1,
) -> T:

    random_factor = min(max(0, random_factor), 1)
    backoff_factor = min(max(1, backoff_factor), 10)
    swallow = True

    def bail(exception: Exception) -> None:
        nonlocal swallow
        swallow = False
        raise exception

    for attempt in range(1, max_retries):
        try:
            return func(bail, attempt)
        except Exception as e:
            if not swallow:
                raise e

        random_sleep_factor = random.uniform(1, 1 + random_factor)
        backoff_base_secs = backoff_base_millis / 1000
        backoff_exp_factor = backoff_factor ** (attempt - 1)

        sleep_time_secs = random_sleep_factor * backoff_base_secs * backoff_exp_factor
        time.sleep(sleep_time_secs)

    return func(bail, max_retries)


def _catch_not_found_or_throw(exc: ApifyApiError) -> None:
    is_not_found_status = (exc.status_code == NOT_FOUND_STATUS_CODE)
    is_not_found_message = (exc.type == NOT_FOUND_TYPE) or (isinstance(exc.message, str) and NOT_FOUND_ON_S3 in exc.message)
    if not (is_not_found_status and is_not_found_message):
        raise exc

    return None
