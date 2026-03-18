import logging

# Configure the Apify client logger
apify_client_logger = logging.getLogger('apify_client')
apify_client_logger.setLevel(logging.DEBUG)
apify_client_logger.addHandler(logging.StreamHandler())

# Create a custom logging formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
    '%(attempt)s - %(status_code)s - %(url)s'
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
apify_client_logger.addHandler(handler)
