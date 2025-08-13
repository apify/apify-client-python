from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apify_client import ApifyClient

from apify_shared.consts import ActorJobStatus

pytestmark = pytest.mark.integration


class TestRunCollectionSync:
    APIFY_HELLO_WORLD_ACTOR = 'apify/hello-world'
    created_runs: list[dict]

    def setup_runs(self, apify_client: ApifyClient) -> None:
        self.created_runs = []

        successfull_run = apify_client.actor(self.APIFY_HELLO_WORLD_ACTOR).call()
        if successfull_run is not None:
            self.created_runs.append(successfull_run)

        timed_out_run = apify_client.actor(self.APIFY_HELLO_WORLD_ACTOR).call(timeout_secs=1)
        if timed_out_run is not None:
            self.created_runs.append(timed_out_run)

    def teadown_runs(self, apify_client: ApifyClient) -> None:
        for run in self.created_runs:
            run_id = run.get('id')
            if isinstance(run_id, str):
                apify_client.run(run_id).delete()

    async def test_run_collection_list_multiple_statuses(self, apify_client: ApifyClient) -> None:
        self.setup_runs(apify_client)

        run_collection = apify_client.actor(self.APIFY_HELLO_WORLD_ACTOR).runs()

        multiple_status_runs = run_collection.list(status=[ActorJobStatus.SUCCEEDED, ActorJobStatus.TIMED_OUT])
        single_status_runs = run_collection.list(status=ActorJobStatus.SUCCEEDED)

        assert multiple_status_runs is not None
        assert single_status_runs is not None

        assert hasattr(multiple_status_runs, 'items')
        assert hasattr(single_status_runs, 'items')

        assert all(
            run.get('status') in [ActorJobStatus.SUCCEEDED, ActorJobStatus.TIMED_OUT]
            for run in multiple_status_runs.items
        )
        assert all(run.get('status') == ActorJobStatus.SUCCEEDED for run in single_status_runs.items)

        self.teadown_runs(apify_client)
