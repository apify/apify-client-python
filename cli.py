from apify_client import ApifyClient

client = ApifyClient(token="pt8ZArh3NoqbPKPrsAYQ3f7FL")

# print(client.build(build_id="mNaXGLRwsPFc4ENBa").get())
# print(client.build(build_id="gUPsohFDdU0f3MDvb").abort())
# print(client.build(build_id="gUPsohFDdU0f3MDvb").wait_for_finish(wait_secs=3))
# print(client.builds().list(limit=2, offset=0, desc=False))

# print(client.schedule(schedule_id="z4sCMM9RYNDzwsWE1").get())
# print(client.schedule(schedule_id="geurmolaNgNusQkKZ").update(is_enabled=False, description="This is new"))
# print(client.schedule(schedule_id="z4sCMM9RYNDzwsWE1").get())
# print(client.schedule(schedule_id="z4sCMM9RYNDzwsWE1").delete())
# print(client.schedule(schedule_id="z4sCMM9RYNDzwsWE1").get())

# print(type(client.schedule(schedule_id="DAn2cGhjfi588J3EJ").get_log()))
# print(client.schedule(schedule_id="DAn2cGhjfi588J3EJ").get_log())

# print(client.schedules().list(limit=1, offset=1))
print(client.schedules().create(cron_expression='@daily', is_enabled=False, is_exclusive=False, name='test-client-5', timezone="US/Samoa"))
# print(client.schedules().list())



# print(client.tasks().list())
# print(client.tasks().create(actor_id="4ektHDJJ92P6TZ8wV", name="task-from-python-4", memory_mb=256, timeout_secs=111, task_input={"linkSelector": 'abc'}))

# print(client.task(task_id="6JXgSWMu4mfBHvvan").get())
# print(client.task(task_id="6JXgSWMu4mfBHvvan").update(timeout_secs=321, task_input={'a': 'b'}))
# print(client.task(task_id="6JXgSWMu4mfBHvvan").get())
# print(client.task(task_id="6JXgSWMu4mfBHvvan").start(
#     task_input={'foo': 'bla'},
#     memory_mb=256,
#     timeout_secs=50,
#     wait_for_finish=10,
#     webhooks=[]
# ))

# print(client.task(task_id="6JXgSWMu4mfBHvvan").get_input())
# print(client.task(task_id="6JXgSWMu4mfBHvvan").update_input(task_input={'foo': 'bar'}))
# print(client.task(task_id="6JXgSWMu4mfBHvvan").get_input())

# print(client.task(task_id="6JXgSWMu4mfBHvvan").webhooks().list())
# print(client.task(task_id="6JXgSWMu4mfBHvvan").runs())
