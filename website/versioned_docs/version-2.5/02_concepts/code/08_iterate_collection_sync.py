from apify_client import ApifyClient

TOKEN = 'MY-APIFY-TOKEN'


def main() -> None:
    apify_client = ApifyClient(TOKEN)

    # Iterate over all Actors owned by the current user, lazily fetching
    # as many pages as needed under the hood.
    for actor in apify_client.actors().iterate(my=True):
        print(actor.id)


if __name__ == '__main__':
    main()
