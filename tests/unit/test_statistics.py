import pytest

from apify_client._statistics import ClientStatistics


@pytest.mark.parametrize(
    ('attempts', 'expected_errors'),
    [
        pytest.param([1], {0: 1}, id='single error'),
        pytest.param([1, 5], {0: 1, 4: 1}, id='two single errors'),
        pytest.param([5, 1], {0: 1, 4: 1}, id='two single errors reversed'),
        pytest.param([3, 5, 1], {0: 1, 2: 1, 4: 1}, id='three single errors'),
        pytest.param([1, 5, 3], {0: 1, 2: 1, 4: 1}, id='three single errors reordered'),
        pytest.param([2, 1, 2, 1, 5, 2, 1], {0: 3, 1: 3, 4: 1}, id='multiple errors per attempt'),
    ],
)
def test_add_rate_limit_error(attempts: list[int], expected_errors: list[int]) -> None:
    """Test that add_rate_limit_error correctly tracks errors for different attempt sequences."""
    stats = ClientStatistics()
    for attempt in attempts:
        stats.add_rate_limit_error(attempt)
    assert stats.rate_limit_errors == expected_errors


def test_add_rate_limit_error_invalid_attempt() -> None:
    """Test that add_rate_limit_error raises ValueError for invalid attempt."""
    stats = ClientStatistics()
    with pytest.raises(ValueError, match=r'Attempt must be greater than 0'):
        stats.add_rate_limit_error(0)


def test_statistics_initial_state() -> None:
    """Test initial state of Statistics instance."""
    stats = ClientStatistics()
    assert stats.calls == 0
    assert stats.requests == 0
    assert stats.rate_limit_errors == {}


def test_add_rate_limit_error_type_validation() -> None:
    """Test type validation in add_rate_limit_error."""
    stats = ClientStatistics()
    with pytest.raises(TypeError):
        stats.add_rate_limit_error('1')  # ty: ignore[invalid-argument-type]


def test_statistics_calls_and_requests_increment() -> None:
    """Test that calls and requests can be incremented."""
    stats = ClientStatistics()

    stats.calls += 1
    assert stats.calls == 1

    stats.requests += 1
    assert stats.requests == 1

    stats.calls += 5
    stats.requests += 10
    assert stats.calls == 6
    assert stats.requests == 11


def test_rate_limit_errors_accumulation() -> None:
    """Test that rate limit errors accumulate correctly."""
    stats = ClientStatistics()

    # Add errors to different attempts
    stats.add_rate_limit_error(1)
    stats.add_rate_limit_error(2)
    stats.add_rate_limit_error(3)

    assert stats.rate_limit_errors[0] == 1
    assert stats.rate_limit_errors[1] == 1
    assert stats.rate_limit_errors[2] == 1

    # Add more errors to same attempts
    stats.add_rate_limit_error(1)
    stats.add_rate_limit_error(1)
    stats.add_rate_limit_error(2)

    assert stats.rate_limit_errors[0] == 3
    assert stats.rate_limit_errors[1] == 2
    assert stats.rate_limit_errors[2] == 1


def test_rate_limit_errors_dict_behavior() -> None:
    """Test that rate_limit_errors behaves like a defaultdict."""
    stats = ClientStatistics()

    # Accessing non-existent key should not raise error (defaultdict behavior)
    assert stats.rate_limit_errors.get(999, 0) == 0

    # Adding to high attempt numbers should work
    stats.add_rate_limit_error(100)
    assert stats.rate_limit_errors[99] == 1


def test_statistics_independent_instances() -> None:
    """Test that different Statistics instances are independent."""
    stats1 = ClientStatistics()
    stats2 = ClientStatistics()

    stats1.calls = 10
    stats1.requests = 20
    stats1.add_rate_limit_error(1)

    assert stats2.calls == 0
    assert stats2.requests == 0
    assert stats2.rate_limit_errors == {}


def test_add_rate_limit_error_large_attempt() -> None:
    """Test add_rate_limit_error with large attempt numbers."""
    stats = ClientStatistics()

    stats.add_rate_limit_error(1000)
    assert stats.rate_limit_errors[999] == 1

    stats.add_rate_limit_error(10000)
    assert stats.rate_limit_errors[9999] == 1
