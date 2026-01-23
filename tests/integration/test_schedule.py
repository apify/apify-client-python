from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import get_random_resource_name

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_schedule_create_and_get(apify_client: ApifyClient) -> None:
    """Test creating a schedule and retrieving it."""
    schedule_name = get_random_resource_name('schedule')

    # Create schedule
    created_schedule = apify_client.schedules().create(
        cron_expression='0 0 * * *',
        is_enabled=False,
        is_exclusive=False,
        name=schedule_name,
    )
    assert created_schedule is not None
    assert created_schedule.id is not None
    assert created_schedule.name == schedule_name
    assert created_schedule.cron_expression == '0 0 * * *'
    assert created_schedule.is_enabled is False
    assert created_schedule.is_exclusive is False

    # Get the same schedule
    schedule_client = apify_client.schedule(created_schedule.id)
    retrieved_schedule = schedule_client.get()
    assert retrieved_schedule is not None
    assert retrieved_schedule.id == created_schedule.id
    assert retrieved_schedule.name == schedule_name

    # Cleanup
    schedule_client.delete()


def test_schedule_update(apify_client: ApifyClient) -> None:
    """Test updating schedule properties."""
    schedule_name = get_random_resource_name('schedule')
    new_name = get_random_resource_name('schedule-updated')

    # Create schedule
    created_schedule = apify_client.schedules().create(
        cron_expression='0 0 * * *',
        is_enabled=False,
        is_exclusive=False,
        name=schedule_name,
    )
    schedule_client = apify_client.schedule(created_schedule.id)

    # Update the schedule
    updated_schedule = schedule_client.update(
        name=new_name,
        cron_expression='0 12 * * *',
        is_enabled=True,
    )
    assert updated_schedule is not None
    assert updated_schedule.name == new_name
    assert updated_schedule.cron_expression == '0 12 * * *'
    assert updated_schedule.is_enabled is True
    assert updated_schedule.id == created_schedule.id

    # Verify the update persisted
    retrieved_schedule = schedule_client.get()
    assert retrieved_schedule is not None
    assert retrieved_schedule.name == new_name
    assert retrieved_schedule.cron_expression == '0 12 * * *'

    # Cleanup
    schedule_client.delete()


def test_schedule_list(apify_client: ApifyClient) -> None:
    """Test listing schedules."""
    schedule_name_1 = get_random_resource_name('schedule')
    schedule_name_2 = get_random_resource_name('schedule')

    # Create two schedules
    created_1 = apify_client.schedules().create(
        cron_expression='0 0 * * *',
        is_enabled=False,
        is_exclusive=False,
        name=schedule_name_1,
    )
    created_2 = apify_client.schedules().create(
        cron_expression='0 6 * * *',
        is_enabled=False,
        is_exclusive=False,
        name=schedule_name_2,
    )

    # List schedules
    schedules_page = apify_client.schedules().list(limit=100)
    assert schedules_page is not None
    assert schedules_page.items is not None

    # Verify our schedules are in the list
    schedule_ids = [s.id for s in schedules_page.items]
    assert created_1.id in schedule_ids
    assert created_2.id in schedule_ids

    # Cleanup
    apify_client.schedule(created_1.id).delete()
    apify_client.schedule(created_2.id).delete()


def test_schedule_delete(apify_client: ApifyClient) -> None:
    """Test deleting a schedule."""
    schedule_name = get_random_resource_name('schedule')

    # Create schedule
    created_schedule = apify_client.schedules().create(
        cron_expression='0 0 * * *',
        is_enabled=False,
        is_exclusive=False,
        name=schedule_name,
    )
    schedule_client = apify_client.schedule(created_schedule.id)

    # Delete schedule
    schedule_client.delete()

    # Verify it's gone
    retrieved_schedule = schedule_client.get()
    assert retrieved_schedule is None
