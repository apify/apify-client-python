"""Unified tests for schedule (sync + async)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import ListOfSchedules, Schedule


from .conftest import get_random_resource_name, maybe_await


async def test_schedule_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a schedule and retrieving it."""
    schedule_name = get_random_resource_name('schedule')

    # Create schedule
    result = await maybe_await(
        client.schedules().create(
            cron_expression='0 0 * * *',
            is_enabled=False,
            is_exclusive=False,
            name=schedule_name,
        )
    )
    created_schedule = cast('Schedule', result)
    assert created_schedule is not None
    assert created_schedule.id is not None
    assert created_schedule.name == schedule_name
    assert created_schedule.cron_expression == '0 0 * * *'
    assert created_schedule.is_enabled is False
    assert created_schedule.is_exclusive is False

    # Get the same schedule
    schedule_client = client.schedule(created_schedule.id)
    result = await maybe_await(schedule_client.get())
    retrieved_schedule = cast('Schedule', result)
    assert retrieved_schedule is not None
    assert retrieved_schedule.id == created_schedule.id
    assert retrieved_schedule.name == schedule_name

    # Cleanup
    await maybe_await(schedule_client.delete())


async def test_schedule_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating schedule properties."""
    schedule_name = get_random_resource_name('schedule')
    new_name = get_random_resource_name('schedule-updated')

    # Create schedule
    result = await maybe_await(
        client.schedules().create(
            cron_expression='0 0 * * *',
            is_enabled=False,
            is_exclusive=False,
            name=schedule_name,
        )
    )
    created_schedule = cast('Schedule', result)
    schedule_client = client.schedule(created_schedule.id)

    # Update the schedule
    result = await maybe_await(
        schedule_client.update(
            name=new_name,
            cron_expression='0 12 * * *',
            is_enabled=True,
        )
    )
    updated_schedule = cast('Schedule', result)
    assert updated_schedule is not None
    assert updated_schedule.name == new_name
    assert updated_schedule.cron_expression == '0 12 * * *'
    assert updated_schedule.is_enabled is True
    assert updated_schedule.id == created_schedule.id

    # Verify the update persisted
    result = await maybe_await(schedule_client.get())
    retrieved_schedule = cast('Schedule', result)
    assert retrieved_schedule is not None
    assert retrieved_schedule.name == new_name
    assert retrieved_schedule.cron_expression == '0 12 * * *'

    # Cleanup
    await maybe_await(schedule_client.delete())


async def test_schedule_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing schedules."""
    schedule_name_1 = get_random_resource_name('schedule')
    schedule_name_2 = get_random_resource_name('schedule')

    # Create two schedules
    result = await maybe_await(
        client.schedules().create(
            cron_expression='0 0 * * *',
            is_enabled=False,
            is_exclusive=False,
            name=schedule_name_1,
        )
    )
    created_1 = cast('Schedule', result)
    result = await maybe_await(
        client.schedules().create(
            cron_expression='0 6 * * *',
            is_enabled=False,
            is_exclusive=False,
            name=schedule_name_2,
        )
    )
    created_2 = cast('Schedule', result)

    # List schedules
    result = await maybe_await(client.schedules().list(limit=100))
    schedules_page = cast('ListOfSchedules', result)
    assert schedules_page is not None
    assert schedules_page.items is not None

    # Verify our schedules are in the list
    schedule_ids = [s.id for s in schedules_page.items]
    assert created_1.id in schedule_ids
    assert created_2.id in schedule_ids

    # Cleanup
    await maybe_await(client.schedule(created_1.id).delete())
    await maybe_await(client.schedule(created_2.id).delete())


async def test_schedule_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting a schedule."""
    schedule_name = get_random_resource_name('schedule')

    # Create schedule
    result = await maybe_await(
        client.schedules().create(
            cron_expression='0 0 * * *',
            is_enabled=False,
            is_exclusive=False,
            name=schedule_name,
        )
    )
    created_schedule = cast('Schedule', result)
    schedule_client = client.schedule(created_schedule.id)

    # Delete schedule
    await maybe_await(schedule_client.delete())

    # Verify it's gone
    retrieved_schedule = await maybe_await(schedule_client.get())
    assert retrieved_schedule is None


async def test_schedule_get_log(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting schedule log."""
    schedule_name = get_random_resource_name('schedule')

    # Create schedule
    result = await maybe_await(
        client.schedules().create(
            cron_expression='0 0 * * *',
            is_enabled=False,
            is_exclusive=False,
            name=schedule_name,
        )
    )
    created_schedule = cast('Schedule', result)
    schedule_client = client.schedule(created_schedule.id)

    try:
        # Get schedule log - new schedule has no log entries but the method should work
        log = await maybe_await(schedule_client.get_log())

        # Log should be None or empty list for a new disabled schedule
        assert log is None or isinstance(log, list)

    finally:
        await maybe_await(schedule_client.delete())
