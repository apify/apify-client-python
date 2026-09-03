import logging

# Create a custom logging formatter. Reference only the properties present
# on every record. Properties attached to some records only, such as
# `status_code`, would raise an error for the records that lack them.
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
    '%(client_method)s - %(attempt)s - %(url)s'
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Configure the Apify client logger to use the custom formatter
apify_client_logger = logging.getLogger('apify_client')
apify_client_logger.setLevel(logging.DEBUG)
apify_client_logger.addHandler(handler)
