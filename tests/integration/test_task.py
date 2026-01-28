from __future__ import annotations

from typing import TYPE_CHECKING

from .utils import get_random_resource_name

if TYPE_CHECKING:
    from apify_client import ApifyClient

# Use a simple, fast public actor for testing
HELLO_WORLD_ACTOR = 'apify/hello-world'


def test_task_create_and_get(apify_client: ApifyClient) -> None:
    """Test creating a task and retrieving it."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None
    actor_id = actor.id

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor_id,
        name=task_name,
    )
    assert created_task is not None
    assert created_task.id is not None
    assert created_task.name == task_name
    assert created_task.act_id == actor_id

    # Get the same task
    task_client = apify_client.task(created_task.id)
    retrieved_task = task_client.get()
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == task_name

    # Cleanup
    task_client.delete()


def test_task_update(apify_client: ApifyClient) -> None:
    """Test updating task properties."""
    task_name = get_random_resource_name('task')
    new_name = get_random_resource_name('task-updated')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )
    task_client = apify_client.task(created_task.id)

    # Update the task
    updated_task = task_client.update(
        name=new_name,
        timeout_secs=300,
    )
    assert updated_task is not None
    assert updated_task.name == new_name
    assert updated_task.id == created_task.id

    # Verify the update persisted
    retrieved_task = task_client.get()
    assert retrieved_task is not None
    assert retrieved_task.name == new_name

    # Cleanup
    task_client.delete()


def test_task_list(apify_client: ApifyClient) -> None:
    """Test listing tasks."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create a task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )

    # List tasks
    tasks_page = apify_client.tasks().list(limit=100)
    assert tasks_page is not None
    assert tasks_page.items is not None

    # Verify our task is in the list
    task_ids = [t.id for t in tasks_page.items]
    assert created_task.id in task_ids

    # Cleanup
    apify_client.task(created_task.id).delete()


def test_task_get_input(apify_client: ApifyClient) -> None:
    """Test getting and updating task input."""
    task_name = get_random_resource_name('task')
    test_input = {'message': 'Hello from test'}

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task with input
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
        task_input=test_input,
    )
    task_client = apify_client.task(created_task.id)

    # Get input
    retrieved_input = task_client.get_input()
    assert retrieved_input is not None
    assert retrieved_input.get('message') == 'Hello from test'

    # Update input
    new_input = {'message': 'Updated message'}
    updated_input = task_client.update_input(task_input=new_input)
    assert updated_input is not None
    assert updated_input.get('message') == 'Updated message'

    # Cleanup
    task_client.delete()


def test_task_start(apify_client: ApifyClient) -> None:
    """Test starting a task run."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )
    task_client = apify_client.task(created_task.id)

    # Start the task
    run = task_client.start()
    assert run is not None
    assert run.id is not None
    assert run.act_id == actor.id

    # Wait for the run to finish
    finished_run = apify_client.run(run.id).wait_for_finish()
    assert finished_run is not None
    assert finished_run.status.value == 'SUCCEEDED'

    # Cleanup
    apify_client.run(run.id).delete()
    task_client.delete()


def test_task_call(apify_client: ApifyClient) -> None:
    """Test calling a task and waiting for completion."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )
    task_client = apify_client.task(created_task.id)

    # Call the task (waits for finish)
    run = task_client.call()
    assert run is not None
    assert run.id is not None
    assert run.status.value == 'SUCCEEDED'

    # Cleanup
    apify_client.run(run.id).delete()
    task_client.delete()


def test_task_delete(apify_client: ApifyClient) -> None:
    """Test deleting a task."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )
    task_client = apify_client.task(created_task.id)

    # Delete task
    task_client.delete()

    # Verify it's gone
    retrieved_task = task_client.get()
    assert retrieved_task is None


def test_task_runs(apify_client: ApifyClient) -> None:
    """Test listing task runs."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )
    task_client = apify_client.task(created_task.id)

    try:
        # Run the task
        run = task_client.call()
        assert run is not None

        # List runs for this task
        runs_client = task_client.runs()
        runs_page = runs_client.list(limit=10)
        assert runs_page is not None
        assert runs_page.items is not None
        assert len(runs_page.items) >= 1

        # Cleanup run
        apify_client.run(run.id).delete()

    finally:
        # Cleanup task
        task_client.delete()


def test_task_last_run(apify_client: ApifyClient) -> None:
    """Test getting the last run of a task."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )
    task_client = apify_client.task(created_task.id)

    try:
        # Run the task
        run = task_client.call()
        assert run is not None

        # Get last run client
        last_run_client = task_client.last_run()
        last_run = last_run_client.get()
        assert last_run is not None
        assert last_run.id == run.id

        # Cleanup run
        apify_client.run(run.id).delete()

    finally:
        # Cleanup task
        task_client.delete()


def test_task_webhooks(apify_client: ApifyClient) -> None:
    """Test listing webhooks for a task."""
    task_name = get_random_resource_name('task')

    # Get the actor ID for hello-world
    actor = apify_client.actor(HELLO_WORLD_ACTOR).get()
    assert actor is not None

    # Create task
    created_task = apify_client.tasks().create(
        actor_id=actor.id,
        name=task_name,
    )
    task_client = apify_client.task(created_task.id)

    try:
        # Get webhooks client
        webhooks_client = task_client.webhooks()
        webhooks_page = webhooks_client.list()
        assert webhooks_page is not None
        assert webhooks_page.items is not None
        # New task should have no webhooks
        assert len(webhooks_page.items) == 0

    finally:
        # Cleanup task
        task_client.delete()
