"""Unified tests for task (sync + async)."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from ._utils import get_random_resource_name, maybe_await
from apify_client._models import Actor, ListOfRuns, ListOfTasks, ListOfWebhooks, Run, Task

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync

# Use a simple, fast public actor for testing
HELLO_WORLD_ACTOR = 'apify/hello-world'


async def test_task_create_and_get(client: ApifyClient | ApifyClientAsync) -> None:
    """Test creating a task and retrieving it."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)
    actor_id = actor.id

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor_id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        assert created_task.id is not None
        assert created_task.name == task_name
        assert created_task.act_id == actor_id

        # Get the same task
        retrieved_task = await maybe_await(task_client.get())
        assert isinstance(retrieved_task, Task)
        assert retrieved_task.id == created_task.id
        assert retrieved_task.name == task_name
    finally:
        await maybe_await(task_client.delete())


async def test_task_update(client: ApifyClient | ApifyClientAsync) -> None:
    """Test updating task properties."""
    task_name = get_random_resource_name('task')
    new_name = get_random_resource_name('task-updated')

    # Get the actor ID for hello-world
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        # Update the task
        updated_task = await maybe_await(
            task_client.update(
                name=new_name,
                timeout=timedelta(seconds=300),
            )
        )
        assert isinstance(updated_task, Task)
        assert updated_task.name == new_name
        assert updated_task.id == created_task.id

        # Verify the update persisted
        retrieved_task = await maybe_await(task_client.get())
        assert isinstance(retrieved_task, Task)
        assert retrieved_task.name == new_name
    finally:
        await maybe_await(task_client.delete())


async def test_task_list(client: ApifyClient | ApifyClientAsync) -> None:
    """Test listing tasks."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create a task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)

    try:
        # List tasks
        tasks_page = await maybe_await(client.tasks().list(limit=100))
        assert isinstance(tasks_page, ListOfTasks)
        assert tasks_page.items is not None

        # Verify our task is in the list
        task_ids = [t.id for t in tasks_page.items]
        assert created_task.id in task_ids
    finally:
        await maybe_await(client.task(created_task.id).delete())


async def test_task_get_input(client: ApifyClient | ApifyClientAsync) -> None:
    """Test getting and updating task input."""
    task_name = get_random_resource_name('task')
    test_input = {'message': 'Hello from test'}

    # Get the actor ID for hello-world
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task with input
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
            task_input=test_input,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        # Get input
        retrieved_input = await maybe_await(task_client.get_input())
        assert isinstance(retrieved_input, dict)
        assert retrieved_input.get('message') == 'Hello from test'

        # Update input
        new_input = {'message': 'Updated message'}
        updated_input = await maybe_await(task_client.update_input(task_input=new_input))
        assert isinstance(updated_input, dict)
        assert updated_input.get('message') == 'Updated message'
    finally:
        await maybe_await(task_client.delete())


async def test_task_start(client: ApifyClient | ApifyClientAsync) -> None:
    """Test starting a task run."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        # Start the task
        run = await maybe_await(task_client.start())
        assert isinstance(run, Run)
        assert run.id is not None
        assert run.act_id == actor.id

        # Wait for the run to finish
        finished_run = await maybe_await(client.run(run.id).wait_for_finish())
        assert isinstance(finished_run, Run)
        assert finished_run.status == 'SUCCEEDED'

        # Cleanup run
        await maybe_await(client.run(run.id).delete())
    finally:
        await maybe_await(task_client.delete())


async def test_task_call(client: ApifyClient | ApifyClientAsync) -> None:
    """Test calling a task and waiting for completion."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        # Call the task (waits for finish)
        run = await maybe_await(task_client.call())
        assert isinstance(run, Run)
        assert run.id is not None
        assert run.status == 'SUCCEEDED'

        # Cleanup run
        await maybe_await(client.run(run.id).delete())
    finally:
        await maybe_await(task_client.delete())


async def test_task_delete(client: ApifyClient | ApifyClientAsync) -> None:
    """Test deleting a task."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
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
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        # Run the task
        run = await maybe_await(task_client.call())
        assert isinstance(run, Run)

        # List runs for this task
        runs_client = task_client.runs()
        runs_page = await maybe_await(runs_client.list(limit=10))
        assert isinstance(runs_page, ListOfRuns)
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
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        # Run the task
        run = await maybe_await(task_client.call())
        assert isinstance(run, Run)

        # Get last run client
        last_run_client = task_client.last_run()
        last_run = await maybe_await(last_run_client.get())
        assert isinstance(last_run, Run)
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
    actor = await maybe_await(client.actor(HELLO_WORLD_ACTOR).get())
    assert isinstance(actor, Actor)

    # Create task
    created_task = await maybe_await(
        client.tasks().create(
            actor_id=actor.id,
            name=task_name,
        )
    )
    assert isinstance(created_task, Task)
    task_client = client.task(created_task.id)

    try:
        # Get webhooks client
        webhooks_client = task_client.webhooks()
        webhooks_page = await maybe_await(webhooks_client.list())
        assert isinstance(webhooks_page, ListOfWebhooks)
        assert webhooks_page.items is not None
        # New task should have no webhooks
        assert len(webhooks_page.items) == 0

    finally:
        # Cleanup task
        await maybe_await(task_client.delete())
