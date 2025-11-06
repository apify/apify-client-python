from enum import Enum

class FlatPricePerMonthActorPricingInfoPricingModel(str, Enum):
    FLAT_PRICE_PER_MONTH = "FLAT_PRICE_PER_MONTH"

    def __str__(self) -> str:
        return str(self.value)
