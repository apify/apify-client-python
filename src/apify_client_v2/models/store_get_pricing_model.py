from enum import Enum

class StoreGetPricingModel(str, Enum):
    FLAT_PRICE_PER_MONTH = "FLAT_PRICE_PER_MONTH"
    FREE = "FREE"
    PAY_PER_EVENT = "PAY_PER_EVENT"
    PRICE_PER_DATASET_ITEM = "PRICE_PER_DATASET_ITEM"

    def __str__(self) -> str:
        return str(self.value)
