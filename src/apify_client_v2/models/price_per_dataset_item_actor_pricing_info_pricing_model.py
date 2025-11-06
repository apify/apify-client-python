from enum import Enum

class PricePerDatasetItemActorPricingInfoPricingModel(str, Enum):
    PRICE_PER_DATASET_ITEM = "PRICE_PER_DATASET_ITEM"

    def __str__(self) -> str:
        return str(self.value)
