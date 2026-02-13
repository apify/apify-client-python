import asyncio

from apify_client import ApifyClientAsync
from apify_client.clients.resource_clients import TaskClientAsync

TOKEN = 'MY-APIFY-TOKEN'
HASHTAGS = ['zebra', 'lion', 'hippo']


async def run_apify_task(client: TaskClientAsync) -> dict:
    result = await client.call()
    return result or {}


async def main() -> None:
    apify_client = ApifyClientAsync(token=TOKEN)

    # Create Apify tasks
    apify_tasks = list[dict]()
    apify_tasks_client = apify_client.tasks()

    for hashtag in HASHTAGS:
        apify_task = await apify_tasks_client.create(
            name=f'hashtags-{hashtag}',
            actor_id='apify/instagram-hashtag-scraper',
            task_input={'hashtags': [hashtag], 'resultsLimit': 20},
            memory_mbytes=1024,
        )
        apify_tasks.append(apify_task)

    print('Tasks created:', apify_tasks)

    # Create Apify task clients
    apify_task_clients = list[TaskClientAsync]()

    for apify_task in apify_tasks:
        task_id = apify_task['id']
        apify_task_client = apify_client.task(task_id)
        apify_task_clients.append(apify_task_client)

    print('Task clients created:', apify_task_clients)

    # Execute Apify tasks
    run_apify_tasks = [run_apify_task(client) for client in apify_task_clients]
    task_run_results = await asyncio.gather(*run_apify_tasks)

    print('Task results:', task_run_results)


if __name__ == '__main__':
    asyncio.run(main())
