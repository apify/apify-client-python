#!/usr/bin/env python3

from pprint import pprint

from apify_client import ApifyClient

client = ApifyClient('65hdEQx8DwN6haJybP92xnR2a', max_retries=4)

dataset = client.dataset('fO2WpMkkbfx4eV7KT')

key_value_store = client.key_value_store('7cfT3XDmtw0gLRcRG')

# print(client.datasets().list())

# print(client.dataset('Kbg1oHXPUBZ48tNln').get())


def pp(arg: object) -> None:
    """Pp."""
    pprint(arg)
