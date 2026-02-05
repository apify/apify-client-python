"""Unified tests for task (sync + async)."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, cast

from .conftest import get_random_resource_name, maybe_await

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator

    from apify_client import ApifyClient, ApifyClientAsync
    from apify_client._models import Actor, ListOfRuns, ListOfTasks, ListOfWebhooks, Run, Task, TaskShort

# Use a simple, fast public actor for testing
HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_task_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a task and retrieving it."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None
    actor_id = actor.id

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor_id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    assert created_task is not None
    assert created_task.id is not None
    assert created_task.name == task_name
    assert created_task.act_id == actor_id

    # Get the same task
    task_client = client.task(created_task.id)
    result = await maybe_await(task_client.get())
    retrieved_task = cast('Task', result)
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == task_name

    # Cleanup
    await maybe_await(task_client.delete())


async def test_task_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating task properties."""
    task_name = get_random_resource_name('task')
    new_name = get_random_resource_name('task-updated')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    # Update the task
    result = await maybe_await(
        task_client.update(
            name=new_name,
            timeout=timedelta(seconds=300),
        )
    )
    updated_task = cast('Task', result)
    assert updated_task is not None
    assert updated_task.name == new_name
    assert updated_task.id == created_task.id

    # Verify the update persisted
    result = await maybe_await(task_client.get())
    retrieved_task = cast('Task', result)
    assert retrieved_task is not None
    assert retrieved_task.name == new_name

    # Cleanup
    await maybe_await(task_client.delete())


async def test_task_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing tasks."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create a task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)

    # List tasks
    result = await maybe_await(client.tasks().list(limit=100))
    tasks_page = cast('ListOfTasks', result)
    assert tasks_page is not None
    assert tasks_page.items is not None

    # Verify our task is in the list
    task_ids = [t.id for t in tasks_page.items]
    assert created_task.id in task_ids

    # Cleanup
    await maybe_await(client.task(created_task.id).delete())


async def test_task_get_input(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting and updating task input."""
    task_name = get_random_resource_name('task')
    test_input = {'message': 'Hello from test'}

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task with input
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
            task_input=test_input,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    # Get input
    result = await maybe_await(task_client.get_input())
    assert result is not None
    retrieved_input = cast('dict', result)
    assert retrieved_input.get('message') == 'Hello from test'

    # Update input
    new_input = {'message': 'Updated message'}
    result = await maybe_await(task_client.update_input(task_input=new_input))
    assert result is not None
    updated_input = cast('dict', result)
    assert updated_input.get('message') == 'Updated message'

    # Cleanup
    await maybe_await(task_client.delete())


async def test_task_start(client: ApifyClient | ApifyClientAsync) -> None:
    """Test starting a task run."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    # Start the task
    result = await maybe_await(task_client.start())
    run = cast('Run', result)
    assert run is not None
    assert run.id is not None
    assert run.act_id == actor.id

    # Wait for the run to finish
    result = await maybe_await(client.run(run.id).wait_for_finish())
    finished_run = cast('Run', result)
    assert finished_run is not None
    assert finished_run.status.value == 'SUCCEEDED'

    # Cleanup
    await maybe_await(client.run(run.id).delete())
    await maybe_await(task_client.delete())


async def test_task_call(client: ApifyClient | ApifyClientAsync) -> None:
    """Test calling a task and waiting for completion."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    # Call the task (waits for finish)
    result = await maybe_await(task_client.call())
    run = cast('Run', result)
    assert run is not None
    assert run.id is not None
    assert run.status.value == 'SUCCEEDED'

    # Cleanup
    await maybe_await(client.run(run.id).delete())
    await maybe_await(task_client.delete())


async def test_task_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting a task."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    # Delete task
    await maybe_await(task_client.delete())

    # Verify it's gone
    retrieved_task = await maybe_await(task_client.get())
    assert retrieved_task is None


async def test_task_runs(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing task runs."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    try:
        # Run the task
        result = await maybe_await(task_client.call())
        run = cast('Run', result)
        assert run is not None

        # List runs for this task
        runs_client = task_client.runs()
        result = await maybe_await(runs_client.list(limit=10))
        runs_page = cast('ListOfRuns', result)
        assert runs_page is not None
        assert runs_page.items is not None
        assert len(runs_page.items) >= 1

        # Cleanup run
        await maybe_await(client.run(run.id).delete())

    finally:
        # Cleanup task
        await maybe_await(task_client.delete())


async def test_task_last_run(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting the last run of a task."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    try:
        # Run the task
        result = await maybe_await(task_client.call())
        run = cast('Run', result)
        assert run is not None

        # Get last run client
        last_run_client = task_client.last_run()
        result = await maybe_await(last_run_client.get())
        last_run = cast('Run', result)
        assert last_run is not None
        assert last_run.id == run.id

        # Cleanup run
        await maybe_await(client.run(run.id).delete())

    finally:
        # Cleanup task
        await maybe_await(task_client.delete())


async def test_task_webhooks(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing webhooks for a task."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create task
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)
    task_client = client.task(created_task.id)

    try:
        # Get webhooks client
        webhooks_client = task_client.webhooks()
        result = await maybe_await(webhooks_client.list())
        webhooks_page = cast('ListOfWebhooks', result)
        assert webhooks_page is not None
        assert webhooks_page.items is not None
        # New task should have no webhooks
        assert len(webhooks_page.items) == 0

    finally:
        # Cleanup task
        await maybe_await(task_client.delete())


async def test_task_collection_iterate(client: ApifyClient | ApifyClientAsync, *, is_async: bool) -> None:
    """Test iterating over tasks in the collection."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    result = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    actor = cast('Actor', result)
    assert actor is not None

    # Create a task so we have something to iterate over
    result = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    created_task = cast('Task', result)

    try:
        # Iterate over tasks (desc=True to get newest first, so our task appears in results)
        if is_async:
            collected_tasks = [
                task async for task in cast('AsyncIterator[TaskShort]', client.tasks().iterate(limit=10, desc=True))
            ]
        else:
            collected_tasks = list(cast('Iterator[TaskShort]', client.tasks().iterate(limit=10, desc=True)))

        # Should have at least our created task
        assert isinstance(collected_tasks, list)
        assert len(collected_tasks) >= 1
        assert len(collected_tasks) <= 10

        # Verify our task is in the list (should be first since desc=True and it's newest)
        task_ids = [t.id for t in collected_tasks]
        assert created_task.id in task_ids

        # Verify each item is a TaskShort
        for task in collected_tasks:
            assert task.id is not None
            assert task.name is not None

    finally:
        await maybe_await(client.task(created_task.id).delete())
